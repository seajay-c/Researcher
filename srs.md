# Software requirements specification

## Identity

Researcher

## Purpose

This spec is for the implementation agent and for the owner (the person reviewing the build). It defines a small local research agent: give it a question and it returns a cited report. Every source behind the report is saved next to it.

## Scope

Researcher takes a question and runs Qwen 3.8 27B (hosted on the m1max) in a tool-calling loop. It searches the web with SearXNG and scrapes the best pages through MCP-Searxng, then writes a markdown report with numbered citations. The report and every scraped source go into one folder under `research/`. A basic web GUI lists these folders, shows the reports and sources, starts new research, and answers follow-up questions about a report. Inference, search and storage all stay on the homelab.

## Product perspective

It's a standalone program running on vm1 (12.0.0.179, tailnet 100.100.88.116). It uses three existing systems:

- **m1max**: Qwen 3.8 27B behind an OpenAI-compatible `/v1` endpoint at `100.67.98.112:8080`, with its own API key. Called directly, not through OmniRoute.
- **MCP-Searxng** (`isokoliuk/mcp-searxng`) on plutus, over HTTP MCP at `12.0.0.225:3000/mcp`. It provides `searxng_web_search` and `web_url_read`.
- **SearXNG** on plutus. Reached only through MCP-Searxng.

This is v1 of the local "Portable Computer" described in `todo.md`. The rest of `todo.md` comes in later versions (see Out of scope).

## Users

- Owner: one technical user on the LAN or tailnet. They ask research questions, read reports, check sources and ask follow-ups. They can run CLI commands and edit `.env`.

## Product functions

- Run research: plan, search, scrape and save sources, then write a cited report.
- Resume research that a crash or restart interrupted.
- Answer follow-up questions about a report, searching again when the saved sources don't cover the question.
- Web GUI: browse research folders, read reports and sources, start research, chat follow-ups.

## Assumptions and dependencies

- The m1max serves Qwen 3.8 27B with working OpenAI-style tool calling and per-request thinking on/off. Unverified: increment 1 must prove it with a real tool-call request. If it fails, fix the server config (for example llama.cpp `--jinja` with the correct template). Don't work around it in prompts.
- MCP-Searxng answers on `12.0.0.225:3000` from the LAN. This needs `MCP_HTTP_HOST=0.0.0.0` set on the container; that work was handed to the Unraid agent.
- `web_url_read` fetches pages directly as plain HTTP and returns markdown. It doesn't run JavaScript.
- vm1 has Python 3.12. `uv` is not installed.

## Out of scope

Don't build these in v1. They're later phases from `todo.md`:

- The PlutusBot module or any chat-app channel.
- Cron scheduler and scheduled tasks.
- Code/shell sandbox container.
- Approval gates (v1 has no write, delete or send tools that would need them).
- Headless-browser scraping, a separate scraper container.
- Docker or compose deployment.
- GUI login or multi-user support.
- Any external search, scrape or LLM API.

## Requirements

