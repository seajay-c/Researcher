---
n: 4
url: https://dev.to/syed_anzar/how-sqlite-wal-mode-actually-works-the-3-files-shared-memory-and-lock-free-reads-1j2l
title: DEV Community
fetched_at: 2026-11-17T06:59:56.118150Z
---

 

[Skip to content](#main-content) 

Navigation menu [ ![DEV Community](https://media2.dev.to/dynamic/image/quality=100/https://dev-to-uploads.s3.amazonaws.com/uploads/logos/resized_logo_UQww2soKuUsjaOGNB38o.png) ](/) 

Search [Powered by Algolia Search ](https://www.algolia.com/developers/?utm%5Fsource=devto&utm%5Fmedium=referral) 

[Log in ](/enter?signup%5Fsubforem=1) [Create account ](/enter?signup%5Fsubforem=1&state=new-user) 

## DEV Community

Close 

![](https://assets.dev.to/assets/heart-plus-active-9ea3b22f2bc311281db911d416166c5f430636e76b15cd5df6b3b841d830eefa.svg) Add reaction 

![](https://assets.dev.to/assets/sparkle-heart-5f9bee3767e18deb1bb725290cb151c25234768a0e9a2bd39370c382d02920cf.svg) Like ![](https://assets.dev.to/assets/multi-unicorn-b44d6f8c23cdd00964192bedc38af3e82463978aa611b4365bd33a0f1f4f3e97.svg) Unicorn ![](https://assets.dev.to/assets/exploding-head-daceb38d627e6ae9b730f36a1e390fca556a4289d5a41abb2c35068ad3e2c4b5.svg) Exploding Head ![](https://assets.dev.to/assets/raised-hands-74b2099fd66a39f2d7eed9305ee0f4553df0eb7b4f11b01b6b1b499973048fe5.svg) Raised Hands ![](https://assets.dev.to/assets/fire-f60e7a582391810302117f987b22a8ef04a2fe0df7e3258a5f49332df1cec71e.svg) Fire 

Jump to Comments Save Boost 

Pick as gem 

More... 

Copy link Copy link 

Copied to Clipboard

[Share to X ](https://twitter.com/intent/tweet?text=%22How%20SQLite%20WAL%20Mode%20Actually%20Works%3A%20The%203%20Files%2C%20Shared%20Memory%2C%20and%20Lock-Free%20Reads%22%20by%20Syed%20Anzar%20%23DEVCommunity%20https%3A%2F%2Fdev.to%2Fsyed%5Fanzar%2Fhow-sqlite-wal-mode-actually-works-the-3-files-shared-memory-and-lock-free-reads-1j2l) [Share to LinkedIn ](https://www.linkedin.com/shareArticle?mini=true&url=https%3A%2F%2Fdev.to%2Fsyed%5Fanzar%2Fhow-sqlite-wal-mode-actually-works-the-3-files-shared-memory-and-lock-free-reads-1j2l&title=How%20SQLite%20WAL%20Mode%20Actually%20Works%3A%20The%203%20Files%2C%20Shared%20Memory%2C%20and%20Lock-Free%20Reads&summary=A%20deep%20dive%20into%20SQLite%20Write-Ahead%20Logging%20%28WAL%29%3A%20how%20.db%2C%20.db-wal%2C%20and%20.db-shm%20coordinate%20concurrent%20reads%2C%20snapshot%20isolation%2C%20and%20checkpointing.&source=DEV%20Community) [Share to Facebook ](https://www.facebook.com/sharer.php?u=https%3A%2F%2Fdev.to%2Fsyed%5Fanzar%2Fhow-sqlite-wal-mode-actually-works-the-3-files-shared-memory-and-lock-free-reads-1j2l) [Share to Mastodon ](https://s2f.kytta.dev/?text=https%3A%2F%2Fdev.to%2Fsyed%5Fanzar%2Fhow-sqlite-wal-mode-actually-works-the-3-files-shared-memory-and-lock-free-reads-1j2l) 

[Share Post via...](#) [Report Abuse](/report-abuse) 

[ ![Cover image for How SQLite WAL Mode Actually Works: The 3 Files, Shared Memory, and Lock-Free Reads](https://media2.dev.to/dynamic/image/width=1000,height=420,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fholy-plume-2vqr.here.now%2Fthumbnail.png) ](https://media2.dev.to/dynamic/image/width=1000,height=420,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fholy-plume-2vqr.here.now%2Fthumbnail.png) 

[![Syed Anzar](https://media2.dev.to/dynamic/image/width=50,height=50,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Fuser%2Fprofile_image%2F4069010%2Fda8f710a-f285-4309-8c69-770badbe9c7b.jpg)](/syed%5Fanzar) 

[Syed Anzar](/syed%5Fanzar) 

Posted on Oct 6 

# How SQLite WAL Mode Actually Works: The 3 Files, Shared Memory, and Lock-Free Reads 

[#sqlite](/t/sqlite) [#database](/t/database) [#programming](/t/programming) [#performance](/t/performance) 

Every developer knows SQLite's default pitch: it is a lightweight, zero-configuration, single-file database engine embedded directly inside your application process.

For years, developers also repeated a persistent criticism: _SQLite cannot handle concurrent access because any write locks the entire database._

If you use SQLite in its default configuration, that criticism is accurate. Under the legacy rollback journal mode, writing a single row acquires an exclusive lock on the database file, blocking every concurrent reader and writer until the transaction commits.

Enable Write-Ahead Logging (`PRAGMA journal_mode = WAL;`), and that locking behavior changes completely. Readers no longer block writers. Writers no longer block readers. A high-throughput web server can process thousands of concurrent read queries while a background worker continuously appends new records.

This concurrency does not happen through background magic. It relies on a coordinated three-file architecture, an in-memory hash table index, and snapshot isolation tracked through raw byte offsets.

Here is what actually happens under the hood when SQLite runs in WAL mode.  

```
+-----------------------------------------------------------------------+
|                         SQLITE 3-FILE ECOSYSTEM                       |
|                                                                       |
|   +--------------------+  +--------------------+  +---------------+   |
|   |    database.db     |  |   database.db-wal  |  |database.db-shm|   |
|   |                    |  |                    |  |               |   |
|   | Base B-Tree pages  |  | Append-only log of |  | Shared memory |   |
|   | (Quiescent during  |  | newly written      |  | index (mmap)  |   |
|   | active writes)     |  | page frames        |  | Hash tables   |   |
|   +--------------------+  +--------------------+  +---------------+   |
|             ^                       ^                     ^           |
|             |                       |                     |           |
|      Base Page Reads         Delta Page Reads       Frame Lookup &    |
|      (Unmodified Pages)     (Committed Updates)     Reader Locks      |
+-----------------------------------------------------------------------+

```

Enter fullscreen mode Exit fullscreen mode 

---

## [ ](#1-the-flaw-in-the-rollback-journal)1\. The Flaw in the Rollback Journal 

To understand why WAL mode exists, you have to look at the mechanism it replaced: the rollback journal.

In rollback journal mode (`journal_mode = DELETE`), SQLite achieves atomicity by writing the original, unmodified pages to a separate journal file _before_ overwriting them in the main `.db` file.  

```
ROLLBACK JOURNAL TRANSACTION LIFECYCLE:
1. Acquire EXCLUSIVE lock on database.db (blocks all readers).
2. Read original Page 42 from database.db.
3. Write original Page 42 to database.db-journal.
4. Overwrite Page 42 in database.db with new data.
5. Commit: Delete or truncate database.db-journal.
6. Release lock.

```

Enter fullscreen mode Exit fullscreen mode 

If the system crashes during step 4, the database on disk is corrupt. When SQLite reopens the file, it reads `database.db-journal`, copies the original pages back into `database.db`, and restores consistency.

This design has two major penalties:

1. **Concurrency bottleneck:** Writing requires modifying the main database file in-place. Readers cannot read from `database.db` while a write is underway without seeing torn or uncommitted pages.
2. **Double write penalty:** Every updated page is written to disk twice: once to the journal file and once to the main database file, with synchronous disk flushes (`fsync`) between steps.

WAL mode reverses this flow entirely.

---

## [ ](#2-the-3file-architecture-raw-db-endraw-raw-dbwal-endraw-and-raw-dbshm-endraw-)2\. The 3-File Architecture: `.db`, `.db-wal`, and `.db-shm` 

When you switch a database to WAL mode, SQLite introduces two companion files in the same directory:  

```
$ ls -l
-rw-r--r--  1 anzar anzar  409600 Oct  6 18:00 app.db
-rw-r--r--  1 anzar anzar   32768 Oct  6 18:00 app.db-shm
-rw-r--r--  1 anzar anzar  131584 Oct  6 18:00 app.db-wal

```

Enter fullscreen mode Exit fullscreen mode 

Each file serves a dedicated purpose:

### [ ](#-raw-appdb-endraw-the-main-database-file) `app.db` (The Main Database File) 

Contains the base database state organized as standard B-Tree pages (typically 4096 bytes each). In WAL mode, this file is **never modified during an active write transaction**. It is only updated during a separate process called checkpointing.

### [ ](#-raw-appdbwal-endraw-the-writeahead-log) `app.db-wal` (The Write-Ahead Log) 

An append-only file containing the revised versions of modified database pages. When a transaction commits, new pages are written sequentially to the end of the WAL file. The main `.db` file remains completely untouched.

### [ ](#-raw-appdbshm-endraw-the-shared-memory-index) `app.db-shm` (The Shared Memory Index) 

A volatile, memory-mapped index (`mmap`) that maps database page numbers to their corresponding frame offsets in the `.db-wal` file. Without this file, readers would have to scan the entire WAL file sequentially on every query.  

```
+-------------------------------------------------------------------------+
|                  LOGICAL VS PHYSICAL TRANSACTION FLOW                   |
|                                                                         |
|  [WRITE TRANSACTION]                                                    |
|         │                                                               |
|         ├─► 1. Append Page 42 & Page 88 to app.db-wal                   |
|         ├─► 2. Update hash table in app.db-shm (Page 42 -> Frame 104)   |
|         └─► 3. Flush WAL to disk (fsync). app.db remains untouched.     |
|                                                                         |
|  [READ TRANSACTION]                                                     |
|         │                                                               |
|         ├─► 1. Read mxFrame snapshot boundary from app.db-shm           |
|         ├─► 2. Check hash table in app.db-shm for Page 42               |
|         ├─► 3. If found in WAL (Frame 104 <= mxFrame): Read from WAL   |
|         └─► 4. If NOT in WAL: Read base Page 42 from app.db             |
+-------------------------------------------------------------------------+

```

Enter fullscreen mode Exit fullscreen mode 

---

## [ ](#3-anatomy-of-the-wal-file-headers-and-frames)3\. Anatomy of the WAL File: Headers and Frames 

The `.db-wal` file starts with a 32-byte header followed by zero or more sequential **frames**. Each frame encapsulates exactly one modified database page.

### [ ](#the-32byte-wal-header)The 32-Byte WAL Header 

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Magic Number (0x377f0682 or 0x377f0683)                |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       File Format Version (Currently 3007000)                 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Database Page Size (e.g. 4096 bytes)                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Checkpoint Sequence Number                              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Salt-1 (Random 32-bit integer generated per reset)      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Salt-2 (Random 32-bit integer incremented per reset)    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Checksum-1 (Cumulative 32-bit checksum of header)       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Checksum-2 (Cumulative 32-bit checksum of header)       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

```

Enter fullscreen mode Exit fullscreen mode 

* **Magic Number:** Identifies WAL format and the endianness used for checksum calculation (`0x377f0682` for big-endian checksums, `0x377f0683` for little-endian).
* **Page Size:** Stored so the WAL parser knows the exact byte length of every trailing frame without querying the main database header.
* **Checkpoint Sequence Number:** Increments each time the WAL file is checkpointed and restarted.
* **Salt values:** Prevent stale frames from previous WAL iterations from being mistaken for valid transactions after a checkpoint reset.

### [ ](#the-24byte-frame-header-and-payload)The 24-Byte Frame Header and Payload 

Every frame in the WAL file consists of a 24-byte frame header immediately followed by `pageSize` bytes of raw page data:  

```
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Page Number (Big-endian 32-bit integer)                 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Size of DB in Pages (Non-zero ONLY on commit frame)     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Salt-1 (Must match Salt-1 from WAL header)              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Salt-2 (Must match Salt-2 from WAL header)              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Checksum-1 (Rolling checksum including this frame)      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Checksum-2 (Rolling checksum including this frame)      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
|                   PAGE DATA (e.g. 4096 bytes)                 |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

```

Enter fullscreen mode Exit fullscreen mode 

Notice the second field: **Size of DB in Pages**. 

When a multi-page transaction writes 5 modified pages to the WAL, the first 4 frames have this field set to `0`. The 5th frame (the commit frame) contains the total page count of the database. 

If power fails while writing frame 3, the database engine ignores frames 1 through 3 on recovery because it never encounters a valid commit marker with matching checksums. Atomicity is guaranteed by appending a single integer to the last frame.

---

## [ ](#4-the-shared-memory-index-raw-dbshm-endraw-why-readers-dont-scan-the-log)4\. The Shared Memory Index (`.db-shm`): Why Readers Don't Scan the Log 

If a WAL file contains 10,000 frames, how does a reader looking for Page 42 know which frame holds the newest version without scanning all 10,000 frames from disk?

That is the job of `database.db-shm`.  

```
+--------------------------------------------------------------------+
|                    WAL-INDEX (.db-shm) ARCHITECTURE                |
|                                                                    |
|  +--------------------------------------------------------------+  |
|  | 136-Byte WAL-Index Header                                    |  |
|  | - mxFrame: 840 (Highest committed frame in WAL)              |  |
|  | - readMarks[8]: [120, 450, 840, 0xFFFFFFFF, ...]             |  |
|  | - Checksums & Salting metadata                               |  |
|  +--------------------------------------------------------------+  |
|  | Hash Table Block 0 (Frames 1 to 4062)                        |  |
|  |   [Page Number Index -> Frame Number Mapping]                |  |
|  +--------------------------------------------------------------+  |
|  | Hash Table Block 1 (Frames 4063 to 8158)                      |  |
|  +--------------------------------------------------------------+  |
+--------------------------------------------------------------------+

```

Enter fullscreen mode Exit fullscreen mode 

The WAL index file is structured into 32KB memory blocks:

1. **The 136-Byte Header:** Contains two identical copies of the index metadata (for atomic lock-free reads using memory barriers), the current `mxFrame` counter, and an array of 8 `readMark` slots.
2. **Hash Tables:** Each 32KB block indexes up to 4,062 frames using open-address linear probing.

### [ ](#crucial-architectural-properties-of-raw-dbshm-endraw-)Crucial Architectural Properties of `.db-shm`: 

* **Volatile and Transient:** The `.db-shm` file contains zero persistent database data. If it is deleted or the machine crashes, SQLite reconstructs it automatically by reading `database.db-wal` upon the next connection.
* **Native CPU Endianness:** Unlike `.db` and `.db-wal` (which are strictly big-endian on disk for cross-platform portability), the `.db-shm` file is formatted in the host CPU's native byte order. This allows zero-cost dereferencing without endianness translation instructions.
* **Shared via OS Memory Mapping:** All connections within the same OS access `.db-shm` using `mmap()`. Atomic CAS (Compare-And-Swap) operations and POSIX shared-memory advisory locks synchronize reader registration without system call overhead.

---

## [ ](#5-how-snapshot-isolation-works-stepbystep)5\. How Snapshot Isolation Works: Step-by-Step 

Let us trace what happens when Reader A and Writer B interact simultaneously.  

```
TIMELINE: CONCURRENT READ & WRITE IN WAL MODE

T1: [Reader A starts transaction]
    └─► Reads mxFrame = 100 from .db-shm.
    └─► Sets its readMark = 100 in .db-shm.
    └─► Snapshot boundary is now locked at Frame 100.

T2: [Writer B modifies Page 5 and commits]
    └─► Appends Page 5 as Frame 101 to .db-wal.
    └─► Updates hash table in .db-shm (Page 5 -> Frame 101).
    └─► Updates mxFrame in .db-shm to 101.

T3: [Reader A reads Page 5]
    └─► Looks up Page 5 in .db-shm hash table.
    └─► Finds Frame 101, but Reader A's max frame is 100 (101 > 100).
    └─► Reader A ignores Frame 101 and reads original Page 5 from app.db!

T4: [Reader C starts new transaction]
    └─► Reads mxFrame = 101 from .db-shm.
    └─► Reads Page 5 -> directly loads Frame 101 from app.db-wal!

```

Enter fullscreen mode Exit fullscreen mode 

### [ ](#the-read-algorithm-page-resolution)The Read Algorithm (Page Resolution) 

Whenever SQLite needs to read Page $P$ during a query:

1. SQLite checks the `.db-shm` hash table for Page $P$.
2. It searches for the highest frame number $F$ associated with $P$ such that $F \\le \\text{mxFrame}\_{\\text{reader}}$.
3. **If found:** SQLite reads Page $P$ directly from `app.db-wal` at byte offset: $$\\text{Offset} = 32 + (F - 1) \\times (24 + \\text{pageSize}) + 24$$
4. **If not found:** SQLite reads Page $P$ from the main `app.db` file at byte offset: $$\\text{Offset} = (P - 1) \\times \\text{pageSize}$$

Because Reader A ignores all frames numbered greater than 100, Writer B can write frames 101, 102, and 103 without locking or corrupting Reader A's view of the world.

---

## [ ](#6-checkpointing-moving-frames-back-to-the-main-database)6\. Checkpointing: Moving Frames Back to the Main Database 

Because writes only append to `app.db-wal`, the WAL file would grow indefinitely if left unchecked. 

**Checkpointing** is the process of copying committed page frames from `app.db-wal` back into their corresponding locations in the base `app.db` file.  

```
+--------------------------------------------------------------------------+
|                          CHECKPOINTING MECHANISM                         |
|                                                                          |
|   app.db-wal (Frames 1..1000)              app.db (Base Pages)           |
|  +---------------------------+            +----------------------------+ |
|  | Frame 1: Page 4  ───────┼───────────► | Offset: (4-1) * 4096       | |
|  | Frame 2: Page 12 ───────┼───────────► | Offset: (12-1) * 4096      | |
|  | Frame 3: Page 4  ───────┼───(Overwrites newest Page 4 to disk)      | |
|  +---------------------------+            +----------------------------+ |
|               │                                                          |
|               └─► Once backfilled past all active reader readMarks:      |
|                   Reset WAL header frame pointer back to 1.              |
+--------------------------------------------------------------------------+

```

Enter fullscreen mode Exit fullscreen mode 

SQLite supports 4 distinct checkpoint modes via `sqlite3_wal_checkpoint_v2()`:

| Mode         | Behavior                                                                                                                                                                             | Blocks Writers? | Blocks Readers? |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- | --------------- |
| **PASSIVE**  | Backfills as many frames as possible up to the oldest active readMark. If an active reader is reading an old frame, it stops without waiting. Default mode used by auto-checkpoints. | No              | No              |
| **FULL**     | Blocks new writers and waits for existing readers to finish, then backfills all frames to the main .db file.                                                                         | Yes             | No              |
| **RESTART**  | Like FULL, but also waits for all readers to clear so it can reset the WAL index to frame 1\. Subsequent writes overwrite the WAL file from the beginning.                           | Yes             | Yes (briefly)   |
| **TRUNCATE** | Like RESTART, but additionally truncates the app.db-wal file on disk to 0 bytes.                                                                                                     | Yes             | Yes (briefly)   |

By default, SQLite triggers an automatic `PASSIVE` checkpoint whenever the WAL file reaches **1,000 frames** (approx. 4MB with 4KB pages).

---

## [ ](#7-the-three-hidden-traps-of-sqlite-wal-in-production)7\. The Three Hidden Traps of SQLite WAL in Production 

While WAL mode transforms SQLite into a high-performance concurrent engine, it introduces three operational edge cases that catch developers off guard.

### [ ](#trap-1-the-10gb-wal-bloat-checkpoint-starvation)Trap 1: The 10GB WAL Bloat (Checkpoint Starvation) 

This is the most common SQLite production failure. 

Because `PASSIVE` checkpointing cannot overwrite frames that are older than the oldest active reader's `readMark`, **a single long-running read query or unclosed connection will stall all checkpoints**.  

```
[Active Long Reader]   ──► Holding readMark at Frame 50
[Incoming Writes]      ──► Append Frames 51 through 50,000 to .db-wal
[Auto-Checkpoint]      ──► Tries to run at Frame 1,000...
                           STOPS at Frame 50 because Reader is still active!
                           Result: .db-wal balloons to 500MB, 2GB, 10GB.

```

Enter fullscreen mode Exit fullscreen mode 

As the WAL file grows into gigabytes, every new read query suffers degraded cache locality and slower index traversals.

**The Fix:** 

1. Keep read transactions short.
2. Set a busy timeout (`busy_timeout = 5000;`).
3. Monitor WAL size and periodically run explicit checkpoints:

```
import sqlite3

conn = sqlite3.connect("app.db")
# Run a PASSIVE or FULL checkpoint and check un-backfilled frame counts
# Returns (busy_status, log_frames, checkpointed_frames)
busy, log, ckpt = conn.execute("PRAGMA wal_checkpoint(PASSIVE);").fetchone()
if log - ckpt > 1000:
    print(f"Warning: {log - ckpt} uncheckpointed frames stalled by active readers!")

```

Enter fullscreen mode Exit fullscreen mode 

### [ ](#trap-2-network-filesystems-nfs-smb-ebs-multiattach)Trap 2: Network Filesystems (NFS / SMB / EBS Multi-Attach) 

SQLite WAL mode **does not work over network filesystems** like NFS, SMB, or GlusterFS.

The `.db-shm` file relies on shared memory semantics (`mmap` memory synchronization and POSIX advisory locking within the kernel). Network filesystems do not support unified shared memory across separate client instances. 

Attempting to run WAL mode on an NFS mount results in instant locking failures (`SQLITE_IOERR_SHMOPEN`) or silent data corruption.

### [ ](#trap-3-incomplete-file-backups)Trap 3: Incomplete File Backups 

In rollback journal mode, backing up `database.db` with a simple file copy utility (`cp` or `rsync`) while the database is idle yields a valid database.

In WAL mode, copying `database.db` alone leaves the newest committed transactions behind in `database.db-wal`. If you restore `database.db` without its companion `.db-wal` and `.db-shm` files, you restore an outdated snapshot.

**The Fix:** Never use filesystem file copy on an active WAL database. Always use the SQLite Online Backup API:  

```
sqlite3 app.db ".backup 'backup.db'"

```

Enter fullscreen mode Exit fullscreen mode 

---

## [ ](#summary-mental-model)Summary Mental Model 

| Feature                 | Rollback Journal (DELETE)                      | Write-Ahead Log (WAL)                                        |
| ----------------------- | ---------------------------------------------- | ------------------------------------------------------------ |
| **Write Strategy**      | Overwrite main .db in-place after journal copy | Append new frames to .db-wal                                 |
| **Readers vs Writers**  | Writers block readers; Readers block writers   | **Readers never block writers; Writers never block readers** |
| **Commit Overhead**     | 2 disk writes + multiple fsyncs per commit     | 1 append write + 1 fsync per commit                          |
| **Companion Files**     | Temporary app.db-journal during writes         | Persistent app.db-wal and app.db-shm                         |
| **Network FS Support**  | Supported with network locks                   | **Unsupported** (requires shared OS memory)                  |
| **Concurrency Ceiling** | 1 active operation (Read OR Write)             | **N concurrent Readers + 1 serialized Writer**               |

By understanding the division of labor between `app.db`, `app.db-wal`, and `app.db-shm`, you can comfortably run SQLite at thousands of queries per second without mysterious lock timeouts or runaway log growth.

## Top comments (0) 

Subscribe 

![pic](https://media2.dev.to/dynamic/image/width=256,height=,fit=scale-down,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.amazonaws.com%2Fuploads%2Farticles%2F8j7kvp660rqzt99zui8e.png) 

Submit Preview [Dismiss](/404.html) 

[Code of Conduct](/code-of-conduct) • [Report abuse](/report-abuse) 

[ ![](https://media2.dev.to/dynamic/image/width=90,height=90,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Fuser%2Fprofile_image%2F4069010%2Fda8f710a-f285-4309-8c69-770badbe9c7b.jpg) Syed Anzar ](/syed%5Fanzar) 

Follow 

* Location  
Srinagar ,J&K
* Joined  
Aug 8, 2026

### More from [Syed Anzar](/syed%5Fanzar) 

[JWTs vs Server Sessions: What Developers Actually Get Wrong About Stateless Auth #security #webdev #architecture #programming ](/syed%5Fanzar/jwts-vs-server-sessions-what-developers-actually-get-wrong-about-stateless-auth-4c7d) [Supabase Under the Hood: What Actually Happens When You Listen to Postgres Changes #supabase #postgres #architecture #database ](/syed%5Fanzar/supabase-under-the-hood-what-actually-happens-when-you-listen-to-postgres-changes-4moj) 

[DEV Community](/) — A space to discuss and keep up software development and manage your software career 

* [Home ](/)
* [DEV Challenges ](/challenges)
* [DEV++ ](/++)
* [Videos ](/videos)
* [DEV Help ](/help)
* [Advertise on DEV ](/advertise)
* [Organization Accounts ](/organizations)
* [DEV Showcase ](/showcase)
* [About ](/about)
* [Contact ](/contact)
* [DEV Shop ](https://shop.forem.com/)
* [MLH ](https://mlh.io/)
* [Code of Conduct ](/code-of-conduct)
* [Privacy Policy ](/privacy)
* [Terms of Use ](/terms)

Built on [Forem](https://www.forem.com) — the [open source](https://dev.to/t/opensource) software that powers [DEV](https://dev.to) and other inclusive communities.

Made with love and [Ruby on Rails](https://dev.to/t/rails). DEV Community © 2016 - 2026.

![DEV Community](https://media2.dev.to/dynamic/image/width=190,height=,fit=scale-down,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.amazonaws.com%2Fuploads%2Farticles%2F8j7kvp660rqzt99zui8e.png) 

We're a place where coders share, stay up-to-date and grow their careers. 

[Log in ](/enter?signup%5Fsubforem=1) [Create account ](/enter?signup%5Fsubforem=1&state=new-user) 

![](https://assets.dev.to/assets/sparkle-heart-5f9bee3767e18deb1bb725290cb151c25234768a0e9a2bd39370c382d02920cf.svg) ![](https://assets.dev.to/assets/multi-unicorn-b44d6f8c23cdd00964192bedc38af3e82463978aa611b4365bd33a0f1f4f3e97.svg) ![](https://assets.dev.to/assets/exploding-head-daceb38d627e6ae9b730f36a1e390fca556a4289d5a41abb2c35068ad3e2c4b5.svg) ![](https://assets.dev.to/assets/raised-hands-74b2099fd66a39f2d7eed9305ee0f4553df0eb7b4f11b01b6b1b499973048fe5.svg) ![](https://assets.dev.to/assets/fire-f60e7a582391810302117f987b22a8ef04a2fe0df7e3258a5f49332df1cec71e.svg)