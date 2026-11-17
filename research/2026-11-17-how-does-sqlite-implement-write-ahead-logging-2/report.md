# How SQLite Implements Write-Ahead Logging

SQLite implements write-ahead logging (WAL) by appending committed page changes to a separate `-wal` file rather than overwriting the main database in place, and by periodically "checkpointing" those frames back into the database file [1][3][4]. The mode was introduced in version 3.7.0 (2010-07-21) and is activated with `PRAGMA journal_mode=WAL;`, after which the setting is stored persistently in the database file header [1][5]. The core design trades an extra append-only log file and a shared-memory index for far better concurrency: readers never block writers and writers never block readers, while a single serialized writer is still the only one that can commit at a time [1][4][6].

## The Three Files on Disk

An active WAL-mode database is described by three files: the main database file (e.g. `app.db`), the write-ahead log file (e.g. `app.db-wal`), and the wal-index or shared-memory file (e.g. `app.db-shm`) [2][4]. The main database file holds the base state as standard B-tree pages and is **never modified during an active write transaction**; it is only updated during checkpointing [4][11]. The `-wal` file is an append-only log containing the revised versions of modified pages; its name is the database filename with a `-wal` suffix [1][2][4]. The `-shm` file is a volatile, memory-mapped index that maps database page numbers to their corresponding frame offsets in the WAL, so readers do not have to scan the entire log sequentially [2][4][9].

The main database file's format version numbers (bytes 18 and 19 in the header) are set to 2 in WAL mode, preventing older SQLite versions (pre-3.7.0) from mistakenly trying to recover a WAL-mode database [1][2].

## How WAL Works: The Write Path

In the traditional rollback-journal approach, SQLite copies original pages into a journal file and then writes changes directly into the database file; a commit occurs when the journal is deleted [1][3]. WAL inverts this: the original content stays in the database file, and new page versions are **appended** to the WAL file [1][3][11]. A commit occurs when a special record—a frame whose commit-flag field is set to the database's new page count—is appended to the WAL [1][10][11]. Because the database file is never touched during a write, readers can continue operating from it while changes are simultaneously committed into the WAL [1][3].

The source-code primitive `walWriteOneFrame` encodes each dirty page as a frame (a 24-byte header plus the full page image) and appends it to the `-wal` file; the `nTruncate` argument is 0 for ordinary frames and is set to the database size in pages on the final frame of a transaction, which serves as the commit marker [11][12]. Only one writer is permitted at a time, enforced by the `WAL_WRITE_LOCK` in the wal-index [2][8].

## The WAL File Format

A WAL file opens with a 32-byte header containing: a magic number (0x377f0682 or 0x377f0683), the file format version (3007000), the database page size, a checkpoint sequence number, two salt values (random, regenerated each checkpoint), and an 8-byte checksum [8]. After the header, the file is a sequence of frames, each consisting of a 24-byte frame header (page number, commit flag, salt values, and a chained checksum) followed by the full page data [8][10][12].

Recovery works by performing a single pass over the WAL from beginning to end, verifying checksums on each frame; the scan stops at the first invalid checksum or end of file, and the `mxFrame` field in the wal-index is set to the index of the last valid commit frame [2][8].

## The Wal-Index (Shared Memory) and Snapshot Isolation

The wal-index is maintained in shared memory (typically via `mmap` of the `-shm` file) and serves two purposes: it coordinates concurrent access through byte-range locks, and it provides a hash table so readers can locate the latest version of a page without scanning the entire WAL [1][2][4][8]. The hash table is organized in 32,768-byte units, each containing a 136-byte header, a `u32 aPgno` array, and a `u16 aHash` array [2]. The `FindFrame(P, M)` function returns the largest WAL frame index for page P that does not exceed M, or NULL if none exists [2][8].

The wal-index uses native CPU byte order (not big-endian like the main database and WAL files), enabling zero-cost dereferencing [2][4]. It is volatile and transient: if the machine crashes or the file is deleted, it is automatically reconstructed by reading the WAL on the next connection [2][4][8].

