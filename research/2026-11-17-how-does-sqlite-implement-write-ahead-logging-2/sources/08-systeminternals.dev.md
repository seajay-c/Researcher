---
n: 8
url: https://systeminternals.dev/sqlite/wal/
title: SQLite Write-Ahead Logging
fetched_at: 2026-11-17T07:01:21.177633Z
---

[⚡ Systems Explained](/) 

Databases ▾ 

[🐘 PostgreSQL](/postgresql/) [🍃 MongoDB](/mongodb/) [🔴 Redis](/redis/) [👁️ Cassandra](/cassandra/) [🔍 Elasticsearch](/elasticsearch/) [🏠 ClickHouse](/clickhouse/) [⚡ DynamoDB](/dynamodb/) [🔷 TiDB](/tidb/) [🔥 CockroachDB](/cockroachdb/) [🔱 Vitess](/vitess/) [⚡ Spanner](/spanner/) [🛡️ RocksDB](/rocksdb/) [🦆 DuckDB](/duckdb/) 

Streaming ▾ 

[📨 Kafka](/kafka/) [⚡ Spark](/spark/) 

Infrastructure ▾ 

[☸️ Kubernetes](/kubernetes/) [🐳 Docker](/docker/) [🔺 Envoy](/envoy/) [📊 Prometheus](/prometheus/) [📡 Observability](/observability/) [🔌 gRPC](/grpc/) 

AI / ML ▾ 

[🧠 LLM Internals](/llm/) [🤖 Claude Code Internals](/claude-code/) 

Interviews ▾ 

[📐 System Design](/system-design-interview/) 

Security ▾ 

[🔑 OAuth 2.0](/security/oauth2/) [🎫 JWT Tokens](/security/jwt/) [🔒 TLS 1.3 Handshake](/security/tls-handshake/) [🛡️ Zero Trust](/security/zero-trust/) 

Blockchain ▾ 

[⟠ Ethereum](/ethereum/) 

Resources ▾ 

[🔗 Tools & Hosting](/resources/) 

[About](/about/) 

Databases

[🐘 PostgreSQL](/postgresql/) [🍃 MongoDB](/mongodb/) [🔴 Redis](/redis/) [👁️ Cassandra](/cassandra/) [🔍 Elasticsearch](/elasticsearch/) [🏠 ClickHouse](/clickhouse/) [⚡ DynamoDB](/dynamodb/) [🔷 TiDB](/tidb/) [🔥 CockroachDB](/cockroachdb/) [🔱 Vitess](/vitess/) [⚡ Spanner](/spanner/) [🛡️ RocksDB](/rocksdb/) [🦆 DuckDB](/duckdb/) 

Streaming

[📨 Kafka](/kafka/) [⚡ Spark](/spark/) 

Infrastructure

[☸️ Kubernetes](/kubernetes/) [🐳 Docker](/docker/) [🔺 Envoy](/envoy/) [📊 Prometheus](/prometheus/) [📡 Observability](/observability/) [🔌 gRPC](/grpc/) 

AI / ML

[🧠 LLM Internals](/llm/) [🤖 Claude Code Internals](/claude-code/) 

Interviews

[📐 System Design](/system-design-interview/) 

Security

[🔑 OAuth 2.0](/security/oauth2/) [🎫 JWT Tokens](/security/jwt/) [🔒 TLS 1.3](/security/tls-handshake/) [🛡️ Zero Trust](/security/zero-trust/) 

Blockchain

[⟠ Ethereum](/ethereum/) 

[About](/about/) [🔗 Tools & Hosting](/resources/) 

[Home](/) ›[SQLite](/sqlite/) ›[WAL](/sqlite/wal/) 

# SQLite Write-Ahead Logging

WAL is the protocol that makes a SQLite database with multiple concurrent readers and a single writer behave like a real concurrent database. Set `PRAGMA journal_mode=WAL`once and reads stop blocking writes; writes stop blocking reads. The mechanism is a separate append-only log file, a tiny shared-memory index, and a checkpoint process that periodically folds the log back into the main database. This page is the long version — what each byte of the WAL means, how the wal-index lets readers cherry-pick a consistent snapshot, when each checkpoint mode does or doesn't release space, and the sequence of operations during a typical contended workload. 

### WAL Layout

