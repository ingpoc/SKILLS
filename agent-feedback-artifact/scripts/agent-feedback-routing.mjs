export function classifyWorkItem(item) {
  const marker = markerFor(item);
  const latest = latestUserMessage(marker) || item.latestUserMessage || "";
  const haystack = `${latest}\n${item.visibleText || ""}`.toLowerCase();
  const styleIntent = /\b(bigger|smaller|font|typography|weight|stronger|bold|color|spacing|align|padding|margin|ui|style|layout|button|icon|copy|text)\b/i.test(haystack);
  const dataIntent = /\b(total|gross|taxable|tax|refund|liability|income|calculate|recalculate|dependent|derive|data|amount|number|incorrect|wrong|not)\b|₹|rs\.?/i.test(haystack);
  const explanationIntent = /\b(explain|why|what changed|reply|answer|clarify|summari[sz]e)\b/i.test(haystack);

  if (styleIntent && !dataIntent) {
    return {
      route: "no_worker_main_agent_direct",
      contextTier: "T0",
      workerLifecycle: "none",
      model: null,
      reasoningEffort: null,
      reason: "The marker is a local single-element UI/text adjustment that the main agent can resolve directly with lower overhead than spawning a worker."
    };
  }

  if (explanationIntent && item.threadSummary) {
    return {
      route: "cheap_marker_worker",
      contextTier: "T0",
      workerLifecycle: "fresh_once",
      model: "gpt-5.4-mini",
      reasoningEffort: "low",
      reason: "The marker follow-up asks for an explanation and has a compact thread summary, so a fresh cheap worker can answer without full source context."
    };
  }

  if (dataIntent) {
    return {
      route: "deep_marker_worker",
      contextTier: "T2",
      workerLifecycle: "fresh_once",
      model: "gpt-5.4-mini",
      reasoningEffort: "medium",
      reason: "The marker can affect source/data or dependent values, so a fresh worker should inspect details and narrow source slices before proposing a fix."
    };
  }

  if (styleIntent) {
    return {
      route: "no_worker_main_agent_direct",
      contextTier: "T0",
      workerLifecycle: "none",
      model: null,
      reasoningEffort: null,
      reason: "The marker is a local single-element UI/text adjustment that the main agent can resolve directly with lower overhead than spawning a worker."
    };
  }

  if (explanationIntent) {
    return {
      route: "cheap_marker_worker",
      contextTier: "T0",
      workerLifecycle: "fresh_once",
      model: "gpt-5.4-mini",
      reasoningEffort: "low",
      reason: "The marker is an explanation or follow-up that should be answerable from the compact marker thread summary."
    };
  }

  return {
    route: "cheap_marker_worker",
    contextTier: "T1",
    workerLifecycle: "fresh_once",
    model: "gpt-5.4-mini",
    reasoningEffort: "low",
    reason: "The marker needs a scoped diagnosis, but not full artifact context by default."
  };
}

export function buildWorkerPrompt(item, route = classifyWorkItem(item)) {
  const marker = markerFor(item);
  const commandHint = route.contextTier === "T2"
    ? `You may request progressive context with: node scripts/agent-feedback-details.mjs ${item.id}, then inspect only the narrow source/data slices needed.`
    : `Use the packet below first. Request details only if the marker packet is insufficient.`;
  const prompt = [
    "You are a marker-scoped artifact feedback worker.",
    "Do not edit files unless the main agent explicitly assigns a disjoint write scope.",
    "Diagnose this marker, propose the smallest fix or reply, and return structured JSON for the main agent.",
    commandHint,
    "",
    `workId: ${item.id}`,
    `markerId: ${item.markerId || marker.markerId || marker.id}`,
    `route: ${route.route}`,
    `contextTier: ${route.contextTier}`,
    `artifactPath: ${item.artifactPath || item.payload?.artifactPath || ""}`,
    `artifactTitle: ${item.artifactTitle || item.payload?.artifactTitle || ""}`,
    `artifactVersion: ${item.artifactVersion || item.payload?.artifactVersion || "unversioned"}`,
    `selector: ${item.selector || marker.selector || ""}`,
    `visibleText: ${item.visibleText || marker.selectedText || marker.text || ""}`,
    `latestUserMessage: ${item.latestUserMessage || latestUserMessage(marker)}`,
    `threadSummary: ${item.threadSummary || "(empty)"}`,
    "",
    "Return JSON only with keys:",
    "can_solve, extra_context_used, proposed_change, agent_reply, files_to_edit, risk, thread_summary_update, main_agent_role"
  ].join("\n");

  return {
    spawn: route.workerLifecycle === "none" ? null : {
      agent_type: "worker",
      fork_context: false,
      model: route.model,
      reasoning_effort: route.reasoningEffort,
      message: prompt
    },
    prompt
  };
}

export function routeSummary(item, route = classifyWorkItem(item)) {
  const worker = buildWorkerPrompt(item, route);
  return {
    route: route.route,
    contextTier: route.contextTier,
    workerLifecycle: route.workerLifecycle,
    model: route.model,
    reasoningEffort: route.reasoningEffort,
    routeReason: route.reason,
    workerPrompt: worker.prompt,
    spawn: worker.spawn
  };
}

export function summarizeThread(item, agentMessage = "") {
  const marker = markerFor(item);
  const latest = item.latestUserMessage || latestUserMessage(marker);
  const prior = item.threadSummary ? `${item.threadSummary}\n` : "";
  const response = agentMessage || item.agentMessage || "";
  return `${prior}Marker ${item.markerId || marker.markerId || marker.id}: user asked "${latest}".${response ? ` Agent replied "${response}".` : ""}`.trim();
}

export function markerFor(item) {
  return item.marker || item.payload?.comments?.[0] || {};
}

export function latestUserMessage(marker) {
  const messages = Array.isArray(marker.messages) ? marker.messages : [];
  const latest = messages.filter((message) => message.role !== "agent" && message.text).at(-1);
  return latest?.text || marker.text || "";
}
