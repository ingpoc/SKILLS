"""Actionable error handling patterns for MCP tools"""

from mcp.server import Server
from typing import Optional

mcp = Server("error-demo")

@mcp.tool()
async def get_user_data(user_id: str, include_details: bool = False) -> str:
    """
    Fetch user data with educational error messages.

    Args:
        user_id: User identifier (numeric string)
        include_details: Include extended profile information

    Returns:
        User data in requested format
    """
    try:
        # Validate input format
        if not user_id.isdigit():
            return (
                "Error: user_id must be numeric. "
                "Example: use user_id='12345' instead of user_id='user-12345'. "
                "Try searching by name first with search_users() to find the correct ID."
            )

        # Fetch data
        user = await fetch_user(int(user_id))

        if user is None:
            return (
                f"Error: User {user_id} not found. "
                "Try using search_users() to find users by name or email first."
            )

        # Check permissions
        if include_details and not has_permission(user_id):
            return (
                f"Error: Permission denied for detailed view of user {user_id}. "
                "Try using include_details=False for basic information, "
                "or use get_public_profile() for publicly available data."
            )

        return format_user_data(user, include_details)

    except RateLimitError as e:
        return (
            f"Error: Rate limit exceeded ({e.retry_after}s remaining). "
            "Consider using batch_get_users() to fetch multiple users efficiently, "
            "or add a delay between requests."
        )
    except TimeoutError:
        return (
            "Error: Request timed out. "
            "Try reducing the scope: use include_details=False to fetch less data, "
            "or check system_status() to see if there are ongoing issues."
        )
    except Exception as e:
        return f"Error: Unexpected failure - {str(e)}. Please try again."


@mcp.tool()
async def list_projects(
    filter_type: Optional[str] = None,
    limit: int = 50
) -> str:
    """
    List projects with smart pagination and filtering guidance.

    Args:
        filter_type: Filter by type ('active', 'archived', 'all')
        limit: Max results (1-100)

    Returns:
        Project list with pagination info
    """
    try:
        if limit > 100:
            return (
                f"Error: limit={limit} exceeds maximum of 100. "
                "For large datasets, use pagination: call list_projects(limit=100), "
                "then use the 'next_page_token' in subsequent calls. "
                "Or try filter_type='active' to reduce results."
            )

        projects = await fetch_projects(filter_type, limit)

        if len(projects) == 0 and filter_type:
            return (
                f"No projects found with filter_type='{filter_type}'. "
                f"Try filter_type='all' to see all projects, "
                f"or remove the filter to search more broadly."
            )

        return format_projects(projects)

    except Exception as e:
        return f"Error: Failed to list projects - {str(e)}"
