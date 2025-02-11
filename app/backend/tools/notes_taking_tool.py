from typing import Any
import uuid
from azure.cosmos.aio import CosmosClient
from rtmt import ToolResult, ToolResultDirection
from datetime import datetime, timezone

note_taking_tool_schema = {
    "type": "function",
    "name": "add_notes",
    "description": "Adds a note into the database for future retrieval.",
    "parameters": {
        "type": "object",
        "properties": {
            "note": {
                "type": "string",
                "description": "Summary of the notes that needs to be recorded."
            }
        },
        "required": ["note"],
        "additionalProperties": False
    }
}

async def add_note_tool(
    cosmos_client: CosmosClient,
    database_name: str,
    container_name: str,
    args: Any) -> ToolResult:
    note_content = args["note"]
    print(f"Adding note: '{note_content}' to CosmosDB.")
    
    database = cosmos_client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    
    note_entry = {
        "id": str(uuid.uuid4()), 
        "content": note_content,
        "timestamp": datetime.now(timezone.utc).isoformat() 
    }
    
    await container.upsert_item(note_entry)
    return ToolResult("Note added successfully.", ToolResultDirection.TO_SERVER)