| ID | Statement | Priority | Verification |
| --- | --- | --- | --- |
| SRS-FR-001 | Starting research with a question (CLI or GUI) creates a new folder `research/<YYYY-MM-DD>-<slug>/`. | must | Run one question and see the folder appear. |
| SRS-FR-002 | The agent finds candidate pages only through the MCP tool `searxng_web_search`. | must | The run log shows search calls going to MCP-Searxng. |
| SRS-FR-003 | Each page the agent uses is fetched with `web_url_read` and saved as `sources/NN-<domain>.md`, with a header giving its URL, title, fetch time and source number. | must | Open the source files and check the headers match the URLs fetched. |
| SRS-FR-004 | A URL already saved in the folder is not fetched again. | must | Re-run or resume and see no second fetch for the same URL in the log. |
| SRS-FR-005 | Before fetching a page, the agent reads that site's `robots.txt` through `web_url_read` and skips pages it disallows. It waits at least 2 s between fetches to the same domain, and each fetch times out after 30 s. | must | Test against a disallowed URL and see a "skipped: robots" log entry. Log timestamps show the per-domain gap. |
| SRS-FR-006 | `report.md` cites sources inline as `[n]`, where n is a saved source's number, and ends with a numbered list of those sources and their URLs. | must | Every `[n]` in the report has a matching `sources/NN-*.md` file, checked by a script. |
| SRS-FR-007 | A claim that no saved source supports is marked `[unverified]` in the report. | must | Prompt test: give a question the fake sources can't answer and see `[unverified]` in the output. |
| SRS-FR-008 | Default research saves 8–15 sources. The maximum can be changed in config. | must | Count the source files after a default run. |
| SRS-FR-009 | When a tool call fails, the agent retries with a different query or source, at most 3 times per step. After that it records the failure in one line in the report and continues. | must | Fake MCP failures in a test and see the retries and the failure line. |
| SRS-FR-010 | The agent saves task state to `state.json` in the folder after every step. Running resume, or restarting the GUI server, continues unfinished tasks from their last saved step. | must | Kill the process mid-run, restart it, and see it finish without redoing completed steps. |
| SRS-FR-011 | A follow-up question about a report is answered first from that folder's saved sources. If those don't cover it, the agent searches and scrapes more, saves the new pages under the next source numbers in the same folder, and cites them. | must | Ask a covered question and see no new fetches. Ask an uncovered one and see new numbered source files. |
| SRS-FR-012 | Each follow-up question and its cited answer are appended to `followups.md` in the folder. | must | Check the file after two follow-ups. |
| SRS-FR-013 | The GUI lists research folders newest first, with each folder's question and status. | must | Open the GUI and see the list. |
| SRS-FR-014 | The GUI renders `report.md`, and each `[n]` citation links to the rendered source file. | must | Click a citation and see the source page open. |
| SRS-FR-015 | The GUI has a follow-up chat on each report that shows earlier follow-ups and sends new ones (SRS-FR-011). | must | Ask a follow-up in the browser and see the answer appear and be saved. |
| SRS-FR-016 | The GUI can start new research and shows a progress log that updates while it runs. | must | Start research from the GUI and watch the steps appear. |
| SRS-FR-017 | Model calls run with thinking on for planning and synthesis, and off for picking URLs and extracting text. | should | The request log shows the thinking flag for each call type. |
| SRS-NFR-001 | The program opens network connections only to the m1max endpoint and MCP-Searxng. All page and robots fetches happen inside MCP-Searxng. | must | `ss -tnp` or tcpdump on vm1 during a run shows only those two hosts. |
| SRS-NFR-002 | At most one model request is in flight at a time, across research and follow-ups. | must | A test fires two tasks at once and sees model calls never overlap. |
| SRS-NFR-003 | No single model request goes over the configured context budget (default 48K tokens, allowed range 32–64K). Source text is chunked and ranked to fit. | must | Unit test with oversized sources: the prompt stays under budget. |
| SRS-NFR-004 | Tool calls with invalid JSON or unknown tools are not executed. The model is asked again with the error. | must | Unit test with a fake model that sends bad JSON. |
| SRS-NFR-005 | Secrets (the m1max key) come only from `.env`, which git ignores. `.env.example` lists every variable. | must | `git grep` finds no key. The app starts with only `.env` set. |
| SRS-NFR-006 | Logs are JSON lines, one event per line, with a task ID. | must | Read the log and check each line is valid JSON. |
| SRS-NFR-007 | The GUI listens on vm1's LAN and tailnet addresses without auth. | must | Open it from another LAN machine. |
| SRS-NFR-008 | The agent never says it can't browse, and adds no refusals or disclaimers to ordinary research. | should | Read three test transcripts and find none of these phrases. |
| SRS-NFR-009 | A health endpoint reports whether the m1max and MCP-Searxng answer. | should | `curl /health` returns JSON with both statuses. |

## Logical data

- Research folder: question, status, timestamps, plan, steps done, sources (number, URL, title, fetch time), report, follow-ups.
- No database. The folder is the record.

## Performance

- Default research finishes in about 15 minutes or less on the m1max. This isn't an NFR row; it depends on the hardware.
