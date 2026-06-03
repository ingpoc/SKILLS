#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

const id = process.argv[2];
if (!id) {
  console.error("Usage: scripts/agent-feedback-details.mjs <work-id>");
  process.exit(2);
}

const queuePath = resolve(process.cwd(), "data", "feedback-queue.json");
const queue = JSON.parse(await readFile(queuePath, "utf8"));
const item = queue.find((entry) => entry.id === id);

if (!item) {
  console.error(`Feedback batch not found: ${id}`);
  process.exit(1);
}

console.log(JSON.stringify(item, null, 2));