When a reader begins a transaction, it reads the current `mxFrame` value (the "end mark") from the wal-index and pins it; for the duration of that transaction the end mark is unchanged, guaranteeing the reader sees a consistent snapshot [1][3][4][8]. Because readers do not need to write to the database file or to the WAL, they do not block the writer, and the writer does not block them [1][4][7].

### Locking Protocol

Access is coordinated using both the legacy DELETE-mode locks (stored on the lock-byte page of the main database file) and WAL locks controlled by `xShmLock()` on the `-shm` file [2]. The eight WAL-index locks are: `WAL_WRITE_LOCK` (offset 0), `WAL_CKPT_LOCK` (offset 1), `WAL_RECOVER_LOCK` (offset 2), and five `WAL_READ_LOCK(i)` slots (offsets 3–7) [2][12]. During recovery, all locks except `WAL_READ_LOCK(0)` are held exclusively to prevent other threads from reading or writing until recovery completes [2].

## Checkpointing

A checkpoint transfers content from the WAL file back into the original database file [1][3][11]. It can run concurrently with readers, but must stop when it reaches a frame past the end mark of any current reader, to avoid overwriting a page that a reader is actively using [1][3][11]. The checkpointer records its progress in the wal-index (`nBackfill` field) and resumes from where it left off on the next invocation [1][2][11].

By default, SQLite performs a checkpoint automatically when the WAL reaches 1000 pages (about 4 MB at the default 4 KB page size) [1][3][5][8]. The checkpoint is run by the same thread that performs the COMMIT that pushes the WAL over the threshold, making most commits fast but the occasional triggering commit much slower [1][3]. Applications can adjust the threshold with `PRAGMA wal_autocheckpoint=N`, or disable automatic checkpointing (set to 0) and run checkpoints in a separate thread or process [1][3][8].

Checkpoint modes: **PASSIVE** (default for auto-checkpoint) writes as much as it can without disturbing readers; **FULL** waits for all readers to release; **RESTART** is FULL plus resetting the WAL position to frame 1; **TRUNCATE** is RESTART plus shrinking the WAL file to zero bytes [8].

Checkpointing requires `fsync` operations on both the WAL and the database file, and involves many seek operations, making it slower than the write transactions themselves [1][3]. When the last connection to a database closes, it performs a final checkpoint and then deletes the `-wal` and `-shm` files [1][3].

## Activation, Configuration, and Persistence

WAL mode is enabled with `PRAGMA journal_mode=WAL;` [1][3][5][7]. Unlike other journal modes, this setting is **persistent**: it is stored in the database file, so a new connection to the same file automatically opens in WAL mode [1][3][5][7]. To leave WAL mode, an application runs `PRAGMA journal_mode=DELETE;`, which resets the file format version numbers back to 1 [1]. If exactly one connection is open, changing the locking mode between NORMAL and EXCLUSIVE is allowed; in EXCLUSIVE locking mode the shared-memory wal-index is never created, and the locking mode is "stuck" until WAL mode is turned off [1][3].

WAL requires that all connections share the same host, because the wal-index uses operating-system shared memory [1][2][7][8]. Consequently, WAL does **not** work on a network filesystem (NFS, SMB, etc.) [1][4][6][7][8].

## Performance Considerations

WAL is significantly faster than the rollback journal in most scenarios because it uses fewer `fsync()` calls and more sequential I/O [1][3]. The default `synchronous=NORMAL` in WAL mode performs one `fsync` per commit (on the WAL append) and skips a second fsync of the wal-index header, because the wal-index can always be rebuilt from the WAL [8].

There is a tradeoff between read and write performance: frequent checkpoints keep the WAL small (better reads) but add overhead to writes; infrequent checkpoints let the WAL grow (better writes) but slow reads [1][3][8]. For write-heavy workloads, raising `wal_autocheckpoint` (e.g. to 10,000 pages) amortizes checkpoint cost over more commits [8]. For batch loads, setting it to 0 and calling `PRAGMA wal_checkpoint(TRUNCATE)` manually at the end is appropriate [8].