main.db durable database, page-aligned 100-byte db header page 1: schema btree page 2: table btree (root) page 3: index btree (root) … page N (leaf, overflow, freelist) main.db-wal append-only log, frames 32-byte WAL header magic · format · pgsz · ckpt · salts · checksum Frame 1 (24-byte hdr + page) pgno · commit-flag · salts · checksum · 4096B page Frame 2 commit-flag = 0 → not yet committed Frame 3 (commit) commit-flag = page count → durable Frame 4 (later txn) checksum chains across the file … frames continue, checkpoint folds them back main.db-shm shared memory, ephemeral wal-index header read marks · writer mark · backfill mark hash table (8 KB block) page# → frame# (last write of page) hash table (8 KB block) extends as WAL grows no durable data: rebuilt from WAL on crash deleted when last connection closes cleanly 

### Key Numbers

WAL header

32 bytes

Frame header

24 bytes

Default autocheckpoint

1000 pages

Read marks

5 slots

Hash blocks

8192 each

Magic value

0x377f0682/3

Checksum

8-byte chained

### Why WAL Replaced the Rollback Journal

The Gap

In rollback journal mode, every write transaction takes an EXCLUSIVE lock during its final phase. Readers and writers contend for the same lock space. On a busy WAL-less SQLite, you'd see SQLITE\_BUSY storms during sustained reads or any write spike.

The Insight

If new versions of pages live in a separate file, readers can keep reading old versions from the main database while a writer appends new versions to the log. The two streams don't share locks. The cost: a periodic merge step (the checkpoint) that folds the log back.

The Result

Multi-reader concurrency without MVCC, fsync on commit drops to one per transaction (the WAL append) instead of multiple, and write throughput increases roughly 2-3x in mixed workloads. WAL became the default in nearly all SQLite embeddings (iOS, Android Room, modern Python sqlite3 with explicit opt-in).

## The WAL File Format

A 32-byte header plus a stream of identically-formatted frames.

A SQLite WAL file is a sequence of bytes that lives at `filename-wal` next to the database. It opens with a **32-byte WAL header**: 

offset  bytes  field
  0      4    Magic number: 0x377f0682 (little-endian) or 0x377f0683 (big-endian)
  4      4    File format version: 3007000
  8      4    Database page size in bytes (e.g. 4096)
 12      4    Checkpoint sequence number
 16      4    Salt-1: random, regenerated each checkpoint
 20      4    Salt-2: random, regenerated each checkpoint
 24      4    Checksum-1 (over bytes 0..23)
 28      4    Checksum-2 (over bytes 0..23)

The salts are the defense against stale frames. When a checkpoint resets the WAL position to the beginning, fresh salts are written to the header. Any frame still on disk from a previous WAL generation has a different salt and gets ignored on the next read pass. Without this, a crash mid-checkpoint could leave old frames mixed with new and corrupt the database. 

Following the header is a sequence of **frames**. Each frame is a 24-byte header followed by exactly one database page (default 4096 bytes): 

offset  bytes  field
  0      4    Page number being written
  4      4    Commit flag: 0 if not a commit frame; total db page count if it is
  8      4    Salt-1 (must match WAL header)
 12      4    Salt-2 (must match WAL header)
 16      4    Checksum-1 (over previous checksum + frame header + page)
 20      4    Checksum-2 (over previous checksum + frame header + page)
 24    4096   Page contents

The **commit flag** is what makes a transaction durable. While a writer is mid-transaction, it appends frames with commit-flag=0\. The final frame of the transaction has commit-flag set to the new total page count of the database. Readers ignore any frames after the last commit frame they trust — those are partial, possibly torn writes. 

The **chained checksum** takes the previous frame's checksum as input, so any corruption breaks the chain at the point of damage and everything after is rejected. The checksum is a fast custom function (not CRC) tuned to be cheap on the 4 KB+24-byte payload. 

## The wal-index (Shared Memory)

A small shared-memory region that lets multiple processes coordinate without lock storms.

The wal-index lives at `filename-shm`. It is mmap'd shared memory between all processes and threads with the database open. It contains **no durable data**— if every connection closes, the file is removed. If a process crashes, the next connection rebuilds it by reading the WAL. 

