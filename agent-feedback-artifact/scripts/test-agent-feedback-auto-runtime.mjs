#!/usr/bin/env node
import { createServer } from "node:http";
import { readFile, writeFile, mkdir, appendFile } from "node:fs/promises";
import { dirname, normalize, resolve, join } from "node:path";

const root = resolve(process.argv[2] || process.cwd());
const port = Number(process.argv[3] || 4190);
const apiBase = process.env.AGENT_FEEDBACK_API_BASE || "http://127.0.0.1:4177";
const logPath = resolve(root, "data", "auto-runtime-events.jsonl");
const fileLocks = new Map();

await mkdir(dirname(logPath), { recursive: true });
await writeFile(logPath, "");

const server = createServer(async (req, res) => {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const bodyText = Buffer.concat(chunks).toString("utf8");
  const event = JSON.parse(bodyText || "{}");
  await log("received", event);
  for (const item of event.items || []) {
    processItem(item).catch((error) => log("error", { id: item.id, error: error.message }));
  }
  res.writeHead(202, { "content-type": "application/json" });
  res.end(JSON.stringify({ ok: true, accepted: event.items?.length || 0 }));
});

server.listen(port, "127.0.0.1", () => {
  console.log(`Auto runtime: http://127.0.0.1:${port}/hook`);
  console.log(`Log: ${logPath}`);
});

process.on("SIGTERM", () => server.close(() => process.exit(0)));

async function processItem(item) {
  await log("processing", compact(item));
  await updateStatus(item.id, {
    status: "processing",
    workerStatus: item.route || "processing",
    agentMessage: `Processing marker ${item.markerId}`
  });

  await delay(350 + Math.floor(Math.random() * 450));
  const result = await applyRequestedChange(item);
  await updateStatus(item.id, {
    status: "done",
    workerStatus: "done",
    agentMessage: result.agentMessage,
    threadSummary: result.threadSummary
  });
  await log("done", { ...compact(item), result });
}

async function applyRequestedChange(item) {
  const filePath = resolveArtifactPath(item.artifactPath);
  return withFileLock(filePath, () => applyRequestedChangeLocked(item, filePath));
}

async function applyRequestedChangeLocked(item, filePath) {
  let html = await readFile(filePath, "utf8");
  const message = `${item.latestUserMessage || ""} ${item.visibleText || ""}`.toLowerCase();
  let changed = false;
  let agentMessage = "Done: processed this marker.";
  let threadSummary = `Marker ${item.markerId}: processed "${item.latestUserMessage || item.visibleText || ""}".`;

  if (message.includes("uptime") && (message.includes("bigger") || message.includes("stronger"))) {
    if (!html.includes('[data-test-target="uptime"] strong { font-size: 30px; font-weight: 750; }')) {
      html = html.replace("</style>", '    [data-test-target="uptime"] strong { font-size: 30px; font-weight: 750; }\n  </style>');
      changed = true;
    }
    agentMessage = "Done: made the uptime value larger and stronger.";
    threadSummary = `Marker ${item.markerId}: uptime typography increased to 30px and weight 750.`;
  } else if (message.includes("latency") && message.includes("240ms")) {
    const next = html.replace(/(<div class="metric" data-test-target="latency"><span>P95 latency<\/span><strong>)([^<]+)(<\/strong><\/div>)/, "$1240ms$3");
    changed = next !== html;
    html = next;
    agentMessage = "Done: updated P95 latency to 240ms.";
    threadSummary = `Marker ${item.markerId}: latency corrected to 240ms.`;
  } else if (message.includes("next actions") || message.includes("rename action queue")) {
    const next = html.replace(/<h2>Action Queue <span class="pill">Live<\/span><\/h2>/, '<h2>Next Actions <span class="pill">Live</span></h2>');
    changed = next !== html;
    html = next;
    agentMessage = "Done: renamed Action Queue to Next Actions.";
    threadSummary = `Marker ${item.markerId}: action queue heading renamed to Next Actions.`;
  } else {
    agentMessage = "Done: no deterministic test change matched this marker.";
  }

  if (changed) await writeFile(filePath, html);
  return { changed, agentMessage, threadSummary };
}

function withFileLock(filePath, fn) {
  const prior = fileLocks.get(filePath) || Promise.resolve();
  const next = prior.then(fn, fn);
  fileLocks.set(filePath, next.catch(() => {}));
  return next;
}

function resolveArtifactPath(artifactPath) {
  const relative = String(artifactPath || "").replace(/^\/+/, "");
  const candidate = normalize(join(root, relative));
  if (!candidate.startsWith(root)) throw new Error(`artifact_outside_root: ${artifactPath}`);
  return candidate;
}

async function updateStatus(id, patch) {
  const response = await fetch(`${apiBase}/api/agent/status/${encodeURIComponent(id)}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(patch)
  });
  if (!response.ok) throw new Error(`status_update_failed:${response.status}`);
}

async function log(type, payload) {
  await appendFile(logPath, `${JSON.stringify({ at: new Date().toISOString(), type, payload })}\n`);
}

function compact(item) {
  return {
    id: item.id,
    markerId: item.markerId,
    route: item.route,
    contextTier: item.contextTier,
    artifactPath: item.artifactPath,
    latestUserMessage: item.latestUserMessage
  };
}

function delay(ms) {
  return new Promise((resolveDelay) => setTimeout(resolveDelay, ms));
}
