SQLite implements write-ahead logging (WAL) by inverting the traditional rollback-journal approach: instead of copying original pages to a journal before modifying the database in place, it keeps the original content in the database file and appends new (modified) page images into a separate `*-wal` file. [1][3] A commit is recorded when a special commit frame is appended to that log, so readers can continue reading the unaltered main database while writes proceed concurrently. [1][3] Periodically, a *checkpoint* operation copies committed frames back into the main database, and a shared-memory hash table (the *wal-index*, stored in a `*-shm` file) lets readers quickly locate the latest version of any page without scanning the entire log. [1][2]

## The Three Files on Disk

When a WAL-mode database is in active use, its state is described by three files: the main database file (arbitrary name, e.g. `mydb`), the write-ahead log file (`mydb-wal`), and the wal-index file (`mydb-shm`). [2] The main database file uses the standard SQLite file format; its format-version bytes (offsets 18 and 19) are set to 2 to indicate WAL mode, which prevents pre-3.7.0 SQLite from attempting to open it. [1][2] The wal file records transactions that have been committed but not yet applied to the main database. [2] The shm file is memory-mapped and serves as shared coordination space; it is never fsync-ed to disk and is deleted when the last connection closes cleanly. [2]

## The WAL File Format

The WAL file opens with a 32-byte header containing a magic number (0x377f0682 little-endian or 0x377f0683 big-endian), the file-format version (3007000), the database page size, a checkpoint sequence number, two random salt values regenerated each checkpoint, and an 8-byte chained checksum over the first 24 bytes. [4] After the header, the file is a stream of identically-formatted frames: each frame has a 24-byte header (page number, a commit-flag that equals the total database page count for the last frame of a transaction, the two salt values, and an 8-byte checksum) followed by the full page image. [4] A frame with a non-zero value in its commit-flag bytes marks the end of a transaction. [2] The WAL file format is precisely defined and cross-platform. [1][3]

## The Wal-Index (Shared-Memory File)

The shm file is implemented as an ordinary file that is memory-mapped, rather than using anonymous shared memory, to guarantee that all processes accessing the same database (including those in different chroots) see the same memory region. [1][3] Its first 136 bytes form a header with two redundant copies of the WAL-index information (version, change counter, init flag, page size, mxFrame, nPage, checksums, salts) followed by checkpoint information (nBackfill, five 32-bit read-mark values, and eight bytes reserved for file locks) and an nBackfillAttempted counter. [2]

Beyond the header, the shm file contains one or more 32768-byte hash-table units. Each unit holds a `u32 aPgno` array (or 4096 in subsequent units) and a `u16 aHash` array. [2] The hash function maps a page number P to `h = (P * 383) % 8192`, and the aHash array supports an open-addressing lookup that finds all candidate aPgno slots for a given page in roughly O(1) average time. [2] The core query the hash tables answer is **FindFrame(P, M)**: given a page number P and a maximum frame index M, return the largest WAL frame index for page P that does not exceed M. [2] The shm file only grows beyond a single 32768-byte unit when the WAL exceeds about 4079 frames; with the default 1000-page auto-checkpoint, this rarely happens. [2]

## How WAL Works: Writes, Reads, and Checkpoints

The traditional rollback journal writes original page copies to a journal, modifies the database in place, and commits by deleting the journal. [1][3] WAL inverts this: original content stays in the database file, and changes are appended to the WAL. [1][3] A COMMIT occurs when a special record (a frame whose commit-flag equals the new total page count) is appended to the WAL, so a commit can happen without ever writing to the original database. [1][3] Multiple transactions can be appended to a single WAL file. [1][3]

**Write path.** A writer acquires an exclusive WAL_WRITE_LOCK, appends modified pages as frames to the end of the WAL, fsyncs the WAL (if `PRAGMA synchronous = FULL`; a single fsync with `NORMAL`), updates the wal-index header's mxFrame, and inserts new (page → frame) entries into the hash table. [4][2] Writers do nothing that interferes with readers, so reads and writes proceed concurrently; however, only one writer may exist at a time because there is a single WAL file. [1][3]

