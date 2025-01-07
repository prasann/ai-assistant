import os
from tools.personal_info_tool import personal_info_tool, personal_info_tool_schema
from tools.notes_taking_tool import add_note_tool, note_taking_tool_schema
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents.aio import SearchClient
from azure.cosmos import CosmosClient

from rtmt import RTMiddleTier, Tool

def attach_rag_tools(rtmt: RTMiddleTier,
    credentials: AzureKeyCredential | DefaultAzureCredential,
    search_endpoint: str, search_index: str,
    semantic_configuration: str,
    identifier_field: str,
    content_field: str,
    embedding_field: str,
    title_field: str,
    use_vector_query: bool
    ) -> None:
    if not isinstance(credentials, AzureKeyCredential):
        credentials.get_token("https://search.azure.com/.default") # warm this up before we start getting requests
    
    cosmos_host = os.environ.get('COSMOS_HOST', 'https://aiasmv4r2nfwlx5w2.documents.azure.com:443/')
    # cosmos_master_key = os.environ.get('COSMOS_MASTER_KEY')
    cosmos_database_name = os.environ.get('COSMOS_DATABASE')
    cosmos_container_name = os.environ.get('COSMOS_CONTAINER')
    
    search_client = SearchClient(search_endpoint, search_index, credentials, user_agent="RTMiddleTier")
    cosmos_store_client = CosmosClient(url=cosmos_host, credential= credentials)
    
    rtmt.tools["personal_info"] = Tool(schema=personal_info_tool_schema, target=lambda args: personal_info_tool(search_client, semantic_configuration, identifier_field, content_field, embedding_field, use_vector_query, args))
    rtmt.tools["add_notes"] = Tool(schema=note_taking_tool_schema, target=lambda args: add_note_tool(cosmos_store_client, cosmos_database_name, cosmos_container_name, args))