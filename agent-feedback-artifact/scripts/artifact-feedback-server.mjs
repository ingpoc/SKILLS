#!/usr/bin/env node
import { createServer } from "node:http";
import { request as httpRequest } from "node:http";
import { request as httpsRequest } from "node:https";
import { readFile, writeFile, mkdir, rename } from "node:fs/promises";
import { createReadStream, existsSync } from "node:fs";
import { createHmac } from "node:crypto";
import { extname, join, normalize, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { classifyWorkItem, routeSummary, summarizeThread } from "./agent-feedback-routing.mjs";

const root = resolve(process.argv[2] || process.cwd());
const port = Number(process.env.PORT || process.argv[3] || 4177);
const dataDir = resolve(root, "data");
const queuePath = resolve(dataDir, "feedback-queue.json");
const webhookUrl = process.env.AGENT_FEEDBACK_WEBHOOK_URL || "";
const webhookSecret = process.env.AGENT_FEEDBACK_WEBHOOK_SECRET || "";
const webhookTimeoutMs = Number(process.env.AGENT_FEEDBACK_WEBHOOK_TIMEOUT_MS || 2500);
let queueLock = Promise.resolve();

await mkdir(dataDir, { recursive: true });
if (!existsSync(queuePath)) {
  await writeJson(queuePath, []);
}

const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url || "/", `http://${req.headers.host || "localhost"}`);

    if (req.method === "POST" && url.pathname === "/api/feedback") {
      const body = await readBody(req);
      const payload = JSON.parse(body || "{}");
      const comments = Array.isArray(payload.comments) ? payload.comments : [];
      if (!comments.length) return json(res, 400, { error: "comments_required" });
      const now = new Date().toISOString();
      let items = [];
      await updateQueue((queue) => {
        items = comments.map((comment) => createWorkItem(payload, comment, now, queue));
        items.forEach(attachRouteMetadata);
        queue.push(...items);
      });
      const dispatch = await notifyAgentWebhook(items, payload);
      return json(res, 202, {
        id: items[0].id,
        status: "queued",
        dispatch,
        items: items.map(summarizeItem)
      });
    }

    if (req.method === "GET" && url.pathname === "/api/feedback/status") {
      const artifact = url.searchParams.get("artifact");
      const queue = await readQueue();
      const matching = artifact
        ? queue.filter((item) => artifactPathFor(item) === artifact)
        : queue;
      return json(res, 200, { latest: matching.at(-1) || null, items: matching, count: matching.length });
    }

    if (req.method === "DELETE" && url.pathname === "/api/feedback/message") {
      const batchId = url.searchParams.get("batch");
      const messageId = url.searchParams.get("message");
      if (!batchId || !messageId) return json(res, 400, { error: "batch_and_message_required" });
      const result = await updateQueue((queue) => {
        const item = queue.find((entry) => entry.id === batchId);
        if (!item) return { code: 404, body: { error: "not_found" } };
        if (item.status !== "queued") return { code: 409, body: { error: "already_processing", status: item.status } };

        let removed = false;
        if (item.marker && Array.isArray(item.marker.messages)) {
          const before = item.marker.messages.length;
          item.marker.messages = item.marker.messages.filter((message) => message.id !== messageId);
          removed = item.marker.messages.length !== before;
          item.marker.text = item.marker.messages.map((message) => message.text).filter(Boolean).join("\n\n");
          item.latestUserMessage = latestUserMessage(item.marker);
        }
        for (const comment of item.payload?.comments || []) {
          if (Array.isArray(comment.messages)) {
            const before = comment.messages.length;
            comment.messages = comment.messages.filter((message) => message.id !== messageId);
            removed = removed || comment.messages.length !== before;
            comment.text = comment.messages.map((message) => message.text).filter(Boolean).join("\n\n");
          } else if (comment.id === messageId) {
            comment._deleted = true;
            removed = true;
          }
        }
        item.payload.comments = (item.payload?.comments || [])
          .filter((comment) => !comment._deleted)
          .filter((comment) => !Array.isArray(comment.messages) || comment.messages.length);
        if (!removed) return { code: 404, body: { error: "message_not_found" } };
        if (!markerFor(item)?.messages?.length && !item.payload?.comments?.length) item.status = "canceled";
        item.workerStatus = item.status;
        item.updatedAt = new Date().toISOString();
        return { code: 200, body: { id: item.id, status: item.status, removed: messageId } };
      });
      return json(res, result.code, result.body);
    }

    if (req.method === "GET" && url.pathname === "/api/agent/next") {
      const queue = await readQueue();
      const next = queue.find((item) => item.status === "queued") || null;
      return json(res, 200, { item: next ? summarizeItem(next) : null });
    }

    if (req.method === "POST" && url.pathname === "/api/agent/dispatch") {
      const claim = url.searchParams.get("claim") === "1" || url.searchParams.get("claim") === "true";
      const result = await updateQueue((queue) => {
        const item = queue.find((entry) => entry.status === "queued");
        if (!item) return { code: 200, body: { item: null } };
        attachRouteMetadata(item);
        item.workerStatus = claim ? "processing" : "routed";
        if (claim) item.status = "processing";
        item.updatedAt = new Date().toISOString();
        return { code: 200, body: { item: summarizeItem(item) } };
      });
      return json(res, result.code, result.body);
    }

    if (req.method === "GET" && url.pathname.startsWith("/api/agent/details/")) {
      const id = decodeURIComponent(url.pathname.replace("/api/agent/details/", ""));
      const queue = await readQueue();
      const item = queue.find((entry) => entry.id === id);
      if (!item) return json(res, 404, { error: "not_found" });
      return json(res, 200, { item });
    }

    if (req.method === "POST" && url.pathname.startsWith("/api/agent/status/")) {
      const id = decodeURIComponent(url.pathname.replace("/api/agent/status/", ""));
      const body = await readBody(req);
      const patch = JSON.parse(body || "{}");
      const result = await updateQueue((queue) => {
        const item = queue.find((entry) => entry.id === id);
        if (!item) return { code: 404, body: { error: "not_found" } };
        item.status = String(patch.status || item.status);
        item.workerStatus = String(patch.workerStatus || patch.status || item.workerStatus || item.status);
        item.agentMessage = String(patch.agentMessage || item.agentMessage || "");
        if (patch.threadSummary) item.threadSummary = String(patch.threadSummary);
        if (["done", "blocked", "canceled"].includes(item.status)) {
          item.lastProcessedAt = new Date().toISOString();
          if (!item.threadSummary) item.threadSummary = summarizeThread(item, item.agentMessage);
        }
        item.updatedAt = new Date().toISOString();
        return { code: 200, body: { id: item.id, status: item.status } };
      });
      return json(res, result.code, result.body);
    }

    if (req.method !== "GET" && req.method !== "HEAD") {
      return text(res, 405, "Method not allowed");
    }

    const filePath = resolveStaticPath(url.pathname);
    if (!filePath || !existsSync(filePath)) {
      return text(res, 404, "Not found");
    }

    res.writeHead(200, {
      "content-type": mimeType(filePath),
      "cache-control": "no-store"
    });
    if (req.method === "HEAD") return res.end();
    createReadStream(filePath).pipe(res);
  } catch (error) {
    console.error(error);
    text(res, 500, "Internal server error");
  }
});