**Read path.** When a read transaction begins, the reader reads the current mxFrame from the wal-index header and claims one of five read-mark slots, recording that value as its "end mark." [1][2][3] For each page it needs, the reader consults the wal-index hash table: if a frame for that page exists at an index ≤ the reader's end mark, the reader pulls that frame from the WAL file; otherwise it reads the page from the main database file. [1][3] Because the end mark is fixed for the duration of the read transaction, each reader sees a consistent snapshot. [1][3]

**Checkpoint.** A checkpoint transfers content from the WAL file back into the original database file, writing pages in ascending page-number order. [1][3] It must stop when it reaches a frame past any current reader's end mark, because writing beyond that point would overwrite content the reader still needs from the main database. [1][3] The checkpoint remembers how far it got (in the nBackfill field of the wal-index) and resumes on the next invocation. [1][3] The WAL must be fsynced before its content is copied into the database, and the database must be fsynced before the WAL is reset. [1][3] With `PRAGMA synchronous = NORMAL`, the checkpoint is the only operation that issues a sync call; in this configuration individual write commits skip their own sync, trading strict power-loss durability for much higher throughput. [1][3]

## Concurrency and Locking Protocol

Access is coordinated using both the legacy lock-byte page on the main database file and WAL-specific locks in the shm file. [2] All connections hold a continuous `SQLITE_LOCK_SHARED` on the main database file while attached to a WAL-mode database (unlike rollback mode, where the shared lock is released at transaction end). [2] An exclusive lock on the main database file is required to transition into or out of WAL mode, or to delete the WAL and shm files on last-connection close. [2]

Within the wal-index, eight dedicated lock bytes (accessed via `xShmLock`) are defined: WAL_WRITE_LOCK (offset 120), WAL_CKPT_LOCK (121), WAL_RECOVER_LOCK (122), and five read locks WAL_READ_LOCK(0) through WAL_READ_LOCK(4) (offsets 123–127). [2] Key rules:

- **WAL_WRITE_LOCK** is held exclusively by any connection appending frames to the WAL; only one writer can do so at a time. [2]
- **WAL_CKPT_LOCK** is held exclusively by any connection running a checkpoint; it may increase nBackfill but never decrease it (nBackfill is reset to zero only during a WAL reset, under WAL_WRITE_LOCK). [2]
- **WAL_READ_LOCK(N)** may be held in shared or exclusive mode. A shared lock on read lock N is a promise that the connection will read pages from the WAL only for frames ≤ read-mark[N]. A shared lock on WAL_READ_LOCK(0) means the connection will ignore the WAL entirely and read only from the main database. [2]
- A checkpoint that sees a lock on WAL_READ_LOCK(N) must not move WAL content into the main database beyond the first read-mark[N] frames. [2]
- A WAL reset (rewinding the file to frame 1) requires no locks on WAL_READ_LOCK(1) through WAL_READ_LOCK(4); connections holding WAL_READ_LOCK(0) are safe because they have promised not to read from the WAL. [2]

Because shared memory is required, all processes accessing the database must be on the same host; WAL does not work over a network filesystem. [1][3]

## Checkpoint Modes and Configuration

WAL mode is activated with `PRAGMA journal_mode=WAL;` and is persistent: unlike other journal modes, the setting is stored in the database header, so a reopened database comes back in WAL mode. [1][3] To leave WAL mode, all but one connection must be closed, and the remaining connection must obtain an exclusive lock. [2]

By default, SQLite automatically runs a **PASSIVE** checkpoint whenever a COMMIT causes the WAL to reach 1000 pages (≈ 4 MB at the default 4 KB page size). [1][3][4] Applications can change the threshold with `PRAGMA wal_autocheckpoint = N` (0 disables it), force a checkpoint with `PRAGMA wal_checkpoint` or `sqlite3_wal_checkpoint()`, or register a `sqlite3_wal_hook()` callback for custom checkpoint policy. [1][3][4] There are four checkpoint modes of increasing aggressiveness:

- **PASSIVE** – backfills as many frames as possible without disturbing active readers; if a reader holds an old mark, it simply returns without completing. This is the default for auto-checkpoint. [1][3][4]
- **FULL** – waits for all readers to release before backfilling the entire WAL. [3][4]
- **RESTART** – FULL plus it resets the WAL position so the next writer begins at frame 1; the file stays the same physical size. [3][4]
- **TRUNCATE** – RESTART plus it shrinks the WAL file to zero, actually returning disk space. [3][4]

