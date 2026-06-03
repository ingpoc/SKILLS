#!/usr/bin/env node
import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const targetArg = process.argv[2];
if (!targetArg) {
  console.error("Usage: scripts/add-agent-feedback.mjs <artifact.html>");
  process.exit(2);
}

const root = resolve(import.meta.dirname, "..");
const target = resolve(process.cwd(), targetArg);
const overlayPath = resolve(root, "references", "overlay.html");
const start = "<!-- AGENT_FEEDBACK_WIDGET_START -->";
const end = "<!-- AGENT_FEEDBACK_WIDGET_END -->";

const [original, overlay] = await Promise.all([
  readFile(target, "utf8"),
  readFile(overlayPath, "utf8")
]);

if (original.includes(start) || original.includes(end)) {
  console.log(`Feedback widget already present: ${target}`);
  process.exit(0);
}

const versionMeta = `<meta name="agent-feedback-version" content="${new Date().toISOString()}">`;
let next = original;

if (!next.includes("agent-feedback-version")) {
  next = next.replace(/<\/head>/i, `${versionMeta}\n</head>`);
}

if (!/<\/body>/i.test(next)) {
  console.error(`No </body> tag found in ${target}`);
  process.exit(1);
}

next = next.replace(/<\/body>/i, `${overlay}\n</body>`);
await writeFile(target, next);
console.log(`Added feedback widget: ${target}`);
