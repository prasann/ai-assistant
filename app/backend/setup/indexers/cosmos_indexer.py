import json
import logging
import os
import subprocess

from azure.identity import AzureDeveloperCliCredential
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    FieldMapping,
    SearchableField,
    SimpleField,
    SearchFieldDataType,
    SearchIndex,
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataSourceType,
)

from dotenv import load_dotenv
from rich.logging import RichHandler


def load_azd_env():
    """Get path to current azd env file and load file using python-dotenv"""
    result = subprocess.run("azd env list -o json", shell=True, capture_output=True, text=True)
    print(result)
    if result.returncode != 0:
        raise Exception("Error loading azd env")
    env_json = json.loads(result.stdout)
    env_file_path = None
    for entry in env_json:
        if entry["IsDefault"]:
            env_file_path = entry["DotEnvPath"]
    if not env_file_path:
        raise Exception("No default azd env file found")
    logger.info(f"Loading azd env from {env_file_path}")
    load_dotenv(env_file_path, override=True)


def setup_index(azure_credential, index_name, azure_search_endpoint, azure_cosmos_connection_string, azure_cosmos_container):
    index_client = SearchIndexClient(azure_search_endpoint, azure_credential)
    indexer_client = SearchIndexerClient(azure_search_endpoint, azure_credential)
    data_source_name = "cosmos-notes"
    data_source_connections = indexer_client.get_data_source_connections()
    if data_source_name in [ds.name for ds in data_source_connections]:
        logger.info(f"Data source connection {data_source_name} already exists, not re-creating")
    else:
        logger.info(f"Creating data source connection: {data_source_name} with conn {azure_cosmos_connection_string}")
        indexer_client.create_data_source_connection(
            data_source_connection=SearchIndexerDataSourceConnection(
                name=data_source_name, 
                type=SearchIndexerDataSourceType.COSMOS_DB,
                connection_string=azure_cosmos_connection_string,
                container=SearchIndexerDataContainer(name=azure_cosmos_container)))

    index_names = [index.name for index in index_client.list_indexes()]
    index_name = "cosmos-notes-index"
    if index_name in index_names:
        logger.info(f"Index {index_name} already exists, not re-creating")
    else:
        logger.info(f"Creating index: {index_name}")
        index_client.create_index(
            SearchIndex(
                name=index_name,
                fields=[
                    SearchableField(name="id", key=True, analyzer_name="keyword", sortable=True),
                    SearchableField(name="content"),
                    SimpleField(name="timestamp", type=SearchFieldDataType.String, filterable=True),
                ]
            )
        )

    indexers = indexer_client.get_indexers()
    indexer_name = "cosmos-indexer"
    if indexer_name in [indexer.name for indexer in indexers]:
        logger.info(f"Indexer {index_name} already exists, not re-creating")
    else:
        indexer_client.create_indexer(
            indexer=SearchIndexer(
                name=indexer_name,
                data_source_name=data_source_name,
                target_index_name=index_name,
                field_mappings=[
                        FieldMapping(source_field_name="content", target_field_name="content"),
                        FieldMapping(source_field_name="timestamp", target_field_name="timestamp"),
                    ]
            )
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)])
    logger = logging.getLogger("ai-assistant")
    logger.setLevel(logging.INFO)

    load_azd_env()

    logger.info("Checking if we need to set up Azure AI Search index...")
    if os.environ.get("AZURE_SEARCH_REUSE_EXISTING") == "true":
        logger.info("Since an existing Azure AI Search index is being used, no changes will be made to the index.")
        exit()
    else:
        logger.info("Setting up Azure AI Search index and integrated vectorization...")

    AZURE_SEARCH_INDEX = os.environ["AZURE_SEARCH_INDEX"]
    AZURE_COSMOS_CONNECTION_STRING = os.environ["AZURE_COSMOS_CONNECTION_STRING"]
    AZURE_COSMOS_CONTAINER = os.environ["AZURE_COSMOS_CONTAINER"]
    AZURE_SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]

    azure_credential = AzureDeveloperCliCredential(tenant_id=os.environ["AZURE_TENANT_ID"], process_timeout=60)

    setup_index(azure_credential,
        index_name=AZURE_SEARCH_INDEX, 
        azure_search_endpoint=AZURE_SEARCH_ENDPOINT,
        azure_cosmos_connection_string=AZURE_COSMOS_CONNECTION_STRING,
        azure_cosmos_container=AZURE_COSMOS_CONTAINER)