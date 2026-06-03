"""Basic MCP server example with Python SDK"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from pydantic import BaseModel, Field

# Constants
CHARACTER_LIMIT = 25000
API_BASE_URL = "https://api.example.com"

# Initialize server
mcp = Server("example-server")

# Input validation model
class SearchInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Max results (1-100)")
    format: str = Field("json", pattern="^(json|markdown)$", description="Response format")

@mcp.tool()
async def search_items(query: str, limit: int = 10, format: str = "json") -> str:
    """
    Search for items in the database.

    Args:
        query: Search query string
        limit: Maximum number of results (1-100)
        format: Response format ('json' or 'markdown')

    Returns:
        Formatted search results (JSON or Markdown)

    Example:
        search_items(query="machine learning", limit=5, format="markdown")
    """
    try:
        # Validate input
        validated = SearchInput(query=query, limit=limit, format=format)

        # API call logic here
        results = await fetch_from_api(validated.query, validated.limit)

        # Format response
        if validated.format == "markdown":
            return format_as_markdown(results)
        return format_as_json(results)

    except ValueError as e:
        return f"Error: Invalid input - {str(e)}"
    except Exception as e:
        return f"Error: Search failed - {str(e)}"

# Server startup
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(read_stream, write_stream, mcp.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
