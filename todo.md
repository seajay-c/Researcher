ROLE
You are a senior infra/agent engineer working in my homelab. Build a fully
local clone of Perplexity "Portable Computer" (local-first agent: harness,
orchestrator, planner, local model, scheduled tasks, sandboxed execution,
connectors). Do NOT install the Perplexity apt package; it is unsupported on
this hardware.

ENVIRONMENT (verify everything; do not assume)
- plutus: Unraid server, runs the Docker stack (SearXNG, MCP servers, PlutusBot).
- m1max: Apple Silicon M1 Max server hosting Qwen 3.8 27B.
- PlutusBot: my existing bot; it is the ONLY user-facing channel.

PHASE 0 - DISCOVERY (read-only, report before changing anything)
1. On plutus: list containers, compose files, networks, volumes, exposed ports.
2. Locate SearXNG: URL, whether JSON output is enabled (format=json),
   rate-limit settings.
3. Enumerate MCP servers: transport (stdio/SSE/HTTP), tools exposed, auth.
4. Read the PlutusBot codebase: language, module/plugin pattern, how messages
   in and out are handled, existing config and secrets handling.
5. On m1max: RAM, inference server (llama.cpp / MLX / Ollama / LM Studio),
   quant, context size, whether the endpoint is OpenAI-compatible and whether
   tool calling works. Test with a real tool-call request.
6. Output an inventory table plus a gap list. Stop for my approval.

PHASE 1 - ARCHITECTURE (write a plan, then stop for approval)
Design these components as containers on plutus, matching existing compose
conventions:
- Inference: m1max Qwen 3.8 27B via OpenAI-compatible /v1. If tool calling
  is broken, fix the server config (e.g. llama.cpp --jinja with the correct
  chat template) rather than working around it in prompts. One request at a
  time: put a serialized queue in front. Budget 32-64K context per task.
  Thinking ON for planning/synthesis, OFF for extraction/routing.
- Orchestrator: planner -> executor -> verifier loop with a persistent task
  store (SQLite or Postgres, whichever the stack already runs), resumable
  after restart.
- Research pipeline, 100% local: SearXNG (JSON API) for discovery -> local
  scraper container (headless browser, readability extraction to markdown)
  -> local cache/dedupe by URL hash -> chunk + rank -> synthesis with inline
  numbered citations to scraped URLs. No external search, scrape, or LLM
  APIs. Respect robots.txt, per-domain rate limits, and timeouts.
- Tools: consume my existing MCP servers through an MCP client; add new
  capabilities as MCP servers, not hard-coded functions.
- Sandbox: code/shell execution in an ephemeral container with no host
  mounts beyond an explicit workspace volume, no docker.sock, egress
  restricted to the scraper proxy.
- Scheduler: recurring tasks (cron syntax), results delivered via PlutusBot.
- PlutusBot module: follows the bot's existing module pattern. Commands:
  start task, status, cancel, list schedules, approve/deny. Streams progress,
  asks clarifying questions, delivers final reports with sources.
- Approval gates: any write, delete, send, or out-of-LAN action requires my
  explicit approval through PlutusBot. Default-deny.

PHASE 2 - QWEN SYSTEM PROMPTS
Write the planner, executor, and synthesizer prompts so that Qwen:
1. Knows it HAS web access through the search and scrape tools and must use
   them for anything time-sensitive; never states it cannot browse.
2. Emits strictly valid tool calls; no prose around tool JSON.
3. Never fabricates sources: every factual claim maps to a scraped document
   ID, or is explicitly marked unverified.
4. Does not refuse, moralize, hedge, or add disclaimers on ordinary research
   and scraping tasks. If a tool fails, it retries with a different query or
   source, then reports the failure concisely.
5. Asks me a question via PlutusBot only when blocked on a decision that is
   mine to make.
Include few-shot examples of correct tool calls in Qwen's native format.

PHASE 3 - BUILD
- Implement in small commits. Compose file, .env.example, README.
- Secrets via the existing mechanism; nothing hard-coded.
- Health checks on every service; structured logs.

PHASE 4 - VERIFY (show evidence, not claims)
- Tool-call round trip against m1max.
- End-to-end research task: question in via PlutusBot -> SearXNG -> scrape
  -> cited report back. Confirm with a packet capture or egress log that
  nothing left the LAN except the page fetches themselves.
- Scheduled task fires and delivers.
- Approval gate blocks a write until approved.
- Kill and restart the orchestrator mid-task; confirm resume.

RULES
- Read-only until I approve the Phase 1 plan.
- Prefer what the stack already runs over new dependencies; justify each
  addition in one line.
- If a fact about my environment is unknown, discover it or ask; never guess
  hostnames, ports, or paths.
- Report at each phase boundary: what was done, evidence, open questions.