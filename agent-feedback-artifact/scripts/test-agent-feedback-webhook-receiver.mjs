#!/usr/bin/env node
import { createServer } from "node:http";
import { appendFile, mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const port = Number(process.argv[2] || 4188);
const logPath = resolve(process.cwd(), "data", "webhook-events.jsonl");

await mkdir(dirname(logPath), { recursive: true });
await writeFile(logPath, "");

const server = createServer(async (req, res) => {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const body = Buffer.concat(chunks).toString("utf8");
  await appendFile(logPath, `${JSON.stringify({
    method: req.method,
    url: req.url,
    headers: req.headers,
    body: JSON.parse(body || "{}")
  })}\n`);
  res.writeHead(202, { "content-type": "application/json" });
  res.end(JSON.stringify({ ok: true }));
});

server.listen(port, () => {
  console.log(`Webhook receiver: http://127.0.0.1:${port}/hook`);
  console.log(`Log: ${logPath}`);
});

process.on("SIGTERM", () => server.close(() => process.exit(0)));
