"""MCP tool with context management and workflow consolidation"""

from mcp.server import Server
from pydantic import BaseModel, Field
from typing import Optional

mcp = Server("workflow-server")

class CreateEventInput(BaseModel):
    """Consolidated workflow: check availability + create event"""
    title: str = Field(..., min_length=1, max_length=200)
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date in YYYY-MM-DD format")
    duration_hours: int = Field(..., ge=1, le=8, description="Duration in hours (1-8)")
    attendees: list[str] = Field(default_factory=list, max_items=50)
    response_format: str = Field("concise", pattern="^(concise|detailed)$")

@mcp.tool(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True
)
async def schedule_event(
    title: str,
    date: str,
    duration_hours: int,
    attendees: Optional[list[str]] = None,
    response_format: str = "concise"
) -> str:
    """
    Check availability and schedule event (consolidated workflow).

    This tool combines availability checking and event creation into a single
    workflow, reducing the number of tool calls needed.

    Args:
        title: Event title
        date: Event date (YYYY-MM-DD)
        duration_hours: Duration in hours (1-8)
        attendees: List of attendee email addresses
        response_format: 'concise' returns summary, 'detailed' returns full info

    Returns:
        Event confirmation with conflict warnings if any

    Error Handling:
        - If date conflicts exist, returns conflicts and suggests alternatives
        - If attendees unavailable, lists who has conflicts
        - Use response_format='concise' to reduce token usage

    Example:
        schedule_event(
            title="Team Sync",
            date="2025-01-15",
            duration_hours=1,
            attendees=["alice@example.com", "bob@example.com"],
            response_format="concise"
        )
    """
    try:
        validated = CreateEventInput(
            title=title,
            date=date,
            duration_hours=duration_hours,
            attendees=attendees or [],
            response_format=response_format
        )

        # Step 1: Check availability for all attendees
        conflicts = await check_availability(validated.date, validated.attendees)

        if conflicts:
            alternatives = await find_alternative_slots(validated.date, validated.duration_hours)
            return format_conflict_response(conflicts, alternatives, validated.response_format)

        # Step 2: Create event if no conflicts
        event = await create_calendar_event(validated)

        # Step 3: Format response based on verbosity
        if validated.response_format == "concise":
            return f"Event '{validated.title}' scheduled on {validated.date}"
        else:
            return format_detailed_event(event)

    except ValueError as e:
        return f"Error: {str(e)}. Please check input format and try again."
    except Exception as e:
        return f"Error: Failed to schedule event - {str(e)}"