server.listen(port, () => {
  console.log(`Artifact feedback server: http://localhost:${port}/`);
  console.log(`Serving: ${root}`);
  console.log(`Queue: ${queuePath}`);
  console.log(`Webhook: ${webhookUrl ? webhookUrl : "not configured"}`);
});

function resolveStaticPath(pathname) {
  const decoded = decodeURIComponent(pathname);
  const requested = decoded === "/" ? "/financial-status-tax-overview.annotated.html" : decoded;
  const candidate = normalize(join(root, requested));
  if (!candidate.startsWith(root)) return null;
  return candidate;
}

async function readQueue() {
  return JSON.parse(await readFile(queuePath, "utf8"));
}

async function writeJson(path, value) {
  const tmp = `${path}.${Date.now()}.${Math.random().toString(36).slice(2)}.tmp`;
  await writeFile(tmp, `${JSON.stringify(value, null, 2)}\n`);
  await rename(tmp, path);
}

function updateQueue(mutator) {
  const next = queueLock.then(async () => {
    const queue = await readQueue();
    const result = await mutator(queue);
    await writeJson(queuePath, queue);
    return result;
  });
  queueLock = next.catch(() => {});
  return next;
}

async function readBody(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  return Buffer.concat(chunks).toString("utf8");
}

function json(res, status, value) {
  res.writeHead(status, {
    "content-type": "application/json",
    "cache-control": "no-store"
  });
  res.end(JSON.stringify(value));
}

function text(res, status, value) {
  res.writeHead(status, {
    "content-type": "text/plain; charset=utf-8",
    "cache-control": "no-store"
  });
  res.end(value);
}

function mimeType(filePath) {
  const ext = extname(filePath).toLowerCase();
  if (ext === ".html") return "text/html; charset=utf-8";
  if (ext === ".js") return "text/javascript; charset=utf-8";
  if (ext === ".css") return "text/css; charset=utf-8";
  if (ext === ".json") return "application/json; charset=utf-8";
  if (ext === ".svg") return "image/svg+xml";
  if (ext === ".png") return "image/png";
  if (ext === ".jpg" || ext === ".jpeg") return "image/jpeg";
  return "application/octet-stream";
}

