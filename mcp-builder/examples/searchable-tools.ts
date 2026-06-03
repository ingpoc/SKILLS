/**
 * Searchable Tools Example - TypeScript MCP Server
 *
 * Demonstrates tool organization for large servers (20+ tools) optimized for tool search
 * and lazy loading. Shows naming conventions, rich descriptions, and searchable parameters.
 *
 * Key patterns demonstrated:
 * 1. Hierarchical naming: service_domain_action_resource
 * 2. Rich descriptions with semantic keywords
 * 3. Descriptive Zod schema parameter names
 * 4. Common synonyms in descriptions
 * 5. Tool categorization with annotations
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Initialize MCP server
const server = new McpServer({
  name: "slack-mcp-server",
  version: "1.0.0"
});

// ============================================================================
// MESSAGES DOMAIN - Tools for sending, listing, and managing messages
// ============================================================================

server.registerTool(
  "slack_messages_send",
  {
    title: "Send Slack Message",
    description:
      "Send a message to a Slack channel or direct message (DM). " +
      "Supports posting, replying, threading, and broadcasting. " +
      "Use for notifications, alerts, team communication, or chatbot responses.",
    inputSchema: z.object({
      channel_name_or_id: z.string().describe(
        "Channel name (#general) or channel ID (C123456), or user ID for direct message"
      ),
      message_text: z.string().describe(
        "Message content (supports markdown formatting, emoji, mentions)"
      ),
      thread_timestamp: z.string().optional().describe(
        "Reply to a specific message thread using parent message timestamp"
      )
    }).strict(),
    annotations: {
      readOnlyHint: false,
      destructiveHint: false,
      category: "messages",
      tags: ["communication", "notify", "post", "broadcast"]
    }
  },
  async (params) => {
    /**
     * Send a message to Slack channel or user.
     * Returns: JSON with message timestamp, channel ID, and delivery confirmation
     */
    return {
      content: [{ type: "text", text: JSON.stringify({ success: true }) }]
    };
  }
);

server.registerTool(
  "slack_messages_list",
  {
    title: "List Slack Messages",
    description:
      "List recent messages from a Slack channel or conversation. " +
      "Retrieve history, search discussions, or find past communications. " +
      "Supports filtering by date range and pagination for large channels.",
    inputSchema: z.object({
      channel_id: z.string().describe(
        "Channel ID to retrieve messages from (e.g., C123456)"
      ),
      limit: z.number().int().min(1).max(100).default(20).describe(
        "Maximum number of messages to return (1-100)"
      ),
      oldest_timestamp: z.string().optional().describe(
        "Only messages after this timestamp (Unix epoch or ISO format)"
      )
    }).strict(),
    annotations: {
      readOnlyHint: true,
      category: "messages",
      tags: ["history", "search", "retrieve", "find"]
    }
  },
  async (params) => {
    /**
     * List messages from a Slack channel.
     * Returns: JSON array of messages with text, user, timestamp, and thread information
     */
    return {
      content: [{ type: "text", text: JSON.stringify([]) }]
    };
  }
);

server.registerTool(
  "slack_messages_delete",
  {
    title: "Delete Slack Message",
    description:
      "Delete a message from a Slack channel or conversation. " +
      "Remove, erase, or retract messages by timestamp. " +
      "Requires appropriate permissions and message ownership.",
    inputSchema: z.object({
      channel_id: z.string().describe(
        "Channel ID containing the message (e.g., C123456)"
      ),
      message_timestamp: z.string().describe(
        "Timestamp of the message to delete (from message history)"
      )
    }).strict(),
    annotations: {
      readOnlyHint: false,
      destructiveHint: true,
      category: "messages",
      tags: ["remove", "erase", "retract"]
    }
  },
  async (params) => {
    /**
     * Delete a message from Slack.
     * Returns: Confirmation of deletion with channel and timestamp
     */
    return {
      content: [{ type: "text", text: JSON.stringify({ deleted: true }) }]
    };
  }
);

// ============================================================================
// CHANNELS DOMAIN - Tools for creating, listing, and managing channels
// ============================================================================

server.registerTool(
  "slack_channels_create",
  {
    title: "Create Slack Channel",
    description:
      "Create a new Slack channel (workspace, room, group). " +
      "Set up public or private channels for teams, projects, or topics. " +
      "Configure channel name, description, and initial members.",
    inputSchema: z.object({
      channel_name: z.string().regex(/^[a-z0-9\-]+$/).describe(
        "Channel name (lowercase, hyphens allowed, e.g., 'project-alpha')"
      ),
      is_private: z.boolean().default(false).describe(
        "True for private channel (invite-only), False for public"
      ),
      description: z.string().optional().describe(
        "Channel purpose and description for members"
      )
    }).strict(),
    annotations: {
      readOnlyHint: false,
      destructiveHint: false,
      category: "channels",
      tags: ["setup", "new", "initialize", "workspace"]
    }
  },
  async (params) => {
    /**
     * Create a new Slack channel.
     * Returns: JSON with new channel ID, name, and creation details
     */
    return {
      content: [{ type: "text", text: JSON.stringify({ channel: {} }) }]
    };
  }
);

