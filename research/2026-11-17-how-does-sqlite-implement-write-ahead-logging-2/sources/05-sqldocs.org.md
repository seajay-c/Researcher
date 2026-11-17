---
n: 5
url: https://sqldocs.org/sqlite-write-ahead-logging/
title: SQLite WAL Mode: How Write-Ahead Logging Works and When to Use It
fetched_at: 2026-11-17T07:00:13.409427Z
---

 

[Skip to content](#wp--skip-link--target)

[![SQL Docs](https://sqldocs.org/wp-content/uploads/2025/09/SQLdocs-logo-modified-1.png)](https://sqldocs.org/)

* [Home](https://sqldocs.org/)
* [About Us](https://sqldocs.org/about/)
* [SQLite](https://sqldocs.org/sqlite-tutorial/)
* [Tools](https://sqldocs.org/tools/sqlite-viewer/)

# SQLite WAL Mode: How Write-Ahead Logging Works and When to Use It

Ninad Pathak

October 7, 2026

Write-ahead logging (WAL) lets SQLite readers keep reading while a writer writes, which is why turning it on can fix some lock errors. It also changes how SQLite writes to disk and adds two files next to the database. In this article I’ll walk you through what WAL mode does and when it’s worth switching on.

**TLDR**

* WAL (write-ahead logging) is a journal mode where changes go to a separate `-wal` file first and get copied into the database later, at a checkpoint.
* Turn it on once with `PRAGMA journal_mode = WAL;`. The setting is stored in the database file.
* Readers no longer block the writer, and the writer no longer blocks readers. There is still only one writer at a time.
* Expect `-wal` and `-shm` files next to the database while it’s open. Never delete the `-wal` file, and back up a live database with the backup API or `VACUUM INTO`.
* WAL doesn’t work on a network filesystem.

Table of contents 

1. [What is WAL mode in SQLite?](#what-is-wal-mode-in-sqlite "What is WAL mode in SQLite?")
2. [SQLite WAL mode syntax](#sqlite-wal-mode-syntax "SQLite WAL mode syntax")
3. [How to turn on WAL mode](#how-to-turn-on-wal-mode "How to turn on WAL mode")  

  1. [Step 1: Switch the journal mode](#step-1-switch-the-journal-mode "Step 1: Switch the journal mode")
  2. [Step 2: Check that it stuck](#step-2-check-that-it-stuck "Step 2: Check that it stuck")
  3. [Step 3: Check the checkpoint threshold](#step-3-check-the-checkpoint-threshold "Step 3: Check the checkpoint threshold")
4. [Examples](#examples "Examples")  

  1. [Watch the -wal and -shm files](#watch-the-wal-and-shm-files "Watch the -wal and -shm files")
  2. [Turn WAL off](#turn-wal-off "Turn WAL off")
5. [Edge cases](#edge-cases "Edge cases")  

  1. [After a crash, the -wal file holds your data](#after-a-crash-the-wal-file-holds-your-data "After a crash, the -wal file holds your data")
  2. [There is still only one writer](#there-is-still-only-one-writer "There is still only one writer")
  3. [synchronous = NORMAL trades durability for speed](#synchronous-normal-trades-durability-for-speed "synchronous = NORMAL trades durability for speed")
  4. [Network filesystems and read-only access](#network-filesystems-and-read-only-access "Network filesystems and read-only access")
6. [Conclusion](#conclusion "Conclusion")
7. [Further reading](#further-reading "Further reading")

## What is WAL mode in SQLite?

WAL mode is one of SQLite’s journal modes, the way SQLite makes a transaction safe against crashes. In the default rollback-journal mode, SQLite copies the old pages aside and writes changes straight into the database file. In WAL mode, it does the reverse: changes are appended to a separate `-wal` file, and a checkpoint copies them into the database later.

The benefit, in the docs’ words: “WAL provides more concurrency as readers do not block writers and a writer does not block readers” ([advantages](https://sqlite.org/wal.html#advantages)). A new database starts in the rollback-journal mode, which SQLite reports as `delete`:

```bash
sqlite> PRAGMA journal_mode;
delete
```

## SQLite WAL mode syntax

WAL is controlled by a few PRAGMAs:

| Statement                         | What it does                                               |
| --------------------------------- | ---------------------------------------------------------- |
| PRAGMA journal\_mode;             | Shows the current mode                                     |
| PRAGMA journal\_mode = WAL;       | Turns WAL on and returns the new mode                      |
| PRAGMA journal\_mode = DELETE;    | Turns WAL off again                                        |
| PRAGMA wal\_autocheckpoint;       | Shows the page count that triggers an automatic checkpoint |
| PRAGMA wal\_checkpoint(TRUNCATE); | Runs a checkpoint now and empties the \-wal file           |

## How to turn on WAL mode

To show you how this works, I will use a fresh database file, `t.db`, and run each statement from a new sqlite3 shell process.

### Step 1: Switch the journal mode

The PRAGMA returns the new mode:

```bash
sqlite> PRAGMA journal_mode = WAL;
wal
```

### Step 2: Check that it stuck

“Unlike the other journaling modes, PRAGMA journal\_mode=WAL is persistent” ([Write-Ahead Logging](https://sqlite.org/wal.html), section 3.3). A new connection, here a new shell process, still sees WAL:

```bash
sqlite> PRAGMA journal_mode;
wal
```

Other modes don’t persist. A new connection goes back to `delete`:

```bash
sqlite> PRAGMA journal_mode = TRUNCATE;
truncate
sqlite> PRAGMA journal_mode;
delete
```

### Step 3: Check the checkpoint threshold

SQLite checkpoints on its own: “By default, SQLite does a checkpoint automatically when the WAL file reaches a threshold size of 1000 pages” ([checkpointing](https://sqlite.org/wal.html#ckpt)). This database reports that default:

```bash
sqlite> PRAGMA journal_mode = WAL;
wal
sqlite> PRAGMA wal_autocheckpoint;
1000
```

## Examples

These examples show WAL’s files at work. Each one runs in its own folder.

### Watch the -wal and -shm files

While a connection is open, writes go to `app.db-wal`, and `app.db-shm` holds a shared index. This script writes 500 rows of 1,000 bytes, then checkpoints and closes:

```python
import os, sqlite3

con = sqlite3.connect("app.db", isolation_level=None)
print("journal_mode:", con.execute("PRAGMA journal_mode = WAL").fetchone()[0])
con.execute("CREATE TABLE IF NOT EXISTS log (msg TEXT)")
con.executemany("INSERT INTO log VALUES (?)", [("x" * 1000,)] * 500)

def files():
    return {f: os.path.getsize(f) for f in sorted(os.listdir(".")) if f.startswith("app.db")}

print("while open:      ", files())
print("checkpoint:      ", con.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone())
print("after checkpoint:", files())
con.close()
print("after close:     ", files())
```

```bash
$ python3 wal_files.py
journal_mode: wal
while open:       {'app.db': 4096, 'app.db-shm': 32768, 'app.db-wal': 3094152}
checkpoint:       (0, 0, 0)
after checkpoint: {'app.db': 520192, 'app.db-shm': 32768, 'app.db-wal': 0}
after close:      {'app.db': 520192}
```

The rows sat in the WAL file, about 3 MB, until the checkpoint copied them into `app.db`. When the last connection closed, the `-wal` and `-shm` files were removed.

### Turn WAL off

Switch back to the rollback journal with `DELETE`:

```bash
sqlite> PRAGMA journal_mode = DELETE;
delete
sqlite> PRAGMA journal_mode;
delete
```

## Edge cases

WAL’s extra files and its single writer have limits:

### After a crash, the -wal file holds your data

I wrote 3 rows in WAL mode and exited without closing or checkpointing, like a crash. The rows existed only in `crash.db-wal`. Opening the database again found all 3\. A copy of `crash.db` on its own didn’t even have the table:

```python
import os, sqlite3

# Write 3 rows in WAL mode, then exit without closing or checkpointing (like a crash).
con = sqlite3.connect("crash.db", isolation_level=None)
con.execute("PRAGMA journal_mode = WAL")
con.execute("PRAGMA wal_autocheckpoint = 0")  # keep everything in the -wal file for this demo
con.execute("CREATE TABLE log (msg TEXT)")
con.executemany("INSERT INTO log VALUES (?)", [("a",), ("b",), ("c",)])
os._exit(0)  # no close(), no checkpoint
```

```bash
$ python3 crash.py
$ ls crash.db*
crash.db
crash.db-shm
crash.db-wal
$ cp crash.db copy-without-wal.db
$ sqlite3 crash.db "SELECT count(*) FROM log;"
3
$ sqlite3 copy-without-wal.db "SELECT count(*) FROM log;"
Error: in prepare, no such table: log
```

So don’t delete a `-wal` file to “fix” a database. To back up a database that’s in use, use the backup API or `VACUUM INTO`, not a file copy. Copying files is safe only when no connection has the database open, and then the copy must include any `-wal` file.

### There is still only one writer

Readers and one writer can work at once, “However, since there is only one WAL file, there can only be one writer at a time” ([concurrency](https://sqlite.org/wal.html#concurrency)). The [database is locked](https://sqldocs.org/sqlite-database-is-locked/) page shows a commit failing in rollback mode and succeeding in WAL mode while a reader is open.

### synchronous = NORMAL trades durability for speed

WAL setups often add `PRAGMA synchronous = NORMAL;`. It’s faster, and the docs state the trade-off plainly: with synchronous set to NORMAL, “transactions are no longer durable and might rollback following a power failure or hard reset” ([performance considerations](https://sqlite.org/wal.html#fast)). The database itself stays consistent, but the last transactions before a power cut may be lost.

### Network filesystems and read-only access

* “All processes using a database must be on the same host computer; WAL does not work over a network filesystem” ([disadvantages](https://sqlite.org/wal.html#advantages)).
* The extra `-wal` and `-shm` files “can make SQLite less appealing for use as an application file-format” (same section).
* Read-only access has conditions. “Beginning with version 3.22.0 (2018-01-22), a read-only WAL-mode database file can be opened if the -shm and -wal files already exist or those files can be created or the database is immutable” ([read-only databases](https://sqlite.org/wal.html#readonly)).

## Conclusion

Turn on WAL with `PRAGMA journal_mode = WAL;` once per database file. You get readers and a writer working at the same time, and the setting stays on. Keep the `-wal` file with the database at all times, and keep WAL databases off network filesystems.

## Further reading

* [SQLite “database is locked”](https://sqldocs.org/sqlite-database-is-locked/)
* [SQLite PRAGMA](https://sqldocs.org/sqlite-pragma/)
* [SQLite VACUUM and VACUUM INTO](https://sqldocs.org/sqlite-vacuum/)
* [Python SQLite3 tutorial](https://sqldocs.org/python-sqlite3/)
* [All SQLite guides by topic](https://sqldocs.org/sqlite-tutorial/)
* SQLite docs: [Write-Ahead Logging](https://sqlite.org/wal.html)

_Tested with SQLite 3.51.0, Python 3.13.14 (SQLite 3.53.4) and Python 3.9.6 on macOS, 7 October 2026._

Ninad Pathak

**Previous:** [SQLite Boolean: How to Store and Query TRUE and FALSE](https://sqldocs.org/sqlite-boolean/)

**Read next:** [SQLite in Node.js: node:sqlite and better-sqlite3 (Tested Examples)](https://sqldocs.org/sqlite-nodejs/)

**Important Links**

[Terms of Use](https://sqldocs.org/terms/)

[Privacy Policy](https://sqldocs.org/privacy/)

**Company**

[Home](https://sqldocs.org/)

[About Us](https://sqldocs.org/about/)

[Write for Us](https://sqldocs.org/write-for-us/)

[Careers](https://www.linkedin.com/company/sql-docs/jobs/)

**Resources**

[SQLite](https://sqldocs.org/introduction/)

[SQLite vs MySQL](https://sqldocs.org/sqlite-vs-mysql/)

[SQLite vs. PostgreSQL](https://sqldocs.org/sqlite-vs-postgresql/)

**Follow SQLDocs**

[Twitter (X)](https://x.com/SQLDocsOrg)

[LinkedIn](https://www.linkedin.com/company/sql-docs/)

Copyright © 2025 – [SQL Documentation](https://sqldocs.org/)