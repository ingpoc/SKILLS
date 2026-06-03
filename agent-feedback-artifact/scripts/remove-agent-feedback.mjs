#!/usr/bin/env node
import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const targetArg = process.argv[2];
if (!targetArg) {
  console.error("Usage: scripts/remove-agent-feedback.mjs <artifact.html>");
  process.exit(2);
}

const target = resolve(process.cwd(), targetArg);
const start = "<!-- AGENT_FEEDBACK_WIDGET_START -->";
const end = "<!-- AGENT_FEEDBACK_WIDGET_END -->";
const original = await readFile(target, "utf8");
const blockPattern = new RegExp(`\\n?${escapeRegExp(start)}[\\s\\S]*?${escapeRegExp(end)}\\n?`, "m");

let next = original.replace(blockPattern, "");
next = next.replace(/\n?<meta name="agent-feedback-version" content="[^"]+">\n?/i, "\n");

if (next === original) {
  console.log(`Feedback widget not present: ${target}`);
  process.exit(0);
}

await writeFile(target, next);
console.log(`Removed feedback widget: ${target}`);

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