Since version 3.11.0 (2016-02-15), WAL mode works as efficiently with large transactions as rollback mode; the WAL file for a single transaction is proportional in size to the transaction, with each page written to the WAL only once [1][3].

## Operational Pitfalls

- **Unbounded WAL growth.** A long-running read transaction pins early frames, preventing the checkpointer from recycling them; the WAL then grows without bound [1][3][7][8]. The fix is to close stuck readers and run `PRAGMA wal_checkpoint(TRUNCATE)` during a quiet moment [7][8].
- **Single-writer constraint.** WAL allows N concurrent readers plus one writer; a second writer receives `SQLITE_BUSY` [1][6][7][8]. Starting write transactions with `BEGIN IMMEDIATE` and keeping them short mitigates `SQLITE_BUSY` errors [7].
- **Network filesystems.** The `-shm` shared-memory mechanism does not function across hosts, so WAL is unsupported on NFS/SMB [2][4][7][8].
- **Backups.** The `-wal` file must be kept with the database; file-level copies that omit the WAL miss committed transactions. Use the SQLite Online Backup API or `VACUUM INTO` instead [4][5][8].

## The WAL-Reset Bug (2026)

On 2026-03-03, a bug was identified that could, in rare cases, lead to database corruption when two or more connections attempt to write or checkpoint at the same instant [1]. The bug was present in all versions from 3.7.0 through 3.51.2 (2026-01-09) and is fixed in version 3.51.3 (2026-03-13) and later, with backports to 3.44.6 and 3.50.7 [1]. It is a data race with tight timing constraints; the developers were unable to reproduce it organically and had to add special testing logic to trigger it [1]. A reproducer not requiring the test-code hack was published in August 2026 [1]. The documented occurrence rate in the wild is comparable to or below the expected rate of SSD malfunctions and cosmic-ray hits [1].

## Summary Mental Model

| Aspect | Rollback Journal (DELETE) | Write-Ahead Log (WAL) |
|---|---|---|
| Write strategy | Overwrite main `.db` in-place after journal copy | Append new frames to `.db-wal` |
| Readers vs. writers | Writers block readers; readers block writers | Readers never block writers; writers never block readers |
| Commit overhead | 2 disk writes + multiple fsyncs | 1 append write + 1 fsync |
| Companion files | Temporary `.db-journal` | Persistent `.db-wal` and `.db-shm` |
| Network FS support | Supported | Unsupported (requires shared OS memory) |
| Concurrency ceiling | 1 active operation | N readers + 1 serialized writer |

[4][6]

## Sources

[1] 1\. Overview — https://www.sqlite.org/wal.html

[2] 1\. Files On Disk — https://www.sqlite.org/walformat.html

[3] 1\. Overview — https://www3.sqlite.org/matrix/wal.html

[4] DEV Community — https://dev.to/syed_anzar/how-sqlite-wal-mode-actually-works-the-3-files-shared-memory-and-lock-free-reads-1j2l

[5] SQLite WAL Mode: How Write-Ahead Logging Works and When to Use It — https://sqldocs.org/sqlite-write-ahead-logging/

[6] SQLite WAL Mode Explained — How It Works, Pros and Cons — https://www.negabaro.com/en/blog/rails/sqlite-wal-mode

[7] SQLite WAL Mode Explained: Settings for Production — https://blog.codercops.com/blog/sqlite-wal-mode-explained-production-settings-2026

[8] SQLite Write-Ahead Logging — https://systeminternals.dev/sqlite/wal/

[9] SQLite Forum — https://www.sqliteforum.com/p/sqlite-wal-internals-frames-commits

[10] SQLite's WAL mode explained — https://sijinjoseph.com/post/2022-05-10-sqlite-wal-mode-explained/

[11] Case Studies — https://patterns.totorojam.com/case-studies/sqlite-wal

[12] Navigation Menu — https://github.com/sqlite/sqlite/blob/master/src/wal.c