server.registerTool(
  "slack_channels_list",
  {
    title: "List Slack Channels",
    description:
      "List all Slack channels in the workspace (rooms, groups, conversations). " +
      "Find, browse, or discover channels by name or type. " +
      "Supports filtering by public/private and active/archived status.",
    inputSchema: z.object({
      include_private: z.boolean().default(false).describe(
        "Include private channels user has access to"
      ),
      exclude_archived: z.boolean().default(true).describe(
        "Exclude archived (inactive) channels from results"
      ),
      limit: z.number().int().min(1).max(200).default(50).describe(
        "Maximum number of channels to return (1-200)"
      )
    }).strict(),
    annotations: {
      readOnlyHint: true,
      category: "channels",
      tags: ["find", "browse", "discover", "search"]
    }
  },
  async (params) => {
    /**
     * List Slack channels in workspace.
     * Returns: JSON array of channels with ID, name, member count, and topic
     */
    return {
      content: [{ type: "text", text: JSON.stringify({ channels: [] }) }]
    };
  }
);

server.registerTool(
  "slack_channels_archive",
  {
    title: "Archive Slack Channel",
    description:
      "Archive a Slack channel to mark it as inactive or closed. " +
      "Preserve history while removing from active channel list. " +
      "Channel can be unarchived later if needed.",
    inputSchema: z.object({
      channel_id: z.string().describe(
        "Channel ID to archive (e.g., C123456)"
      )
    }).strict(),
    annotations: {
      readOnlyHint: false,
      destructiveHint: false,
      category: "channels",
      tags: ["close", "deactivate", "preserve"]
    }
  },
  async (params) => {
    /**
     * Archive a Slack channel.
     * Returns: Confirmation with channel ID and archive timestamp
     */
    return {
      content: [{ type: "text", text: JSON.stringify({ archived: true }) }]
    };
  }
);

// ============================================================================
// USERS DOMAIN - Tools for finding, listing, and managing users
// ============================================================================

server.registerTool(
  "slack_users_search",
  {
    title: "Search Slack Users",
    description:
      "Search for Slack users by name, email, or display name. " +
      "Find, lookup, or discover team members and collaborators. " +
      "Returns user profiles with contact information and status.",
    inputSchema: z.object({
      search_query: z.string().describe(
        "Search term: user's name, email, or display name (partial matches supported)"
      ),
      limit: z.number().int().min(1).max(100).default(10).describe(
        "Maximum number of users to return (1-100)"
      )
    }).strict(),
    annotations: {
      readOnlyHint: true,
      category: "users",
      tags: ["find", "lookup", "discover", "directory"]
    }
  },
  async (params) => {
    /**
     * Search for Slack users.
     * Returns: JSON array of user profiles with ID, name, email, status, and avatar
     */
    return {
      content: [{ type: "text", text: JSON.stringify({ users: [] }) }]
    };
  }
);

server.registerTool(
  "slack_users_info",
  {
    title: "Get Slack User Info",
    description:
      "Get detailed information about a specific Slack user or profile. " +
      "Retrieve contact details, timezone, status, and team information. " +
      "Use for user lookup or profile verification.",
    inputSchema: z.object({
      user_id: z.string().describe(
        "User ID to retrieve information for (e.g., U123456)"
      )
    }).strict(),
    annotations: {
      readOnlyHint: true,
      category: "users",
      tags: ["profile", "details", "lookup", "contact"]
    }
  },
  async (params) => {
    /**
     * Get detailed user information.
     * Returns: JSON with complete user profile including name, email, timezone, and preferences
     */
    return {
      content: [{ type: "text", text: JSON.stringify({ user: {} }) }]
    };
  }
);

server.registerTool(
  "slack_users_presence",
  {
    title: "Check Slack User Presence",
    description:
      "Check if a Slack user is active, online, away, or offline. " +
      "Get real-time availability status for communication planning. " +
      "Useful for determining best time to send messages.",
    inputSchema: z.object({
      user_id: z.string().describe(
        "User ID to check presence status (e.g., U123456)"
      )
    }).strict(),
    annotations: {
      readOnlyHint: true,
      category: "users",
      tags: ["status", "availability", "online", "active"]
    }
  },
  async (params) => {
    /**
     * Check user online/active status.
     * Returns: JSON with presence status (active/away) and last activity timestamp
     */
    return {
      content: [{ type: "text", text: JSON.stringify({ presence: "active" }) }]
    };
  }
);

// ============================================================================
// FILES DOMAIN - Tools for uploading, listing, and managing files
// ============================================================================

