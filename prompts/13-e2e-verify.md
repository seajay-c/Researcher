# INCREMENT 13: End-to-end verification with evidence

- **Status:** Standard
- **Dependencies:** 12
- **SRS IDs:** **SRS-FR-006**, **SRS-FR-007**, **SRS-FR-008**, **SRS-NFR-001**, **SRS-NFR-005**, **SRS-NFR-006**, **SRS-NFR-008**

### Rules

- Change no application code unless a check fails. If one fails, set the row to red and follow the red-zone steps.
- Record command output as evidence in `prompts/tracking.md`, not as claims.

### Capability

Live proof that the whole system meets the SRS.

### May change

Only `prompts/tracking.md`.

### Implementation and verification

1. `.venv/bin/pytest` and `.venv/bin/python tests/smoke_m1max.py`: both pass.
2. Start `sudo tcpdump -i any -nn 'tcp[tcpflags] & tcp-syn != 0 and (src host 12.0.0.179 or src host 100.100.88.116)' -w /tmp/researcher.pcap`. Run one research task from the GUI. Stop tcpdump, then list the destination hosts with `tcpdump -nn -r /tmp/researcher.pcap | awk '{print $5}' | sort -u`. Expect only `100.67.98.112.8080` and `12.0.0.225.3000`, plus your browser's connection to `:8090`, which is inbound (**SRS-NFR-001**).
3. Citation check: for each `[n]` in that `report.md`, `sources/` holds a file for n. There are 8–15 source files (**SRS-FR-006**, **SRS-FR-008**).
4. Ask a question the sources can't answer (for example, an event dated after the scrape). The report or answer contains `[unverified]` or a fresh search (**SRS-FR-007**).
5. Run `grep -iE "cannot browse|can't browse|as an ai|I'm unable"` over three reports and their follow-ups. It finds nothing (**SRS-NFR-008**).
6. Pipe the server log through `python -c 'import sys,json;[json.loads(l) for l in sys.stdin]'`. It exits 0 (**SRS-NFR-006**). `git grep "$M1MAX_API_KEY"` finds nothing (**SRS-NFR-005**).
7. Walk every `must` row in `srs.md` and confirm each has evidence in tracking.

### Rules (repeat)

- Record evidence, not claims. Change code only through the red-zone steps.
