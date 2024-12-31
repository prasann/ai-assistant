from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizableTextQuery

from rtmt import ToolResult, ToolResultDirection

search_tool_schema = {
    "type": "function",
    "name": "search",
    "description": "Search the knowledge base. The knowledge base is in English, translate to and from English if " + \
                   "needed. Results are formatted as a source name first in square brackets, followed by the text " + \
                   "content, and a line with '-----' at the end of each result.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }
}

async def search_tool(
    search_client: SearchClient, 
    semantic_configuration: str,
    identifier_field: str,
    content_field: str,
    embedding_field: str,
    use_vector_query: bool,
    args: Any) -> ToolResult:
    print(f"Searching for '{args['query']}' in the knowledge base.")
    # Hybrid + Reranking query using Azure AI Search
    vector_queries = []
    if use_vector_query:
        vector_queries.append(VectorizableTextQuery(text=args['query'], k_nearest_neighbors=50, fields=embedding_field))
    search_results = await search_client.search(
        search_text=args['query'], 
        query_type="semantic",
        semantic_configuration_name=semantic_configuration,
        top=5,
        vector_queries=vector_queries,
        select=", ".join([identifier_field, content_field])
    )
    result = ""
    async for r in search_results:
        result += f"[{r[identifier_field]}]: {r[content_field]}\n-----\n"
    return ToolResult(result, ToolResultDirection.TO_SERVER)