---
n: 10
url: https://sijinjoseph.com/post/2022-05-10-sqlite-wal-mode-explained/
title: SQLite's WAL mode explained
fetched_at: 2026-11-17T07:01:50.758220Z
---

[skip to content](#main)

[Sijin Joseph](/)
* [posts](/post/)
* [matrix](/programmer-competency-matrix/)
* [ai-matrix](/ai-agent-competency-matrix/)
* [search](/search/)
* ☾☀

cat posts/2022-05-10-sqlite-wal-mode-explained.md

# SQLite's WAL mode explained

2022-05-10 · 9 min read · [databases](/tags/databases/) [sqlite](/tags/sqlite/) [deep-dive](/tags/deep-dive/)

```
PRAGMA journal_mode=WAL;
```

That’s the first thing I run on any SQLite database I’m going to use for more than a test. If you’ve only used SQLite through an ORM’s test configuration you may never have seen it, and it’s the reason most of the “just use SQLite in production” posts going around actually work.

The latest of those is Ben Johnson’s [I’m All-In on Server-Side SQLite](https://fly.io/blog/all-in-on-sqlite-litestream/) on the Fly.io blog, which went up this week. Ben wrote BoltDB and, more recently, Litestream, which streams a SQLite database to S3 as it changes, and he’s now working on it at Fly. His argument is about latency and simplicity. A query against SQLite in your own process takes something like 10 to 20 microseconds, against a millisecond or so to reach a Postgres server in the same region, and a dozen queries per request adds up. And there’s a whole tier of your architecture you don’t have to run. Add last year’s trick of [serving a SQLite database off a static host](/post/2021-07-20-sqlite-on-a-static-host/) with HTTP range requests, and SQLite has had a pretty good year on Hacker News.

I’ve used SQLite since a mobile project in the Windows Mobile days, when it was the only real database that fit on the device, and I’ve always liked it. But what makes it reasonable on a server with concurrent users is WAL mode, and I realized when someone on my team asked me how it works that I could only half explain it. So I went and read the docs properly, and this is what I got out of them.

## First, the old way: the rollback journal

SQLite stores a database as one file divided into fixed-size pages, 4096 bytes by default. A transaction that changes a row ends up changing one or more pages, the leaf page of the table’s B-tree with the row in it, maybe an interior page or two, maybe the index pages. (If you want the B-tree part, I wrote about [how B-trees work](/post/2015-03-17-b-trees-visually/) a few years ago.)

The default journal mode, the one you get if you never run that pragma, is the rollback journal. Before SQLite changes a page in the database file, it copies the page’s _original_ contents into a separate file next to it, `mydb.db-journal`. It flushes the journal to disk, then writes the new pages into the database file itself, flushes that, and finally deletes the journal (or truncates it, or zeroes the header, depending on settings). Deleting the journal is the commit. If the power goes out halfway through, the next process to open the database finds a “hot” journal, copies the original pages back, and the transaction never happened.

It’s simple and very hard to break, but look at what it means for concurrency. While a writer is changing the database file in place, nobody can be reading it, because they might read a page that’s half old and half new. So SQLite uses file locks: readers hold a shared lock, and a writer has to wait until every reader has finished before it can get the exclusive lock it needs to write. One long-running read, a report say, and every write waits behind it. On a phone app that’s fine. On a web server it means the busy page and the slow page get in each other’s way all day.

## WAL: write the changes somewhere else

Write-ahead logging, which arrived in SQLite 3.7.0 back in 2010, turns this around. Instead of copying the _old_ pages out and writing the new ones in place, a writer leaves the database file alone and _appends_ the new versions of the changed pages to a second file, `mydb.db-wal`. Each appended page is a _frame_, the page plus a 24-byte header with the page number, some checksums and salt values that tie it to the current WAL, and a field that’s zero for ordinary frames and set to the database’s new size in pages on the last frame of a transaction. That last frame is the commit marker. A transaction is committed when its commit frame is safely in the WAL, and the database file itself hasn’t been touched.

So now there can be several versions of the same page around: the one in the database file, and one or more newer ones in the WAL. Which one does a reader use?

When a read transaction starts, the reader looks at the WAL and remembers the last valid commit frame it can see. The docs call this its _end mark_. For the rest of its transaction, whenever it needs a page, it looks for the newest copy of that page in the WAL _at or before its end mark_. If there is one, it uses it. If there isn’t, it reads the page from the database file.

mydb.db 1 2 3 4 5 6 mydb.db-wal (frames, appended left to right) p3 p5 ✓ p3 p2 ✓ p6 frame 1 2 3 4 5 A's end mark B's end mark writer appending A reads page 3 here B reads page 3 here both read pages 1 and 4 from the database file 

Two readers, one writer. Green frames end a committed transaction. Each reader sees the WAL only up to the end mark it took when its transaction started, so A and B see different versions of page 3, and neither sees the writer's half-finished frame.

That’s the whole trick, and it’s the same idea as MVCC in Postgres, done with a file instead of row versions. Readers that started at different times see different, consistent snapshots of the database. The writer only ever appends past everyone’s end mark, so it never changes anything a current reader might look at, which means **readers don’t block the writer and the writer doesn’t block readers**. The report can take a minute and the inserts keep going.

Searching the whole WAL for every page read would be slow, so SQLite keeps an index of it, called the wal-index, in a third file, `mydb.db-shm`, which every connection maps into memory. It’s a hash table from page number to frame, which is why a page lookup stays cheap even when the WAL holds thousands of frames. It’s also why WAL mode needs all the processes using the database to be on the same machine. They share that memory, and the docs are clear that WAL doesn’t work over a network filesystem.

## Checkpoints

If the WAL only ever grew, you’d run out of disk, and every page read would have more frames to consider. So every so often SQLite runs a _checkpoint_: it copies the newest committed version of each page from the WAL back into the database file. By default this happens automatically when a commit pushes the WAL past 1000 pages, which is about 4MB at the default page size. Once everything in the WAL has been copied back and no reader is still using it, the next writer can start again from the beginning of the file instead of appending forever.

There’s a catch, which is the one thing about WAL mode I’d tell anyone running it on a server. A checkpoint can’t copy a frame back to the database file if some reader might still need the _old_ version of that page from the database file. In the diagram, while reader A is running, a checkpoint can copy frames 1 and 2 back into the database file but has to stop there. Frame 4 holds a new page 2, and A can’t see frame 4, so A is reading page 2 from the database file. Overwrite it there and A’s snapshot would change underneath it. The rule in the docs is that a checkpoint stops at the end mark of the oldest reader, so long-running readers hold it back. If there’s _always_ a reader, because you have a steady stream of overlapping queries and never a quiet moment, the WAL can’t be reset, and it grows and grows. The docs call this checkpoint starvation. I’ve seen a 2GB WAL next to a 50MB database on a box where a monitoring script held a read transaction open all day.

The fixes are to keep read transactions short (no “open a transaction, call an API, then finish reading”), and if you have to, to run a checkpoint yourself with `PRAGMA wal_checkpoint(TRUNCATE)` from a quiet moment or a background job. There are four checkpoint modes, PASSIVE, FULL, RESTART and TRUNCATE, which differ in how hard they try and whether they wait for readers.

## The other trade-offs

There’s still only one writer at a time. WAL makes reads and the write concurrent, not writes and writes. A second writer waits for the first to commit, and if you don’t set a busy timeout it gets `SQLITE_BUSY` immediately, which is the error every SQLite-on-a-server story eventually includes. Two habits help a lot. Set `PRAGMA busy_timeout` to a few seconds so writers queue instead of failing, and start transactions that are going to write with `BEGIN IMMEDIATE`, so they take the write lock up front instead of reading first and discovering halfway through that someone else got there. Writes in SQLite are fast, so a single writer is fine for a lot more traffic than people expect, but it’s a hard ceiling, and you should know roughly where yours is.

Durability gets a knob too. With `PRAGMA synchronous=FULL`, every commit waits for the WAL to be flushed to disk. With `synchronous=NORMAL`, which is what most people run in WAL mode, the WAL is only flushed at checkpoints, so commits are much faster, and the database still can’t be corrupted by a power failure, but the last few transactions before the power went out may roll back. For a lot of apps that’s a perfectly fine trade. For anything involving money I’d pay for FULL.

And the database is now three files. If you back it up by copying `mydb.db` while it’s in use, you might miss committed transactions that are still in the WAL. Use the backup API, `VACUUM INTO`, or the `.backup` command in the shell.

## Where Litestream fits

This is the part that clicked for me reading Ben’s post. Litestream works _because_ of everything above. It opens a long-running read transaction of its own, on purpose, which stops SQLite from checkpointing on its own schedule. That holds the WAL in place while Litestream copies the new frames out, into its own copy of the WAL and then off to S3\. Then it runs the checkpoint itself, when it’s ready. The checkpoint starvation that’s a bug when a monitoring script does it is a feature when the replicator does it, because it’s done deliberately and released on time. Restoring is replaying those frames on top of a snapshot.

It’s a single-node design, and Ben says so plainly. You get a durable copy of your database within a second or so of each write, not a hot standby, and a restore takes as long as replaying the WAL takes. He also says they’re working on live replication to read replicas, which would change that picture quite a bit if it works.

## Would I?

For our main product, no. We have a lot of app servers writing to one database, and the one-writer, same-machine rules aren’t something I’d want to design around at our size. Postgres is doing fine.

But we also have about a dozen small internal services, each with its own tiny Postgres instance, or a shared one they fight over. Most of them do a handful of writes a minute and get read by a few people. For those, one process, one SQLite file in WAL mode, and Litestream copying it to S3 is a smaller and cheaper system than what we run now, with one less thing to patch. I’m going to try it on the next one we build and see how it goes when someone other than me has to operate it.

[← Hiring in a hot market](/post/2022-05-24-hiring-in-a-hot-market/)[We actually restored from backup →](/post/2022-04-26-we-actually-restored-from-backup/)

© 2026 Sijin Joseph[github](https://github.com/sijinjoseph)[x](https://x.com/SijinJoseph)[linkedin](https://www.linkedin.com/in/sijinjoseph/)[rss](/index.xml)built with astro · catppuccin · / to search