server.registerTool(
  "slack_files_upload",
  {
    title: "Upload Slack File",
    description:
      "Upload a file, document, image, or attachment to Slack. " +
      "Share files with channels, users, or conversations. " +
      "Supports images, PDFs, documents, code files, and archives.",
    inputSchema: z.object({
      file_path: z.string().describe(
        "Local file path to upload"
      ),
      channels: z.array(z.string()).optional().describe(
        "List of channel IDs to share file with (e.g., ['C123456', 'C789012'])"
      ),
      title: z.string().optional().describe(
        "File title or display name in Slack"
      ),
      initial_comment: z.string().optional().describe(
        "Message to post with the file upload"
      )
    }).strict(),
    annotations: {
      readOnlyHint: false,
      category: "files",
      tags: ["attach", "share", "send", "document"]
    }
  },
  async (params) => {
    /**
     * Upload file to Slack.
     * Returns: JSON with file ID, URL, and sharing confirmation
     */
    return {
      content: [{ type: "text", text: JSON.stringify({ file: {} }) }]
    };
  }
);

server.registerTool(
  "slack_files_list",
  {
    title: "List Slack Files",
    description:
      "List files shared in Slack workspace, channel, or by user. " +
      "Browse, find, or search shared documents and attachments. " +
      "Supports filtering by type, date, and channel.",
    inputSchema: z.object({
      channel_id: z.string().optional().describe(
        "Filter files by channel ID (omit for workspace-wide search)"
      ),
      user_id: z.string().optional().describe(
        "Filter files uploaded by specific user"
      ),
      limit: z.number().int().min(1).max(100).default(20).describe(
        "Maximum number of files to return (1-100)"
      )
    }).strict(),
    annotations: {
      readOnlyHint: true,
      category: "files",
      tags: ["browse", "find", "search", "shared"]
    }
  },
  async (params) => {
    /**
     * List files in Slack workspace.
     * Returns: JSON array of files with name, type, size, URL, and upload info
     */
    return {
      content: [{ type: "text", text: JSON.stringify({ files: [] }) }]
    };
  }
);

// ============================================================================
// REACTIONS DOMAIN - Tools for adding and managing emoji reactions
// ============================================================================

server.registerTool(
  "slack_reactions_add",
  {
    title: "Add Slack Reaction",
    description:
      "Add an emoji reaction to a Slack message (like, vote, respond). " +
      "Express sentiment with emoji (👍, ❤️, 🎉, etc.). " +
      "Use for quick feedback, acknowledgment, or voting.",
    inputSchema: z.object({
      channel_id: z.string().describe(
        "Channel ID containing the message (e.g., C123456)"
      ),
      message_timestamp: z.string().describe(
        "Timestamp of message to react to"
      ),
      emoji_name: z.string().describe(
        "Emoji name without colons (e.g., 'thumbsup', 'heart', 'tada')"
      )
    }).strict(),
    annotations: {
      readOnlyHint: false,
      category: "reactions",
      tags: ["emoji", "like", "vote", "respond"]
    }
  },
  async (params) => {
    /**
     * Add emoji reaction to message.
     * Returns: Confirmation with channel, message timestamp, and emoji added
     */
    return {
      content: [{ type: "text", text: JSON.stringify({ ok: true }) }]
    };
  }
);

// ============================================================================
// SEARCHABILITY BEST PRACTICES DEMONSTRATED
// ============================================================================
//
// 1. NAMING PATTERN: service_domain_action_resource
//    - slack_messages_send, slack_channels_list, slack_users_search
//    - Consistent prefixes enable category discovery
//
// 2. RICH DESCRIPTIONS:
//    - Start with clear purpose
//    - Include semantic keywords (send, post, broadcast, notify)
//    - Add common synonyms (find, search, lookup, discover)
//    - Explain use cases (notifications, team communication)
//
// 3. DESCRIPTIVE ZOD SCHEMAS:
//    - channel_name_or_id instead of "target"
//    - message_text instead of "text"
//    - search_query instead of "q"
//    - thread_timestamp instead of "ts"
//
// 4. SCHEMA DESCRIPTIONS:
//    - Include examples: "e.g., C123456"
//    - Explain formats: "Unix epoch or ISO format"
//    - Clarify purpose: "for direct message" not just "user ID"
//
// 5. TOOL CATEGORIZATION:
//    - Custom annotations: category, tags
//    - Logical grouping: messages, channels, users, files, reactions
//    - Enables domain-specific searches
//
// 6. SEARCH SCENARIOS:
//    - "send slack message" → finds slack_messages_send
//    - "slack channels" → finds all channel tools
//    - "search users" → finds slack_users_search
//    - "upload file slack" → finds slack_files_upload
//    - "slack notification" → finds slack_messages_send
//
// ============================================================================

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
