"""
Searchable Tools Example - Python MCP Server

Demonstrates tool organization for large servers (20+ tools) optimized for tool search
and lazy loading. Shows naming conventions, rich descriptions, and searchable parameters.

Key patterns demonstrated:
1. Hierarchical naming: service_domain_action_resource
2. Rich descriptions with semantic keywords
3. Descriptive parameter names
4. Common synonyms in descriptions
5. Tool organization with clear naming
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("slack_mcp")

# ============================================================================
# MESSAGES DOMAIN - Tools for sending, listing, and managing messages
# ============================================================================

@mcp.tool(
    name="slack_messages_send",
    description=(
        "Send a message to a Slack channel or direct message (DM). "
        "Supports posting, replying, threading, and broadcasting. "
        "Use for notifications, alerts, team communication, or chatbot responses."
    )
)
async def slack_messages_send(
    channel_name_or_id: str = Field(
        description="Channel name (#general) or channel ID (C123456), or user ID for direct message"
    ),
    message_text: str = Field(
        description="Message content (supports markdown formatting, emoji, mentions)"
    ),
    thread_timestamp: Optional[str] = Field(
        default=None,
        description="Reply to a specific message thread using parent message timestamp"
    )
) -> str:
    """
    Send a message to Slack channel or user.

    Returns:
        JSON with message timestamp, channel ID, and delivery confirmation
    """
    pass


@mcp.tool(
    name="slack_messages_list",
    description=(
        "List recent messages from a Slack channel or conversation. "
        "Retrieve history, search discussions, or find past communications. "
        "Supports filtering by date range and pagination for large channels."
    )
)
async def slack_messages_list(
    channel_id: str = Field(
        description="Channel ID to retrieve messages from (e.g., C123456)"
    ),
    limit: int = Field(
        default=20,
        description="Maximum number of messages to return (1-100)",
        ge=1,
        le=100
    ),
    oldest_timestamp: Optional[str] = Field(
        default=None,
        description="Only messages after this timestamp (Unix epoch or ISO format)"
    )
) -> str:
    """
    List messages from a Slack channel.

    Returns:
        JSON array of messages with text, user, timestamp, and thread information
    """
    pass


@mcp.tool(
    name="slack_messages_delete",
    description=(
        "Delete a message from a Slack channel or conversation. "
        "Remove, erase, or retract messages by timestamp. "
        "Requires appropriate permissions and message ownership."
    )
)
async def slack_messages_delete(
    channel_id: str = Field(
        description="Channel ID containing the message (e.g., C123456)"
    ),
    message_timestamp: str = Field(
        description="Timestamp of the message to delete (from message history)"
    )
) -> str:
    """
    Delete a message from Slack.

    Returns:
        Confirmation of deletion with channel and timestamp
    """
    pass


# ============================================================================
# CHANNELS DOMAIN - Tools for creating, listing, and managing channels
# ============================================================================

@mcp.tool(
    name="slack_channels_create",
    description=(
        "Create a new Slack channel (workspace, room, group). "
        "Set up public or private channels for teams, projects, or topics. "
        "Configure channel name, description, and initial members."
    )
)
async def slack_channels_create(
    channel_name: str = Field(
        description="Channel name (lowercase, hyphens allowed, e.g., 'project-alpha')",
        pattern=r"^[a-z0-9\-]+$"
    ),
    is_private: bool = Field(
        default=False,
        description="True for private channel (invite-only), False for public"
    ),
    description: Optional[str] = Field(
        default=None,
        description="Channel purpose and description for members"
    )
) -> str:
    """
    Create a new Slack channel.

    Returns:
        JSON with new channel ID, name, and creation details
    """
    pass


@mcp.tool(
    name="slack_channels_list",
    description=(
        "List all Slack channels in the workspace (rooms, groups, conversations). "
        "Find, browse, or discover channels by name or type. "
        "Supports filtering by public/private and active/archived status."
    )
)
async def slack_channels_list(
    include_private: bool = Field(
        default=False,
        description="Include private channels user has access to"
    ),
    exclude_archived: bool = Field(
        default=True,
        description="Exclude archived (inactive) channels from results"
    ),
    limit: int = Field(
        default=50,
        description="Maximum number of channels to return (1-200)",
        ge=1,
        le=200
    )
) -> str:
    """
    List Slack channels in workspace.

    Returns:
        JSON array of channels with ID, name, member count, and topic
    """
    pass


@mcp.tool(
    name="slack_channels_archive",
    description=(
        "Archive a Slack channel to mark it as inactive or closed. "
        "Preserve history while removing from active channel list. "
        "Channel can be unarchived later if needed."
    )
)
async def slack_channels_archive(
    channel_id: str = Field(
        description="Channel ID to archive (e.g., C123456)"
    )
) -> str:
    """
    Archive a Slack channel.

    Returns:
        Confirmation with channel ID and archive timestamp
    """
    pass


# ============================================================================
# USERS DOMAIN - Tools for finding, listing, and managing users
# ============================================================================

@mcp.tool(
    name="slack_users_search",
    description=(
        "Search for Slack users by name, email, or display name. "
        "Find, lookup, or discover team members and collaborators. "
        "Returns user profiles with contact information and status."
    )
)
async def slack_users_search(
    search_query: str = Field(
        description="Search term: user's name, email, or display name (partial matches supported)"
    ),
    limit: int = Field(
        default=10,
        description="Maximum number of users to return (1-100)",
        ge=1,
        le=100
    )
) -> str:
    """
    Search for Slack users.

    Returns:
        JSON array of user profiles with ID, name, email, status, and avatar
    """
    pass


@mcp.tool(
    name="slack_users_info",
    description=(
        "Get detailed information about a specific Slack user or profile. "
        "Retrieve contact details, timezone, status, and team information. "
        "Use for user lookup or profile verification."
    )
)
async def slack_users_info(
    user_id: str = Field(
        description="User ID to retrieve information for (e.g., U123456)"
    )
) -> str:
    """
    Get detailed user information.

    Returns:
        JSON with complete user profile including name, email, timezone, and preferences
    """
    pass


@mcp.tool(
    name="slack_users_presence",
    description=(
        "Check if a Slack user is active, online, away, or offline. "
        "Get real-time availability status for communication planning. "
        "Useful for determining best time to send messages."
    )
)
async def slack_users_presence(
    user_id: str = Field(
        description="User ID to check presence status (e.g., U123456)"
    )
) -> str:
    """
    Check user online/active status.

    Returns:
        JSON with presence status (active/away) and last activity timestamp
    """
    pass


# ============================================================================
# FILES DOMAIN - Tools for uploading, listing, and managing files
# ============================================================================

@mcp.tool(
    name="slack_files_upload",
    description=(
        "Upload a file, document, image, or attachment to Slack. "
        "Share files with channels, users, or conversations. "
        "Supports images, PDFs, documents, code files, and archives."
    )
)
async def slack_files_upload(
    file_path: str = Field(
        description="Local file path to upload"
    ),
    channels: Optional[List[str]] = Field(
        default=None,
        description="List of channel IDs to share file with (e.g., ['C123456', 'C789012'])"
    ),
    title: Optional[str] = Field(
        default=None,
        description="File title or display name in Slack"
    ),
    initial_comment: Optional[str] = Field(
        default=None,
        description="Message to post with the file upload"
    )
) -> str:
    """
    Upload file to Slack.

    Returns:
        JSON with file ID, URL, and sharing confirmation
    """
    pass


@mcp.tool(
    name="slack_files_list",
    description=(
        "List files shared in Slack workspace, channel, or by user. "
        "Browse, find, or search shared documents and attachments. "
        "Supports filtering by type, date, and channel."
    )
)
async def slack_files_list(
    channel_id: Optional[str] = Field(
        default=None,
        description="Filter files by channel ID (omit for workspace-wide search)"
    ),
    user_id: Optional[str] = Field(
        default=None,
        description="Filter files uploaded by specific user"
    ),
    limit: int = Field(
        default=20,
        description="Maximum number of files to return (1-100)",
        ge=1,
        le=100
    )
) -> str:
    """
    List files in Slack workspace.

    Returns:
        JSON array of files with name, type, size, URL, and upload info
    """
    pass


# ============================================================================
# REACTIONS DOMAIN - Tools for adding and managing emoji reactions
# ============================================================================

@mcp.tool(
    name="slack_reactions_add",
    description=(
        "Add an emoji reaction to a Slack message (like, vote, respond). "
        "Express sentiment with emoji (👍, ❤️, 🎉, etc.). "
        "Use for quick feedback, acknowledgment, or voting."
    )
)
async def slack_reactions_add(
    channel_id: str = Field(
        description="Channel ID containing the message (e.g., C123456)"
    ),
    message_timestamp: str = Field(
        description="Timestamp of message to react to"
    ),
    emoji_name: str = Field(
        description="Emoji name without colons (e.g., 'thumbsup', 'heart', 'tada')"
    )
) -> str:
    """
    Add emoji reaction to message.

    Returns:
        Confirmation with channel, message timestamp, and emoji added
    """
    pass


# ============================================================================
# SEARCHABILITY BEST PRACTICES DEMONSTRATED
# ============================================================================
#
# 1. NAMING PATTERN: service_domain_action_resource
#    - slack_messages_send, slack_channels_list, slack_users_search
#    - Consistent prefixes enable category discovery
#
# 2. RICH DESCRIPTIONS:
#    - Start with clear purpose
#    - Include semantic keywords (send, post, broadcast, notify)
#    - Add common synonyms (find, search, lookup, discover)
#    - Explain use cases (notifications, team communication)
#
# 3. DESCRIPTIVE PARAMETERS:
#    - channel_name_or_id instead of "target"
#    - message_text instead of "text"
#    - search_query instead of "q"
#    - thread_timestamp instead of "ts"
#
# 4. PARAMETER DESCRIPTIONS:
#    - Include examples: "e.g., C123456"
#    - Explain formats: "Unix epoch or ISO format"
#    - Clarify purpose: "for direct message" not just "user ID"
#
# 5. TOOL ORGANIZATION:
#    - Clear naming: service_domain_action pattern
#    - Logical grouping: messages, channels, users, files, reactions
#    - Enables domain-specific searches
#
# 6. SEARCH SCENARIOS:
#    - "send slack message" → finds slack_messages_send
#    - "slack channels" → finds all channel tools
#    - "search users" → finds slack_users_search
#    - "upload file slack" → finds slack_files_upload
#    - "slack notification" → finds slack_messages_send
#
# ============================================================================

if __name__ == "__main__":
    mcp.run()