function createWorkItem(payload, comment, now, queue = []) {
  const marker = {
    ...comment,
    markerId: comment.markerId || comment.id,
    messages: Array.isArray(comment.messages) ? comment.messages : []
  };
  const id = `afw-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
  const inheritedSummary = latestThreadSummary(queue, payload.artifactPath, marker.markerId);
  return {
    id,
    markerId: marker.markerId,
    status: "queued",
    workerStatus: "queued",
    createdAt: now,
    updatedAt: now,
    sentAt: payload.sentAt || now,
    artifactPath: payload.artifactPath,
    artifactTitle: payload.artifactTitle,
    artifactVersion: payload.artifactVersion || "unversioned",
    selector: marker.selector,
    visibleText: marker.selectedText || marker.text || latestUserMessage(marker),
    latestUserMessage: latestUserMessage(marker),
    ui: marker.ui || null,
    rect: marker.rect || null,
    threadSummary: inheritedSummary,
    lastProcessedAt: null,
    marker,
    payload: {
      artifactPath: payload.artifactPath,
      artifactTitle: payload.artifactTitle,
      artifactVersion: payload.artifactVersion || "unversioned",
      sentAt: payload.sentAt || now,
      comments: [marker]
    }
  };
}

function artifactPathFor(item) {
  return item.artifactPath || item.payload?.artifactPath;
}

function markerFor(item) {
  return item.marker || item.payload?.comments?.[0] || {};
}

function latestUserMessage(marker) {
  const messages = Array.isArray(marker.messages) ? marker.messages : [];
  const latest = messages.filter((message) => message.role !== "agent" && message.text).at(-1);
  return latest?.text || marker.text || "";
}

function latestThreadSummary(queue, artifactPath, markerId) {
  return [...queue]
    .reverse()
    .find((item) => artifactPathFor(item) === artifactPath && (item.markerId || markerFor(item).markerId || markerFor(item).id) === markerId && item.threadSummary)
    ?.threadSummary || "";
}

async function notifyAgentWebhook(items, payload) {
  if (!webhookUrl) return { configured: false, delivered: false };

  const body = JSON.stringify({
    event: "agent_feedback.marker_queued",
    createdAt: new Date().toISOString(),
    artifact: {
      path: payload.artifactPath,
      title: payload.artifactTitle,
      version: payload.artifactVersion || "unversioned"
    },
    items: items.map(summarizeItem)
  });
  const headers = {
    "content-type": "application/json",
    "user-agent": "agent-feedback-artifact/1"
  };
  if (webhookSecret) {
    headers["x-agent-feedback-signature"] = `sha256=${createHmac("sha256", webhookSecret).update(body).digest("hex")}`;
  }

  try {
    const response = await postWebhook(webhookUrl, headers, body, webhookTimeoutMs);
    return {
      configured: true,
      delivered: response.status >= 200 && response.status < 300,
      status: response.status
    };
  } catch (error) {
    return {
      configured: true,
      delivered: false,
      error: error.cause?.message ? `${error.message}: ${error.cause.message}` : error.message
    };
  }
}

function postWebhook(targetUrl, headers, body, timeoutMs) {
  return new Promise((resolvePost, rejectPost) => {
    const url = new URL(targetUrl);
    const transport = url.protocol === "https:" ? httpsRequest : httpRequest;
    const req = transport(url, {
      method: "POST",
      headers: {
        ...headers,
        "content-length": Buffer.byteLength(body)
      },
      timeout: timeoutMs
    }, (res) => {
      res.resume();
      res.on("end", () => resolvePost({ status: res.statusCode || 0 }));
    });
    req.on("timeout", () => req.destroy(new Error(`webhook_timeout_after_${timeoutMs}ms`)));
    req.on("error", rejectPost);
    req.end(body);
  });
}

function attachRouteMetadata(item) {
  const route = classifyWorkItem(item);
  item.workerRoute = route.route;
  item.contextTier = route.contextTier;
  item.workerLifecycle = route.workerLifecycle;
  item.routeReason = route.reason;
  item.recommendedModel = route.model;
  item.recommendedReasoningEffort = route.reasoningEffort;
  return item;
}

function summarizeItem(item) {
  const marker = markerFor(item);
  const route = classifyWorkItem(item);
  return {
    id: item.id,
    markerId: item.markerId || marker.markerId || marker.id,
    status: item.status,
    workerStatus: item.workerStatus || item.status,
    createdAt: item.createdAt,
    updatedAt: item.updatedAt,
    artifactPath: artifactPathFor(item),
    artifactTitle: item.artifactTitle || item.payload?.artifactTitle,
    artifactVersion: item.artifactVersion || item.payload?.artifactVersion,
    selector: item.selector || marker.selector,
    visibleText: item.visibleText || marker.selectedText || marker.text || "",
    latestUserMessage: item.latestUserMessage || latestUserMessage(marker),
    threadSummary: item.threadSummary || "",
    lastProcessedAt: item.lastProcessedAt || null,
    ...routeSummary(item, route),
    commentCount: marker?.id ? 1 : 0,
    marker: {
      id: marker.id,
      markerId: item.markerId || marker.markerId || marker.id,
      text: marker.text,
      selector: marker.selector,
      status: marker.status || item.status
    }
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  process.on("SIGTERM", () => server.close(() => process.exit(0)));
}
