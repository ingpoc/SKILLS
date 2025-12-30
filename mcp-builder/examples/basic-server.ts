/**
 * Basic MCP server example with TypeScript SDK
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Constants
const CHARACTER_LIMIT = 25000;
const API_BASE_URL = "https://api.example.com";

// Initialize server
const server = new Server(
  {
    name: "example-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Input validation schema
const SearchInputSchema = z.object({
  query: z.string().min(1).max(500),
  limit: z.number().int().min(1).max(100).default(10),
  format: z.enum(["json", "markdown"]).default("json"),
}).strict();

// Register tool
server.registerTool({
  name: "search_items",
  description: "Search for items in the database",
  inputSchema: SearchInputSchema,
  annotations: {
    readOnlyHint: true,
    destructiveHint: false,
    idempotentHint: true,
    openWorldHint: true,
  },
}, async ({ query, limit = 10, format = "json" }): Promise<string> => {
  try {
    // Validate input
    const validated = SearchInputSchema.parse({ query, limit, format });

    // API call logic here
    const results = await fetchFromApi(validated.query, validated.limit);

    // Format response
    if (validated.format === "markdown") {
      return formatAsMarkdown(results);
    }
    return formatAsJson(results);

  } catch (error) {
    if (error instanceof z.ZodError) {
      return `Error: Invalid input - ${error.message}`;
    }
    return `Error: Search failed - ${error.message}`;
  }
});

// Server startup
async function main(): Promise<void> {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
