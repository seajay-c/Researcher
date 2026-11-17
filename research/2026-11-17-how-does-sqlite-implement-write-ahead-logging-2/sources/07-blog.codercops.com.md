---
n: 7
url: https://blog.codercops.com/blog/sqlite-wal-mode-explained-production-settings-2026
title: SQLite WAL Mode Explained: Settings for Production
fetched_at: 2026-11-17T07:00:55.924961Z
---

[](https://blog.codercops.com/cdn-cgi/content?id=JgtXf5D7PhQIEURjcMmrKfhiGQUtX0zr0eJ3KSJKqtg-1794898855.8383837-1.2.1.1-wZhz4FZAfRyyLgLqo6m.ZB.YmLAMHEZTEN9aarW.QOevu9IkBQDNzVYSJW8%5FOZKD) [Skip to content ](#main-content) 

[![CODERCOPS](/images/brand/logo.png)CODERCOPSjournal](/blog)

[Journal](/blog)[Platform](https://app.codercops.com/jobs)[Product](https://www.codercops.com)[Agency](https://agency.codercops.com)

[RSS](/feed.xml)

[![CODERCOPS](/images/brand/logo.png)CODERCOPS](/blog)

[Journal](/blog)[Platform](https://app.codercops.com/jobs)[Product](https://www.codercops.com)[Agency](https://agency.codercops.com)[RSS feed](/feed.xml)

[ Journal ](/blog) [ Technology ](/blog/category/technology) October 12, 2026 

---

 Technology · Databases 

#  SQLite WAL Mode Explained: Settings for Production 

 WAL mode lets SQLite readers and a writer work at once. Here is how it works, the pragmas to set, and the three ways it bites in production. 

![Abhishek Gupta](/images/team/abhishek-gupta.webp) 

Abhishek Gupta

 7 min read 

By

![Abhishek Gupta](/images/team/abhishek-gupta.webp) Abhishek Gupta 

Read

7 min

[ SQLite ](/blog/tag/sqlite)[ Databases ](/blog/tag/databases)[ Backend ](/blog/tag/backend)[ Performance ](/blog/tag/performance)[ Production ](/blog/tag/production)[ 2026 ](/blog/tag/2026) 

![A brass conveyor belt carrying wooden crates toward an iron strongbox while a crane lowers one more crate](https://blog-images.codercops.com/covers/sqlite-wal-mode-explained-production-settings-2026/20261012-b4e6a80d.jpg) 

Sponsored

Contents

* [ What WAL mode actually does ](#what-wal-mode-actually-does)
* [ Turn it on ](#turn-it-on)
* [ What each setting buys you ](#what-each-setting-buys-you)
* [ The write lock is still singular ](#the-write-lock-is-still-singular)
* [ Three ways WAL bites in production ](#three-ways-wal-bites-in-production)
* [ When to leave it off ](#when-to-leave-it-off)

Back to top 

Share

[ ](https://twitter.com/intent/tweet?text=SQLite%20WAL%20Mode%20Explained%3A%20Settings%20for%20Production&url=https%3A%2F%2Fblog.codercops.com%2Fblog%2Fsqlite-wal-mode-explained-production-settings-2026) [ ](https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fblog.codercops.com%2Fblog%2Fsqlite-wal-mode-explained-production-settings-2026) 

Key takeaways

* Run \`PRAGMA journal\_mode=WAL\` once per database file. Unlike the other journal modes, it persists across connections and restarts.
* WAL lets readers and one writer proceed at the same time. It does not allow two writers. Concurrent writers still queue, so set a \`busy\_timeout\`.
* Pair WAL with \`synchronous=NORMAL\`. You trade durability of the last few commits after a power failure for far fewer fsync calls.
* WAL does not work over a network filesystem. Every process must be on the same host.
* A reader that never closes can stop checkpoints from finishing, and the -wal file then grows without bound.

SQLite WAL mode is a journal mode where changes are appended to a separate log file instead of being written into the database file directly. Readers no longer block the writer and the writer no longer blocks readers. For a web app with a read-heavy workload on one server, turning it on is usually the single biggest improvement you can make to SQLite, and it takes one line.

The catch is that “readers and writers don’t block each other” is not the same as “many writers”. People find that out the hard way, usually as a `database is locked` error at 2 a.m. This post covers how WAL works, the settings we put on every connection, and the failure modes worth knowing before you ship.

## What WAL mode actually does

By default SQLite uses a rollback journal. Before changing a page, it copies the original page into a journal file, then edits the database file in place. A writer needs exclusive access at commit time, so readers and writers get in each other’s way.

WAL flips the arrangement. The database file stays untouched while a transaction runs. New page versions are appended to a file named `yourdb.sqlite-wal`. A reader starts by noting how far the log extends, and from then on sees the main file plus the log up to that point. A writer adding more frames after that point does not disturb it.

There is a third file, `yourdb.sqlite-shm`. It is the wal-index, a small shared-memory structure (rarely over 32 KiB according to the SQLite docs) that lets connections find the latest version of a page in the log without scanning it. You never touch it, but you must not delete it while connections are open, and you must keep all three files together when you copy a database.

Periodically a checkpoint copies logged pages back into the main file. By default that happens automatically once the log reaches 1000 pages, and when the last connection closes.

## Turn it on

```
import sqlite3

def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL")   # persistent, stored in the file
    conn.execute("PRAGMA synchronous=NORMAL") # per connection
    conn.execute("PRAGMA busy_timeout=5000")  # per connection, in ms
    conn.execute("PRAGMA foreign_keys=ON")    # per connection
    return conn
```

The same four pragmas work from any driver. Only the first one is persistent: the SQLite docs are explicit that `journal_mode=WAL` stays in effect when the database is reopened, which no other journal mode does. The other three reset to defaults every time a connection opens, so they belong in your connection factory, not in a migration.

One more constraint: the page size cannot be changed once the database is in WAL mode. If you want a non-default `page_size`, set it before you switch.

## What each setting buys you

| Pragma                   | What it does                                                  | Trade-off                                                          |
| ------------------------ | ------------------------------------------------------------- | ------------------------------------------------------------------ |
| journal\_mode=WAL        | Concurrent readers plus one writer                            | Needs local disk; three files instead of one                       |
| synchronous=NORMAL       | Syncs only at checkpoints, not every commit                   | After a power loss, the last commits can roll back. No corruption. |
| busy\_timeout=5000       | Waits up to 5 s for the write lock instead of failing at once | Slow writers can stack up behind each other                        |
| wal\_autocheckpoint=1000 | Pages before an automatic checkpoint (the default)            | Higher means fewer checkpoints and a bigger log                    |

`synchronous=NORMAL` deserves a plain explanation because people read it as “unsafe”. In WAL mode the docs describe it this way: the checkpoint is the only operation that issues a sync. A process crash loses nothing. An operating system crash or power cut can lose transactions that committed after the last checkpoint, but the database stays consistent. If you are storing a shopping cart, that is fine. If you are storing payments, use `synchronous=FULL` and accept the extra fsyncs.

## The write lock is still singular

Here is the mistake I made the first time. I switched a job runner to WAL, saw read latency drop, and assumed I could now fan writes out across eight worker threads. I couldn’t. Eight threads queued behind one write lock, and anything that waited longer than the default timeout got `SQLITE_BUSY`.

Two habits fix most of it:

1. Start write transactions with `BEGIN IMMEDIATE`. A transaction that begins as a read and later tries to upgrade to a write can fail instantly with `SQLITE_BUSY`, even with a busy timeout, because SQLite will not wait when waiting could deadlock. Taking the write lock up front avoids that.
2. Keep write transactions short. Do the network call, the file read, the slow computation first, then open the transaction, write, commit.

```
conn.execute("BEGIN IMMEDIATE")
try:
    conn.execute("UPDATE jobs SET state = 'done' WHERE id = ?", (job_id,))
    conn.commit()
except Exception:
    conn.rollback()
    raise
```

If you truly need many concurrent writers, SQLite is the wrong tool and a server database is the right one. We wrote about where that line sits in Postgres, SQLite and vectors in 2026, and about the managed-SQLite option in [Turso and libSQL at the edge](/blog/turso-libsql-edge-sqlite-production-2026).

## Three ways WAL bites in production

**Network filesystems.** The SQLite docs say it flatly: WAL does not work over a network filesystem, because the wal-index relies on shared memory between processes on one host. If your container mounts the database from NFS or a similar shared volume, do not enable WAL there. Local volumes, including a Docker volume or a block device attached to the VM, are fine.

**The never-ending log.** A checkpoint cannot recycle log frames that an open read transaction might still need. If at least one reader is active at every moment, checkpoints never complete and the `-wal` file grows without bound. The usual cause is not heavy traffic. It is a connection that ran a `SELECT`, never fetched the rest of the rows, and sat in the pool holding a snapshot open. Close cursors, and use a connection pool that resets state on release. If you already have a huge log, find the stuck reader, close it, then run:

```
PRAGMA wal_checkpoint(TRUNCATE);
```

`TRUNCATE` waits for readers to finish and then resets the file to zero bytes, so run it during a quiet moment rather than in the request path. Our guide to [database connection pooling in production](/blog/database-connection-pooling-production-2026) covers the pool-state side of this.

**Copying the database while it runs.** Copying only `yourdb.sqlite` with `cp` while the app is live can give you a file that is missing everything still sitting in the log. Use the online backup API, `VACUUM INTO 'backup.sqlite'`, or the `sqlite3` shell’s `.backup` command. All three produce a consistent single file.

## When to leave it off

Most reasons to skip WAL are about the environment, not the workload. Leave the default journal on if the database lives on a network share, if you need to open it read-only from a location where SQLite cannot create the `-shm` file, or if you need one atomic transaction across several attached databases (WAL guarantees atomicity per database, not across the set).

For an ordinary single-server app, background job queue, or local-first desktop tool, WAL with `synchronous=NORMAL`, a `busy_timeout`, and `BEGIN IMMEDIATE` for writes is the sensible baseline. If you are weighing SQLite against a managed database for a client project, the tradeoffs are the kind we walk through in [our services work](https://agency.codercops.com/services). For schema changes on a database you cannot take offline, see [zero-downtime database migrations](/blog/zero-downtime-database-migrations-production-2026).

The takeaway: set four pragmas in your connection factory, keep write transactions short, and watch the size of the `-wal` file. If it keeps growing, you have a reader that never closed.

Related reading 

* [PostgreSQL 14 End of Life: How to Upgrade to 18, Not 19](/blog/postgresql-14-end-of-life-upgrade-guide-2026)
* [MVCC Explained: Why Postgres Readers Never Block Writers](/blog/mvcc-explained-postgres-readers-dont-block-writers-2026)
* [LSM Trees Explained: Why Write-Heavy Databases Use Them](/blog/lsm-trees-explained-write-heavy-databases-2026)

Built by the people who wrote this

## codercops — get hired, or hire, in one conversation. 

We build the tools we write about. Developers get discovered with a public profile built in one chat; companies hire vetted developers from a curated shortlist. 

[Build your profile ](https://app.codercops.com/signup?utm%5Fsource=blog&utm%5Fmedium=post%5Fcta%5Fbuilder&utm%5Fcampaign=sqlite-wal-mode-explained-production-settings-2026) [Hire developers ](https://app.codercops.com/jobs?utm%5Fsource=blog&utm%5Fmedium=post%5Fcta%5Fhire&utm%5Fcampaign=sqlite-wal-mode-explained-production-settings-2026) [Need it built? Talk to the studio ](https://agency.codercops.com/contact?utm%5Fsource=blog&utm%5Fmedium=post%5Fcta%5Fstudio&utm%5Fcampaign=sqlite-wal-mode-explained-production-settings-2026) 

## Frequently asked questions 

What does WAL mode do in SQLite?

Instead of writing changes into the main database file with a rollback journal, SQLite appends them to a separate write-ahead log. Readers keep seeing a consistent snapshot of the main file plus the log, so they are not blocked by a writer. A checkpoint later copies the logged pages back into the main file.

Is SQLite WAL mode safe for production?

Yes, for a database that lives on a local disk and is used by processes on one machine. It has been available since SQLite 3.7.0 in 2010\. It is unsafe on network filesystems, and with synchronous=NORMAL you can lose the most recent commits (but not corrupt the database) after a power failure.

Why is my SQLite -wal file huge?

Checkpoints cannot finish while a read transaction is always open, so the log keeps growing. Find the long-lived reader (often a connection left in a transaction) and close it. A periodic \`PRAGMA wal\_checkpoint(TRUNCATE)\` during a quiet moment resets the file.

Do I need to set WAL mode on every connection?

No. The journal mode is stored in the database file, so setting it once is enough. Settings like \`synchronous\`, \`busy\_timeout\` and \`foreign\_keys\` are per connection and must be set every time you open one.

Sources

* [ SQLite documentation: Write-Ahead Logging ](https://sqlite.org/wal.html)
* [ SQLite documentation: PRAGMA statements ](https://sqlite.org/pragma.html)

Sponsored

![Abhishek Gupta](/images/team/abhishek-gupta.webp) 

Written by 

 Abhishek Gupta 

 Lead Engineer 

 Expertise in networking and backend development. 

[LinkedIn →](https://linkedin.com/in/abhishek-gupta-g) [GitHub →](https://github.com/Abhi-gits) 

Continue reading

[ Newer dispatch  Python 3.15 UTF-8 Default: Audit Your open() Calls  Technology ](/blog/python-3-15-utf-8-default-audit-open-calls-2026) [ Older dispatch  Deno Deploy Shutdown: How to Migrate to Cloudflare Workers  Web Development ](/blog/deno-joins-cloudflare-runtime-sunset-migration-2026) 

More from this category

## More from Technology 

[See all ](/blog/category/technology) 

[ ![Two-Phase Commit Explained: Why It Blocks, With Code](https://blog-images.codercops.com/covers/two-phase-commit-explained-distributed-transactions-2026/20261014-e6e821b8.jpg) R.01 Technology · 6 min read  Two-Phase Commit Explained: Why It Blocks, With Code  Oct 14, 2026 ](/blog/two-phase-commit-explained-distributed-transactions-2026) 

[ ![HyperLogLog Explained: Count Unique Items in 12 KB](https://blog-images.codercops.com/covers/hyperloglog-explained-count-unique-items-redis-2026/20261013-006d2139.jpg) R.02 Technology · 6 min read  HyperLogLog Explained: Count Unique Items in 12 KB  Oct 13, 2026 ](/blog/hyperloglog-explained-count-unique-items-redis-2026) 

[ ![Python 3.15 UTF-8 Default: Audit Your open() Calls](https://blog-images.codercops.com/covers/python-3-15-utf-8-default-audit-open-calls-2026/20261012-f56c7c45.jpg) R.03 Technology · 7 min read  Python 3.15 UTF-8 Default: Audit Your open() Calls  Oct 12, 2026 ](/blog/python-3-15-utf-8-default-audit-open-calls-2026) 

Sponsored

Discussion

## Join the conversation. 

Comments are powered by GitHub Discussions. Sign in with your GitHub account to leave a comment. 

Sponsored

On this page 

* [ What WAL mode actually does ](#what-wal-mode-actually-does)
* [ Turn it on ](#turn-it-on)
* [ What each setting buys you ](#what-each-setting-buys-you)
* [ The write lock is still singular ](#the-write-lock-is-still-singular)
* [ Three ways WAL bites in production ](#three-ways-wal-bites-in-production)
* [ When to leave it off ](#when-to-leave-it-off)

[![CODERCOPS](/images/brand/logo.png)CODERCOPS Journal](/blog)

Working notes from the CODERCOPS team: what we shipped, what broke, and the AI tools earning their keep.

Working notes, twice a month

Subscribe

[![CODERCOPS - Hire vetted software developers, or get hired | Product Hunt](https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1207094&theme=light&t=1785081049978)![CODERCOPS - Hire vetted software developers, or get hired | Product Hunt](https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1207094&theme=dark&t=1785081049978)](https://www.producthunt.com/products/codercops?embed=true&utm%5Fsource=badge-featured&utm%5Fmedium=badge&utm%5Fcampaign=badge-codercops)[![Featured on Launchstag](https://launchstag.com/badge-light.svg)![Featured on Launchstag](https://launchstag.com/badge-dark.svg)](https://launchstag.com)

#### Read

* [All posts](/blog)
* [RSS feed](/feed.xml)

#### Topics

* [AI Integration](/blog/category/ai-integration)
* [Web Development](/blog/category/web-development)
* [Business](/blog/category/business)
* [Cybersecurity](/blog/category/cybersecurity)
* [Cloud & Infrastructure](/blog/category/cloud-infrastructure)
* [Career](/blog/category/career)

#### More

* [Platform](https://app.codercops.com/jobs)
* [Product](https://www.codercops.com)
* [Agency](https://agency.codercops.com)
* [Contact](https://agency.codercops.com/contact)

#### Contact

* [codercops@codercops.com](mailto:codercops@codercops.com)
* Lucknow, India

© 2026 CODERCOPS. All rights reserved.

[Privacy](https://agency.codercops.com/privacy)|[Terms](https://agency.codercops.com/terms)|[Cookies](https://agency.codercops.com/cookie-policy)

Made in India