A trade-off exists: frequent checkpoints keep the WAL small and reads fast, while infrequent checkpoints let writes amortize checkpoint cost. [1][3] The `PRAGMA journal_size_limit = N` setting causes a checkpoint to truncate the WAL file to N bytes when it exceeds that size, preventing unbounded growth on disk. [4]

## Recovery

Recovery is the process of rebuilding the wal-index to match the WAL file, and it is run by the first thread to connect to a WAL-mode database. [2] Recovery does a single pass over the WAL from beginning to end, verifying the chained checksum on each frame. The scan stops at the first invalid checksum or at end-of-file. The mxFrame field is set to the index of the last valid commit frame, and nBackfill is initialized to zero. [2] During recovery of the global shared wal-index, all WAL-index locks except WAL_READ_LOCK(0) are held exclusively, preventing other threads from reading or writing until recovery is complete. [2] If the shm file is read-only (e.g., the connecting process lacks write permission), the first client creates a private heap-memory wal-index instead, runs the same recovery, and holds the results privately. [2]

## Performance Characteristics

Write transactions in WAL mode are fast because each modified page is written exactly once (to the WAL) rather than twice (once to the journal, once to the database) as in rollback-journal mode, and the writes are sequential appends. [1][3] Read performance degrades as the WAL grows because each page lookup still requires a wal-index hash-table probe; keeping the WAL small via regular checkpoints mitigates this. [1][3] WAL is roughly 1–2 % slower than rollback journal for read-dominated, write-rare workloads, and it uses fewer fsync calls overall. [1][3]

## Operational Pitfalls

- **Long-running readers pin the WAL.** A checkpoint cannot advance past the lowest active read-mark, so a reader that stays open for minutes prevents the WAL from being reset and causes unbounded growth. [1][3][4] Diagnosing: `PRAGMA wal_checkpoint;` returns (busy, total_frames, backfilled_frames); a persistently non-zero `busy` flag indicates a blocking reader. [4]
- **Disabling the auto-checkpoint** removes the only mechanism that reclaims WAL space. [1][3]
- **Checkpoint starvation** occurs when there is always at least one active reader; the checkpoint can never complete. [1][3]
- **Network filesystems** (NFS, SMB) do not provide the cross-process coherence needed for the mmap'd shm file, leading to corruption. [3][4]
- **Forking with an open connection** corrupts the wal-index; connections must be closed before `fork()`. [4]
- **Copying the database without its WAL** loses committed-but-not-checkpointed transactions; run `PRAGMA wal_checkpoint(TRUNCATE)` before a file-level backup, or use the SQLite Online Backup API. [4]

## WAL Without Shared Memory

Beginning with SQLite 3.7.4, if `PRAGMA locking_mode=EXCLUSIVE` is set before the first access, no shm file is created and a private heap-memory wal-index is used instead. [1][3][8-variant in sources] This allows single-process or single-thread use on legacy VFSes that lack the `xShmMap`, `xShmLock`, `xShmBarrier`, and `xShmUnmap` methods. [1][3] The locking mode is then stuck at EXCLUSIVE for the lifetime of the WAL-mode connection; the only way to change it is to first switch out of WAL journal mode. [1][3]

## The WAL-Reset Bug (2026)

A data-race bug, present from 3.7.0 through 3.51.2 (2026-01-09) and fixed in 3.51.3 (2026-03-13), could corrupt the database under a very specific sequence: two checkpoints racing with a WAL reset triggered by a concurrent commit. [1] The developers could not reproduce the bug organically and had to insert special test-control code to trigger it. [1] In August 2026, Phil Eaton published an independent reproducer that does not rely on the test-control hack. [1] The bug affects only databases in WAL mode with two or more connections in separate threads or processes that write or checkpoint at the same instant. [1]

## Sources

[1] 1\. Overview — https://www.sqlite.org/wal.html

[2] 1\. Files On Disk — https://www.sqlite.org/walformat.html

[3] 1\. Overview — https://www3.sqlite.org/matrix/wal.html

[4] SQLite Write-Ahead Logging — https://systeminternals.dev/sqlite/wal/