The index has two parts. The first is the **header**: a small struct holding the current valid frame range, salts (matching the WAL header), and three sets of marks: **read marks** (up to 5 slots, each holding a frame number that a reader has pinned), the **writer mark** (one slot indicating the writer's current frame position), and the **backfill mark** (the highest WAL frame that has been checkpointed back to the database). 

The second part is a **chained hash table**: an open-addressed hash from page number to the last frame in the WAL containing that page. Each block of the hash table covers 4096 frames (configurable based on page size); when the WAL grows past that, a new block is appended. A reader looking up "what's the latest version of page 42?" hashes 42, walks the chain, and gets back the frame number — O(1) average. 

Crucially, the wal-index uses **byte-range locks** on its own bytes (the SQLite "wal-locking protocol") rather than database-wide locks. Different lock bytes correspond to: each read mark, the writer mark, the checkpoint operation, the recover operation. Writers, readers, and checkpointers grab only the locks they need, and they conflict only when truly necessary. 

## Reader Protocol: Pinning a Snapshot

How a reader gets a consistent view without blocking the writer.

When a reader begins (the first read in a transaction), the protocol is: 

1. Read the wal-index header to learn the current valid frame range.
2. Pick a read mark slot. The reader claims it by writing the current "max frame in WAL" value into a free slot, or reuses a slot whose mark equals what the reader wants.
3. Take a SHARED lock on that read mark's lock byte. This pins the slot — checkpoints will not advance the backfill past it.
4. Re-check the wal-index header. If it changed, retry. If still consistent, the reader's snapshot is "all frames up to mark M, plus the original main database for any page not in those frames."

To resolve "give me page P", the reader queries the hash table: is there a frame ≤ M that contains page P? If yes, read from that frame in the WAL. If no, read page P from the main database file directly. Both paths are lockless during steady reads — only during begin/commit are wal-index locks taken. 

Because the read mark is a SHARED lock, multiple readers can pin the same slot. The writer can advance freely past that mark; only the checkpointer must wait for the slot to release before it can backfill frames protected by it. 

## Writer Protocol: Appending Frames

A single writer at a time, but it never blocks readers.

A writer's begin-transaction sequence: 

1. Take an EXCLUSIVE lock on the WRITE lock byte of the wal-index. This is the single-writer constraint — if another writer holds it, return SQLITE\_BUSY (or wait, depending on busy\_timeout).
2. Read the wal-index header to learn the current end-of-WAL frame number.
3. Modify pages in memory (the per-connection page cache). No I/O yet.
4. On COMMIT: append modified pages to the WAL as frames. The last frame has its commit-flag set to the new total page count.
5. fsync the WAL (controlled by the synchronous PRAGMA: NORMAL = one fsync per commit, FULL = additional sync after the header).
6. Update the wal-index header with the new "max frame" value.
7. Update the hash table: for each page written, record (page → new frame number).
8. Release the WRITE lock.

Only step 5 is a syscall to disk. Steps 6-7 are atomic memory writes coordinated by the wal-index lock; readers that begin after step 6 see the new frames, readers that began before don't. 

The default `synchronous=NORMAL` in WAL mode does one fsync per commit (the WAL append) and skips fsync of the wal-index header. The justification: if the WAL is durable, the wal-index can always be rebuilt by reading the WAL on next open. The window where you'd lose data is essentially nil. 

## The Walk-Through: Reader1, Writer, Reader2, Checkpoint

A step-by-step trace of the protocol under contention. This is the example to internalize.

Set the stage: a freshly-checkpointed database. WAL has just had its header rewritten; no frames exist yet. Backfill mark = 0, max frame = 0\. 

T1

Reader1 begins.

Reads wal-index header: max frame = 0\. Claims read mark slot 0 with value 0 ("see main db only, no WAL frames"). Acquires SHARED on slot 0's lock byte. Reader1's snapshot: the main database file, untouched. 

T2

Reader1 reads page 42.

Hash table: no frames cover page 42\. Read directly from main.db page 42\. Returns the value, say `v_old`. 

T3

Writer begins, modifies page 42 to v\_new.

Acquires WRITE lock on wal-index. Builds new page 42 in cache. Reads wal-index header: max frame = 0\. 

T4

Writer commits.

Appends frame 1 to WAL: page 42, commit-flag = N (the new db page count). fsyncs the WAL. Updates wal-index header: max frame = 1\. Inserts (page 42 → frame 1) into the hash table. Releases WRITE lock. 

T5

Reader1 reads page 42 again.

Reader1's read mark is still 0 — its snapshot ignores frames after mark 0\. Hash table lookup: yes, frame 1 covers page 42\. But frame 1 > mark 0, so Reader1 ignores it. Reads main.db page 42\. Returns `v_old`. **Snapshot isolation preserved.** 

T6

Reader2 begins.

Reads wal-index header: max frame = 1\. Claims read mark slot 1 with value 1\. Acquires SHARED on slot 1\. 

T7

Reader2 reads page 42.

Hash table: frame 1 covers page 42, and frame 1 ≤ mark 1\. Read from WAL frame 1\. Returns `v_new`. Reader1 still sees `v_old`; Reader2 sees `v_new`. Both consistent with their respective snapshots. 

T8

Auto-checkpoint fires (PASSIVE).

The checkpointer scans the wal-index. It wants to backfill frames 1..N to the main database. It checks read marks: slot 0 holds value 0, slot 1 holds value 1\. The minimum is 0\. **It cannot advance backfill past frame 0** — Reader1 still depends on the pre-frame-1 state of the main database. PASSIVE checkpoint does nothing this round and returns SQLITE\_BUSY\_RECOVERY. 

T9

Reader1 commits and closes.

Reader1 releases SHARED on slot 0\. Slot 0 is now available for reuse. 

T10

Auto-checkpoint fires again.

Read marks: only slot 1 = 1\. Minimum is 1\. Checkpoint can backfill frames ≤ 1 into the main database. It writes frame 1's payload (new page 42) to main.db, fsyncs main.db, updates the backfill mark to 1\. The WAL is not yet truncated — future readers can still find frame 1 if they began before the backfill. 

T11

Reader2 reads page 42 again.

Reader2's read mark is still 1\. Hash table still says frame 1 covers page 42\. Reader2 reads from frame 1 — this is critical: **Reader2 must continue to see frame 1 even though main.db now also has v\_new**, because the hash table is the source of truth for "which frame holds the latest committed value at mark M". Reader2 returns `v_new` (consistent — same as before). 

T12

Reader2 closes. New writer commits frame 2.

All read marks released. WAL position can now be reset. The next writer's commit triggers (if FULL/RESTART) the WAL position reset: the writer reads the WAL header, sees backfill mark = 1 = max frame = 1, decides this WAL is fully drained, rewrites the WAL header with new salts, and starts appending frame 2 at file offset 32\. The WAL file does not shrink (PASSIVE/FULL/RESTART) — only TRUNCATE shrinks it. 

The two key invariants this trace enforces: (a) a reader's snapshot, defined by its read mark, never changes during its transaction, and (b) the checkpointer can never overwrite a page in main.db with a value newer than what any active reader is allowed to see. Both are enforced by SHARED locks on the read mark bytes. 

## Checkpoint Modes: PASSIVE, FULL, RESTART, TRUNCATE

Each mode trades off latency, concurrency, and disk usage differently.

**PASSIVE** — the default for the auto-checkpoint. Backfills frames up to the lowest active read mark and updates the backfill mark. If a reader is holding an old mark, PASSIVE cannot make progress — it does nothing and returns. PASSIVE never blocks readers or the writer. Lowest impact, no guarantees. 

**FULL** — waits for all readers to release before backfilling the entire WAL. After FULL, backfill mark = max frame. The WAL file size doesn't change, but the next writer can start over at frame 1 (overwriting). Useful when you want to make sure everything is durable in main.db (for example, before a backup). 

**RESTART** — FULL plus: also waits for the writer to release, then resets the wal-index so the next writer starts at frame 1 immediately. The WAL file stays the same physical size (it's reused). Useful when you want subsequent reads to avoid the WAL entirely. 

**TRUNCATE** — RESTART plus: shrinks the WAL file to zero bytes. The header is gone, will be rewritten on next write. This actually returns disk to the file system. Use it when you want to reclaim space — for example after a large bulk load. `PRAGMA wal_checkpoint(TRUNCATE)` is the explicit invocation. 

When to call which

Auto-checkpoint runs PASSIVE. For routine ops, leave it alone. Before a backup or before closing a long-lived process, call `PRAGMA wal_checkpoint(FULL)`to ensure main.db is current. To bound disk usage in long-running processes, run `PRAGMA wal_checkpoint(TRUNCATE)` on a timer (every minute, or after every bulk operation). Never call FULL/RESTART/TRUNCATE in a hot path — they wait for readers, which can mean unbounded latency. 

## The wal\_autocheckpoint Knob

When does SQLite decide to checkpoint on its own?

The default is `PRAGMA wal_autocheckpoint = 1000`: when a commit completes and the WAL has grown to 1000 frames or more, the committing connection runs a PASSIVE checkpoint synchronously before returning to the application. At 4 KB pages this means a checkpoint every \~4 MB of WAL. 

Lower this for memory-bound systems: a smaller WAL means smaller wal-index hash tables and less RAM. Raise it for SSD systems with high write rates: a larger WAL accumulates more writes per checkpoint, amortizing the main.db fsync cost. For batch loads, set it to 0 (disable autocheckpoint) and call `wal_checkpoint(TRUNCATE)` manually at the end. 

Be aware: the autocheckpoint runs in the writer's connection, on the commit path. It is synchronous from that connection's view. If a checkpoint is slow (because main.db is on slow storage or because there's a lot to backfill), commits get slower. Long writers pay the cost; readers don't. 

For more control, register a `wal_hook` via `sqlite3_wal_hook()`. The callback fires on every commit with the current WAL frame count and decides whether to trigger a checkpoint. Custom hooks are how you implement: throttle-based checkpointing, time-based checkpointing, or external coordination (e.g. only checkpoint when no reader is in a critical section). 

## journal\_size\_limit and File Reuse

Why your WAL file might still be huge after a checkpoint.

A PASSIVE or FULL checkpoint backfills frames into main.db but does not shrink the WAL file. The next writer reuses the file by rewriting frames from offset 32 onwards. That's fast — no allocation, no truncation, no fsync of file size — but it means a WAL that briefly grew to 1 GB will stay 1 GB on disk forever. 

`PRAGMA journal_size_limit = N` changes that. When set, a checkpoint that finds the WAL larger than N bytes will TRUNCATE it down to N (or to the size needed for the current valid frames, whichever is larger). The default is -1 (unlimited). 

Recommended values: 64 MB to 256 MB for typical applications. Set it once after open: `PRAGMA journal_size_limit = 67108864;`. The next checkpoint will truncate if needed; subsequent checkpoints keep the size bounded. 

## The wal2 Mode

An experimental two-WAL design that improves writer throughput.

Standard WAL has a fundamental limit: while a checkpoint is running, the writer must keep appending to the same WAL file. Frames written during the checkpoint cannot be backfilled until the checkpoint completes, so they accumulate. Eventually the WAL grows faster than the checkpoint can drain it, and writers stall. 

**wal2** is a research-branch SQLite mode that uses two WAL files, `filename-wal` and `filename-wal2`. Writers append to one while a checkpoint drains the other; the roles flip when the active WAL exceeds a threshold. This eliminates the writer-stalls-during-checkpoint case at the cost of a slightly more complex protocol and double the disk space for the log. 

As of writing, wal2 is not in mainline SQLite — it lives in the [wal2 branch](https://www.sqlite.org/cgi/src/timeline?r=wal2)and is used in some downstream forks (notably the LumoSQL project). If you have a write-heavy workload where the checkpoint can't keep up, wal2 is worth evaluating; otherwise standard WAL is the more conservative choice. 

## Operational Pitfalls and How to Avoid Them

Things that bite people in production.

**Long-running readers pin the WAL.** Any read transaction that lives for minutes (think: an analytics query, an ORM session a developer forgot to close) prevents the checkpointer from advancing. The WAL grows unbounded. Diagnostic: `PRAGMA wal_checkpoint;` returns three numbers — busy flag, WAL frame count, backfilled count. If busy=1 persistently, a reader is the cause. 

**Network file systems and the -shm file.** WAL mode requires a working shared-memory file. On NFS, SMB, or various cloud storage layers, the mmap of -shm may not provide cross-host coherence. Symptom: corruption, lost writes, "database disk image is malformed." Solution: don't run WAL on NFS, or pick a SQLite-aware proxy (LiteFS) that handles this correctly. 

**Forking with an open connection.** A child process that inherits an open SQLite handle and writes through it will corrupt the wal-index. Always close connections before `fork()`, reopen in the child. 

**WAL after restore.** If you copy the database file but not the WAL, you've copied the pre-checkpoint state — the WAL might have committed transactions that haven't been backfilled yet. Always run `PRAGMA wal_checkpoint(TRUNCATE)`before file-level backups, or use the SQLite Online Backup API which handles this correctly. 

**synchronous setting.** The default in WAL mode is NORMAL. This is durable to operating-system crashes but not necessarily to power loss on storage with volatile write caches. For systems where durability across power loss matters (financial transactions, etc.), set `synchronous=FULL` — but expect roughly a 2x reduction in commit throughput. 

## Frequently Asked Questions

When should I use WAL mode vs the rollback journal? 

Almost always WAL. Set \`PRAGMA journal\_mode=WAL\` once, and reads stop blocking writes and writes stop blocking reads. The exceptions: if your database is on a network file system (NFS, SMB) the shared-memory file required by WAL may not work correctly — fall back to rollback journal or use \`journal\_mode=PERSIST\`. If you literally never have concurrent readers and writers (e.g. a write-only batch job), rollback journal is slightly simpler.

How do I tune wal\_autocheckpoint? 

The default is 1000 pages, which at the default 4 KB page size means a checkpoint runs after roughly 4 MB of WAL accumulates. For mostly-read workloads this is fine. For write-heavy workloads, raising it (say to 10000 pages = 40 MB) reduces checkpoint frequency and lets writers commit faster, at the cost of larger WAL files and slower recovery on crash. For mixed workloads with long readers, consider lowering it so writers don't accumulate WAL faster than checkpoints can drain it.

What does PASSIVE vs FULL vs RESTART vs TRUNCATE actually mean? 

PASSIVE writes as much WAL as it can without disturbing readers — if a reader is holding an old snapshot, the corresponding frames stay. FULL waits for all readers to release before checkpointing, so it can write the entire WAL back. RESTART is FULL plus it waits for the writer to release the lock and resets the WAL position to the beginning (the file stays the same size, just gets reused). TRUNCATE is RESTART plus it shrinks the WAL file to zero. PASSIVE is the default for the auto-checkpoint.

Why does my WAL file keep growing? 

Three usual causes: (1) a reader is holding an old transaction open, pinning early frames so the checkpoint cannot reclaim space — common with ORM session pools that forget to release. (2) Checkpoints can't keep up with write rate — bump \`wal\_autocheckpoint\` lower or run \`PRAGMA wal\_checkpoint(TRUNCATE)\` periodically. (3) \`journal\_size\_limit\` is unset and the OS is happy to keep allocating space. Set \`PRAGMA journal\_size\_limit = 67108864\` (64 MB) and SQLite will TRUNCATE the WAL after each checkpoint when it's bigger than the limit.

Can I have two writers in WAL mode? 

No. WAL allows multiple concurrent readers and one writer. If a second writer tries to begin, it gets SQLITE\_BUSY. The win of WAL is that the writer no longer blocks readers — that's the only concurrency change. For more writers you need to serialize at the application level (single-writer process, queue) or move to Postgres. There is an experimental \`wal2\` mode in a research branch that uses two WAL files and improves writer throughput in specific scenarios, but it is not in mainline SQLite as of writing.

What is the wal-index file and can I delete it? 

The \`-shm\` file is the wal-index — a memory-mapped shared-memory region that connections use to coordinate. It does not hold durable data: if all connections close cleanly, SQLite removes it. If your process crashes, the next connection rebuilds it from the WAL. So yes, you can delete \`-shm\` when no process has the database open. Never delete it while a connection is active — readers and writers will lose their place in the WAL.

Does WAL hurt performance for big transactions? 

Sometimes, yes. A transaction that touches 100 MB of data writes 100 MB to the WAL. If the WAL must then be checkpointed back to the main database, that's another 100 MB of writes. Total amplification: \~2x for the write path. Compare to rollback journal: original pages copied to the journal first (write 1), then modifications written to the database (write 2) — also \~2x. For very large single transactions, both modes pay similar costs. WAL wins when you have many small transactions interleaved with reads.

What's the wal\_hook callback? 

\`sqlite3\_wal\_hook()\` registers a C callback invoked after every commit that lands frames in the WAL. The callback receives the current page count of the WAL and can decide to trigger a checkpoint synchronously. The default behavior — auto-checkpoint at 1000 pages — is implemented this way. Custom hooks are useful for: throttling background checkpoints, logging WAL growth for monitoring, or implementing a custom backup strategy that flushes after every commit.

## 🔗 Related Topics

[ SQLite Internals (Hub) File format, B-trees, virtual tables, FTS5, JSON1 → ](/sqlite/)[ PostgreSQL WAL Compare with Postgres's WAL — different goals, different design → ](/postgresql/wal/)[ DuckDB Storage Format Row groups and columnar segments — a different durability model → ](/duckdb/storage-format/)[ Atomic Commit Protocol The rollback journal — what WAL replaced → ](/sqlite/atomic-commit/)[ B-Tree Indexes How B-trees work generally → ](/postgresql/btree-indexes/) 

### 📬 Get notified when we publish new visualizations

Subscribe 

[𝕏 Twitter](https://twitter.com/systemsexplain) [▶ YouTube](https://youtube.com/@systeminternals) [⌨ GitHub](https://github.com/systeminternals) 

Built by engineers, for engineers.

© 2026 Systems Explained