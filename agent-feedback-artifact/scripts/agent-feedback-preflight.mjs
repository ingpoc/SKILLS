#!/usr/bin/env node
import { access, readFile } from "node:fs/promises";
import { constants } from "node:fs";
import { basename, dirname, resolve } from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

const args = process.argv.slice(2);
const targetArg = args.find((arg) => !arg.startsWith("--"));
const port = Number(valueFor("--port") || 4177);

if (!targetArg) {
  console.error("Usage: scripts/agent-feedback-preflight.mjs <artifact.html> [--port 4177]");
  process.exit(2);
}

const target = resolve(process.cwd(), targetArg);
const root = dirname(target);
const queuePath = resolve(root, "data", "feedback-queue.json");
const serverScript = resolve(import.meta.dirname, "artifact-feedback-server.mjs");
const fallbackServerScript = resolve(import.meta.dirname, "..", "server", "artifact-feedback-server.mjs");
const html = await readFile(target, "utf8").catch((error) => fail(`target_read_failed: ${error.message}`));
const widgetInstalled = html.includes("AGENT_FEEDBACK_WIDGET_START") && html.includes("AGENT_FEEDBACK_WIDGET_END");
const hasBody = /<\/body>/i.test(html);
const serverScriptPath = await canRead(serverScript) ? serverScript : fallbackServerScript;
const serverScriptReadable = await canRead(serverScriptPath);
const queueState = await queueAccess(queuePath);
const portState = await checkPort(port);
const webhookUrl = process.env.AGENT_FEEDBACK_WEBHOOK_URL || "";

const report = {
  ok: Boolean(hasBody && serverScriptReadable),
  target,
  targetName: basename(target),
  hasBody,
  widgetInstalled,
  serverScript: serverScriptReadable ? serverScriptPath : null,
  port,
  portAvailable: portState.available,
  portMessage: portState.message,
  webhook: {
    configured: Boolean(webhookUrl),
    url: webhookUrl || null,
    timeoutMs: Number(process.env.AGENT_FEEDBACK_WEBHOOK_TIMEOUT_MS || 2500),
    signingConfigured: Boolean(process.env.AGENT_FEEDBACK_WEBHOOK_SECRET)
  },
  queue: queueState,
  nextCommands: {
    add: widgetInstalled ? null : `node ${resolve(import.meta.dirname, "add-agent-feedback.mjs")} ${target}`,
    startServer: `node ${serverScriptPath} ${root} ${port}`,
    open: `http://localhost:${port}/${basename(target)}`,
    closeout: `node ${resolve(import.meta.dirname, "agent-feedback-closeout.mjs")} ${target} --port ${port}`
  }
};

console.log(JSON.stringify(report, null, 2));
if (!report.ok) process.exit(1);

function valueFor(name) {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : null;
}

function fail(message) {
  console.error(message);
  process.exit(1);
}

async function canRead(path) {
  try {
    await access(path, constants.R_OK);
    return true;
  } catch {
    return false;
  }
}

async function queueAccess(path) {
  try {
    await access(path, constants.R_OK | constants.W_OK);
    return { path, exists: true, readable: true, writable: true };
  } catch {
    return { path, exists: false, readable: false, writable: false };
  }
}

function checkPort(portNumber) {
  return execFileAsync("lsof", ["-nP", `-iTCP:${portNumber}`, "-sTCP:LISTEN"])
    .then(({ stdout }) => ({
      available: false,
      message: stdout.trim().split("\n").slice(1).join("\n") || "already_listening"
    }))
    .catch(() => ({ available: true, message: "available" }));
}
