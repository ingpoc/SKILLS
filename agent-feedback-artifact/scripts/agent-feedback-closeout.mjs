#!/usr/bin/env node
import { readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { basename, dirname, resolve } from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

const args = process.argv.slice(2);
const targetArg = args.find((arg) => !arg.startsWith("--"));
const port = Number(valueFor("--port") || 4177);
const clearLocalQueue = args.includes("--clear-local-queue");

if (!targetArg) {
  console.error("Usage: scripts/agent-feedback-closeout.mjs <artifact.html> [--port 4177] [--clear-local-queue]");
  process.exit(2);
}

const target = resolve(process.cwd(), targetArg);
const root = dirname(target);
const artifactPath = `/${basename(target)}`;
const queuePath = resolve(root, "data", "feedback-queue.json");
const html = await readFile(target, "utf8").catch((error) => fail(`target_read_failed: ${error.message}`));
const widgetInstalled = html.includes("AGENT_FEEDBACK_WIDGET_START") && html.includes("AGENT_FEEDBACK_WIDGET_END");
const serverListening = await isListening(port);
const webhookUrl = process.env.AGENT_FEEDBACK_WEBHOOK_URL || "";
let queue = [];
let queueReadable = false;

if (existsSync(queuePath)) {
  queue = JSON.parse(await readFile(queuePath, "utf8"));
  queueReadable = true;
}

const matching = queue.filter((item) => artifactPathFor(item) === artifactPath);
const counts = countByStatus(matching);
let cleared = false;

if (clearLocalQueue) {
  if (!isTestDuplicate(target)) {
    fail("--clear-local-queue is allowed only for test/verify/smoke/roundtrip duplicate artifacts");
  }
  const remaining = queue.filter((item) => artifactPathFor(item) !== artifactPath);
  await writeFile(queuePath, `${JSON.stringify(remaining, null, 2)}\n`);
  cleared = true;
}

const report = {
  ok: true,
  target,
  artifactPath,
  widgetInstalled,
  server: {
    port,
    listening: serverListening
  },
  webhook: {
    configured: Boolean(webhookUrl),
    url: webhookUrl || null,
    timeoutMs: Number(process.env.AGENT_FEEDBACK_WEBHOOK_TIMEOUT_MS || 2500),
    signingConfigured: Boolean(process.env.AGENT_FEEDBACK_WEBHOOK_SECRET)
  },
  queue: {
    path: queuePath,
    readable: queueReadable,
    totalForArtifact: matching.length,
    counts,
    cleared
  },
  cleanupCommands: {
    removeCapability: `node ${resolve(import.meta.dirname, "remove-agent-feedback.mjs")} ${target}`,
    clearLocalQueue: `node ${resolve(import.meta.dirname, "agent-feedback-closeout.mjs")} ${target} --port ${port} --clear-local-queue`
  }
};

console.log(JSON.stringify(report, null, 2));

function valueFor(name) {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : null;
}

function fail(message) {
  console.error(message);
  process.exit(1);
}

function artifactPathFor(item) {
  return item.artifactPath || item.payload?.artifactPath;
}

function countByStatus(items) {
  return items.reduce((acc, item) => {
    const status = item.status || "unknown";
    acc[status] = (acc[status] || 0) + 1;
    return acc;
  }, { queued: 0, processing: 0, done: 0, blocked: 0, canceled: 0 });
}

function isTestDuplicate(path) {
  return /(test|smoke|verify|roundtrip|duplicate|clear)/i.test(basename(path));
}

function isListening(portNumber) {
  return execFileAsync("lsof", ["-nP", `-iTCP:${portNumber}`, "-sTCP:LISTEN"])
    .then(({ stdout }) => stdout.trim().split("\n").length > 1)
    .catch(() => false);
}
