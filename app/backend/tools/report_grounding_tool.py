import re
from typing import Any

from azure.search.documents.aio import SearchClient

from rtmt import ToolResult, ToolResultDirection

grounding_tool_schema = {
    "type": "function",
    "name": "report_grounding",
    "description": "Report use of a source from the knowledge base as part of an answer (effectively, cite the source). Sources " + \
                   "appear in square brackets before each knowledge base passage. Always use this tool to cite sources when responding " + \
                   "with information from the knowledge base.",
    "parameters": {
        "type": "object",
        "properties": {
            "sources": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of source names from last statement actually used, do not include the ones not used to formulate a response"
            }
        },
        "required": ["sources"],
        "additionalProperties": False
    }
}

KEY_PATTERN = re.compile(r'^[a-zA-Z0-9_=\-]+$')

# TODO: move from sending all chunks used for grounding eagerly to only sending links to 
# the original content in storage, it'll be more efficient overall
async def report_grounding_tool(search_client: SearchClient, identifier_field: str, title_field: str, content_field: str, args: Any) -> None:
    sources = [s for s in args["sources"] if KEY_PATTERN.match(s)]
    list = " OR ".join(sources)
    print(f"Grounding source: {list}")
    # Use search instead of filter to align with how detailt integrated vectorization indexes
    # are generated, where chunk_id is searchable with a keyword tokenizer, not filterable 
    search_results = await search_client.search(search_text=list, 
                                                search_fields=[identifier_field], 
                                                select=[identifier_field, title_field, content_field], 
                                                top=len(sources), 
                                                query_type="full")
    
    # If your index has a key field that's filterable but not searchable and with the keyword analyzer, you can 
    # use a filter instead (and you can remove the regex check above, just ensure you escape single quotes)
    # search_results = await search_client.search(filter=f"search.in(chunk_id, '{list}')", select=["chunk_id", "title", "chunk"])

    docs = []
    async for r in search_results:
        docs.append({"chunk_id": r[identifier_field], "title": r[title_field], "chunk": r[content_field]})
    return ToolResult({"sources": docs}, ToolResultDirection.TO_CLIENT)