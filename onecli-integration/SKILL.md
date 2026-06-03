---
name: onecli-integration
description: Configure or modify OneCLI integrations in agentic apps. Use when adding `@onecli-sh/sdk`, wiring OneCLI into container or process launchers, managing OneCLI agent identifiers, or adding manual approval flows.
---

# OneCLI Integration

Project-agnostic workflow for integrating OneCLI into any app that launches agents, containers, or isolated runtime processes. Integrate OneCLI at the runtime boundary. Prefer the published SDK and the server-owned `/api/container-config` contract over app-local proxy logic.

## Retrieve First

- Read `/Users/gurusharan/.codex/docs/references/onecli-integration.md`
- Search the codebase for:
  - `docker run`
  - `spawn(`
  - `execa(`
  - `container`
  - `agent`
  - `approval`

## Decision Order

1. Identify the integration lane:
   - containerized runtime -> `applyContainerConfig`
   - non-container process runtime -> `getContainerConfig`
   - durable logical agents -> `ensureAgent` or `createAgent`
   - human approval workflow -> `configureManualApproval`
2. Patch the narrowest boundary that owns runtime launch.
3. Preserve feature-off behavior when `ONECLI_API_KEY` is absent unless the user explicitly wants fail-closed behavior.
4. Add or update tests for both active and inactive OneCLI paths.

## Containerized Runtime Pattern

Install:

```bash
pnpm add @onecli-sh/sdk
```

Wire the SDK where launch args are built:

```ts
import { OneCLI } from "@onecli-sh/sdk";

const onecli = process.env.ONECLI_API_KEY
  ? new OneCLI({
      apiKey: process.env.ONECLI_API_KEY,
      url: process.env.ONECLI_URL,
    })
  : null;

if (onecli) {
  const active = await onecli.applyContainerConfig(args, {
    agent: agentIdentifier,
  });

  if (!active) {
    logger.warn("OneCLI not reachable");
  }
}
```

Rules:
- Call it immediately before `docker run`, `container run`, or equivalent launch.
- Keep `combineCaBundle` at the default `true` unless the runtime has a stronger CA strategy already.
- Keep `addHostMapping` at the default `true` unless the runtime already provides host mapping or is not Docker-based.
- Preserve runtime-specific host-gateway rewrites already required by the target execution environment.

## Non-Container Pattern

Use `getContainerConfig(agent)` when the runtime is a direct child process or another non-Docker execution model.

Apply the returned material in one adapter:
- export the returned env vars
- write the CA PEM to disk
- point the runtime at the CA file

Do not copy OneCLI-specific env-building into individual provider clients.

## Agent Lifecycle Pattern

Use `ensureAgent({ name, identifier })` when the app owns stable named agents.

Rules:
- `identifier` must be stable and deterministic
- lowercase letters, numbers, and hyphens only
- do not regenerate identifiers per run
- use `createAgent` only when collisions should surface as errors

## Approval Pattern

Only add manual approvals when the product explicitly needs request gating.

Rules:
- use `configureManualApproval(callback)`
- callback must be fast and idempotent
- expect concurrent callbacks for separate approvals
- failures retry on the next poll cycle
- set `ONECLI_GATEWAY_URL` only if auto-resolution from the web app is not appropriate

## Modification Rules

- Do not hand-build proxy URLs or CA paths.
- Do not put real upstream secrets into runtime env vars.
- Prefer the SDK over direct web API calls unless the app needs a non-Node or non-Docker adapter.
- If the existing integration already uses OneCLI, extend that owner module instead of creating a second OneCLI entrypoint.

## Validation

- Verify `ONECLI_API_KEY` and `ONECLI_URL` wiring.
- Verify args mutation or runtime env application in tests.
- Verify the runtime does not receive real secrets.
- Verify graceful degradation or fail-closed behavior matches the product requirement.
- For approvals, verify callback registration and stop handling.
