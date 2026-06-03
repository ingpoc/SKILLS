#!/usr/bin/env node
import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { classifyWorkItem, routeSummary } from "./agent-feedback-routing.mjs";

const args = process.argv.slice(2);
const claim = args.includes("--claim");
const queuePath = resolve(process.cwd(), "data", "feedback-queue.json");
const queue = JSON.parse(await readFile(queuePath, "utf8"));
const item = queue.find((entry) => entry.status === "queued");

if (!item) {
  console.log(JSON.stringify({ item: null }, null, 2));
  process.exit(0);
}

const route = classifyWorkItem(item);
const routed = routeSummary(item, route);

item.workerRoute = route.route;
item.contextTier = route.contextTier;
item.workerLifecycle = route.workerLifecycle;
item.routeReason = route.reason;
item.recommendedModel = route.model;
item.recommendedReasoningEffort = route.reasoningEffort;
item.workerStatus = claim ? "processing" : "routed";
if (claim) item.status = "processing";
item.updatedAt = new Date().toISOString();

if (claim) {
  await writeFile(queuePath, `${JSON.stringify(queue, null, 2)}\n`);
}

console.log(JSON.stringify({
  item: {
    id: item.id,
    markerId: item.markerId,
    status: item.status,
    workerStatus: item.workerStatus,
    artifactPath: item.artifactPath || item.payload?.artifactPath,
    artifactTitle: item.artifactTitle || item.payload?.artifactTitle,
    artifactVersion: item.artifactVersion || item.payload?.artifactVersion,
    selector: item.selector,
    visibleText: item.visibleText,
    latestUserMessage: item.latestUserMessage,
    threadSummary: item.threadSummary || "",
    ...routed
  }
}, null, 2));
