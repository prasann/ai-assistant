from typing import Any
from azure.search.documents.aio import SearchClient

from rtmt import ToolResult, ToolResultDirection

search_notes_tool_schema = {
    "type": "function",
    "name": "search_notes",
    "description": "Search the notes storage, to check for the information that were recorded as notes previously " + \
                   "you should translate to and from English if needed. " + \
                   "there is a line with '-----' at the end of each result.",
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

async def search_notes_tool(
    search_client: SearchClient, 
    semantic_configuration: str,
    identifier_field: str,
    content_field: str,
    args: Any) -> ToolResult:
    print(f"Searching for '{args['query']}' in the knowledge base.")
    # Semantic query using Azure AI Search
    search_results = await search_client.search(
        search_text=args['query'], 
        query_type="semantic",
        semantic_configuration_name=semantic_configuration,
        top=5,
        select=", ".join([identifier_field, content_field])
    )
    result = ""
    async for r in search_results:
        result += f"[{r[identifier_field]}]: {r[content_field]}\n-----\n"
    print("****** result-start ******")
    print(result)
    print("****** result-end ******")
    return ToolResult(result, ToolResultDirection.TO_SERVER)
