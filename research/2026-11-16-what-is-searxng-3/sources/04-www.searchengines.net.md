---
n: 4
url: https://www.searchengines.net/searxng/
title: SearXNG
fetched_at: 2026-11-17T05:49:50.495618Z
---

[Skip to content](#main)

[![SearchEngines.Net logo — an independent reference on search engines](/assets/img/logo-mark.svg)SearchEngines.NetWho runs which index](/)

[Directory](/directory/)[Guides](/guides/)[How-To](/how-to/change-default-search-engine/)[Glossary](/glossary/)[About](/about/)

Home›[Directory](/directory/)›[Meta-search engines](/meta-search-engines/)›SearXNG

![SearXNG logo, Current logo](/assets/logos/searxng-current.71976cdf.webp)

Meta-search engines

# SearXNG

Resold results

Free metasearch software with no crawler and no index — what it returns, and how private it is, depends entirely on whose instance you use.

By [Bill Hartzer](/about/) · Updated 17 September 2026

## SearXNG is software, not a search engine you visit

Almost everything written about SearXNG starts from a mistaken premise, so this page corrects it first. **There is no such thing as "the SearXNG."** No company, no owner, no canonical address, no service anyone operates on your behalf. SearXNG is free AGPL-3.0 software that you install on a server — or that a volunteer has already installed on theirs and left open to strangers.

What it does is [metasearch](/guides/meta-search-engines-explained/). You give it a query; it asks a configurable set of other engines — Google, Bing, DuckDuckGo, Qwant, Wikipedia, Wikidata, arXiv, GitHub and hundreds more — strips your identity from those requests, merges and re-ranks what comes back, and shows one page. Results group into categories (Web, Images, Videos, News, Social Media, Music, Files, IT, Science), and a bang syntax forces a single upstream engine: _!go_ for [Google](/google/), _!wp_ for Wikipedia. The documentation puts the number of supported services at up to 269.

The verdict at the top reads **[resold results](/guides/own-index-vs-resold-results/)**, accurately, but this is a different kind of resale from the usual one. A commercial front-end resells one partner's index under a license, for profit, on contracted terms. SearXNG sells nothing and fixes nothing: the source is public, the engine list is yours to change, and the aggregator can be you. The verdict describes the architecture — no [crawler](/guides/what-is-a-web-crawler/), no index, results borrowed at query time — not a business relationship, because there is no business.

## How it gets its results

**There is no [crawler](/guides/what-is-a-web-crawler/).** No SearXNG robot visits websites, no user-agent is published because none exists, and nothing is stored, because there is no index. Every result originated with a third-party engine and was fetched live at the moment you pressed enter. The creator of the predecessor project, searx, put it plainly: rather than maintain its own search index, it functions as a [meta-search engine](/meta-search-engines/) and proxy.

The proxy part is the whole [privacy](/guides/private-search-engines-compared/) proposition. Your IP address, cookies and browser fingerprint travel no further than the SearXNG server; what Google or Bing sees is a request from that server, not from you. The original design used HTTP POST by default so query terms stay out of intermediary logs, and it returns plain direct links rather than tracked redirects, with optional proxied or cached alternatives. The mechanism is unlinkability by intermediation: the upstream engine still answers your question, it just cannot tell it was yours.

Two things follow. SearXNG can never be better than the engines it queries — quality is inherited, not created, and the merge is a blend rather than an insight. And when an upstream engine stops answering, results simply get thinner, usually without telling you.

## Which instance? The question that decides everything

This is the most important practical fact about SearXNG and the one most write-ups skip: everything a user cares about is set by whoever installed it. Which services are enabled, how heavily each is weighted in the merged [ranking](/guides/how-search-ranking-works/), whether the image proxy is on, whether results are cached, whether request logs are written at all — all of it is instance-level configuration. **Any sentence of the form "SearXNG gets its results from X" is wrong unless it names an instance.** Two public instances can return materially different results for the same query and offer materially different [privacy](/guides/private-search-engines-compared/), and neither is more authentically SearXNG than the other.

People encounter it two ways:

* **Self-hosted** — on your own server or in a container on your laptop. The guarantee is not a promise from a company but a property of a machine you control, and the code is AGPL so you can read exactly what it does.
* **A public instance** — a volunteer's server, listed at searx.space, under some country's law with that opera[tor](/guides/dark-web-search-engines/)'s logging configuration. The documentation frames the choice bluntly: if you don't trust anyone, you can set up your own.

Jurisdiction is instance-level too. English Wikipedia says SearXNG operates outside US jurisdiction; treat that as loose. The _project_ is not US-based, but an instance may be hosted anywhere, including on American soil — searx.space records each one's location from whois data precisely because it varies. The instance count moves constantly, so no fixed number belongs on a reference page; the documentation cited about 70 well maintained instances as of August 2026.

## Upstream blocking, and why it cannot be patched away

The defining operational problem is that the engines SearXNG depends on have a commercial interest in stopping it, and act on it. In June 2023 a GitHub issue titled "Google is actively blocking SearXNG instances" documented fresh installations being blocked after roughly five consecutive [Google search](/guides/search-algorithm-updates/)es. Public-instance health collapsed within days: tracked instances with a working Google engine fell from 66 of 91 to 25\. The suspected mechanism was Google fingerprinting SearXNG's TLS and HTTP/2 signatures, and maintainers discussed rotating cipher lists, Firefox-like TLS fingerprints and HTTP/3 ([issue #2515](https://github.com/searxng/searxng/issues/2515)).

That was not a one-off. The project still carries active threads about major-engine rate limiting and HTTP 429 errors, its admin documentation ships a Limiter component for managing request pressure, and searx.space tracks per-engine crash rates in bands of under 6 per cent, 6 to 90 per cent, and over 90 per cent, because engines break constantly.

Stated without euphemism: **SearXNG's results depend on the continued tolerance of companies that would prefer it did not exist.** That is a permanent property of the architecture, not a bug awaiting a fix, and it is why a SearXNG page can quietly get worse from one week to the next with nothing changed on your end.

## Who runs it, and how it is funded

Nobody runs it, in the sense that question usually means. SearXNG is a community free-software project developed on GitHub under the searxng organization by volunteer maintainers. The predecessor, searx, was created by **Adam Tauber** and received [European](/guides/search-engine-market-share-europe/) public funding through NGI Zero and NLnet. Whether that funding continued to the SearXNG fork, and for how long, is not documented in any grant record this page could locate.

There is no business model: no advertising, no subscriptions, no API metering, no telemetry and no company. Public instances are paid for by whoever runs them, usually out of pocket, which is the project's chief sustainability risk — instances vanish when an opera[tor](/guides/dark-web-search-engines/) loses interest or tires of paying for the traffic.

The absence of a business model is a strength as well as a fragility. There is no advertiser to please, no investor demanding growth, and no acquisition in which the privacy promise gets quietly rewritten — a failure mode that has claimed more than one nominally private engine. Free software cannot be bought and turned.

## Privacy: what the software guarantees, and what your instance does not

The software's behavior is straightforward: no user tracking, no profiling, cookies and JavaScript optional, POST-based queries, tracker parameters stripped from outbound links, optional image proxying, and upstream engines that never receive your IP address or cookies.

What that guarantees _for you_ depends entirely on who runs the instance, and most coverage gets this wrong by treating public instances as though they inherit the software's guarantees. They do not. On a public instance you have swapped trusting [Google](/google/) for trusting an anonymous volunteer with root on the box your queries pass through. They can log everything. Nothing in the software prevents it, no audit covers it, and searx.space does not verify operator behavior — it measures uptime, response time, TLS grade, CSP grade, HTML modification, version and location. It measures competence, not honesty; its HTML grade exists to flag instances whose pages have been altered ([searx.space](https://searx.space/)).

The strongest scrutiny available is the license itself: the source is public and auditable, and the AGPL requires network-deployed modifications to be published on request — a real, if rarely enforced, lever against an instance quietly running patched code. No formal third-party security audit of the codebase was located.

One trade-off runs against intuition and deserves spelling out. **Self-hosting is not strictly the most private option.** A single-user instance gives perfect protection from an operator, because you are the operator — and the worst crowd anonymity, because every query the upstream engine receives from that IP is yours. A busy public instance is the reverse. No configuration wins on both axes.

## A search backend for AI agents

SearXNG ships no LLM [answer engine](/guides/what-is-an-answer-engine/), no chat interface and no AI summary, and no dated announcement of one was found. It has answerers and infoboxes, but those are deterministic lookups — calculations, Wikidata facts — not generative AI.

The more interesting development runs the other way. SearXNG has become a **de facto search backend for AI systems**: self-hosted LLM agents and retrieval-augmented generation pipelines routinely run a local instance to give a model web access, because it provides a free JSON [search API](/guides/search-engine-apis-and-developer-tools/) with no per-query billing. That is arguably its largest growth area between 2024 and 2026, and it is badly under-covered.

It is also a source of friction. Agent traffic hits the same rate limits and CAPTCHAs described above and accelerates the blocking that degrades the service for humans. Public instances are volunteer-funded infrastructure, not free API capacity.

## History, the searx split, and who it suits

Work on **searx** began in October 2013, inspired by the Seeks project but without Seeks' peer-to-peer [ranking](/guides/how-search-ranking-works/); public releases followed from 2014 under AGPL-3.0, companion tools appeared (Morty for result proxying, Filtron for request filtering) and the contributor base passed fifty. Around 2019 it received NGI Zero and NLnet support for security, accessibility and licensing work. In mid-2021 contributors forked it into **SearXNG**, citing slow bug fixes and the need for engine reliability metrics and user themes. June 2023 brought the Google blocking incident. On **7 September 2023 the original searx repository was archived**, leaving SearXNG the sole maintained line: anyone still running plain searx is running abandonware. SearXNG remains actively developed — the documentation build string read 2026.8.17 when checked on 19 August 2026, against 9,628 commits on master and 34.4k GitHub stars, which measure interest rather than users.

No market-share figure exists, and none is methodologically possible: StatCounter attributes referrals by domain, and SearXNG traffic is spread across hundreds of independent domains plus private instances that are never externally visible. Any percentage quoted for it is invented.

**It suits** a technically competent person who wants full control of their search: which engines answer, in what proportion, with what filters, on hardware they own, under a license nobody can revoke. The bang syntax and category system make it a good research tool, and for a self-hoster the privacy guarantee is a property of a machine rather than a promise from a company — a categorically stronger thing.

**It does not suit** anyone who wants search to just work. A non-technical user pointed at a random public instance gets a slower, flakier, worse-ranked Google with an anonymous stranger in the middle — worse than [DuckDuckGo](/duckduckgo/) or Startpage on every axis they care about, privacy included, since those at least have an accountable company behind them. Self-hosting carries real ongoing costs: CAPTCHAs, engine tuning, threads about 429 errors. It is not install-and-forget.

## Frequently asked questions

### Does SearXNG have its own index?

No. SearXNG has no crawler, no user-agent and no stored documents of any kind. Every result comes from a third-party engine, fetched live at query time and merged into one page. This is the defining property of metasearch software, and it means SearXNG can never return anything that none of its configured upstream engines already had.

### Is SearXNG a search engine or a program?

It is a program. There is no company, no owner and no canonical website: SearXNG is AGPL-licensed software that you install on a server, or that a volunteer has installed on theirs and made public. That distinction matters because it means results, engine selection, logging and jurisdiction are all decided by whoever runs the particular instance you happen to be using.

### Which SearXNG instance should I use?

There is no single right answer, and that is the point. Public instances are listed at searx.space, which publishes uptime, response time, TLS and CSP grades, HTML modification checks, version and whois location for each one. What it cannot publish is whether the operator logs your queries. If that matters to you, the documentation's own advice applies: run your own.

### Is using a public SearXNG instance private?

It is private from the upstream engines, which see the instance's server rather than you. It is not private from the instance operator, who is typically anonymous, unaudited and technically able to log every query you send. Trust is transferred, not eliminated. Self-hosting removes that risk entirely but makes every query attributable to your own IP address at the upstream engine.

### What is the difference between searx and SearXNG?

They are different projects. searx was created by Adam Tauber starting in October 2013; contributors forked it into SearXNG in mid-2021, citing slow bug fixes and the need for engine reliability metrics and user themes. The original searx repository was archived on 7 September 2023 and is no longer maintained. SearXNG is the live fork and remains under active development.

### Why do SearXNG results sometimes disappear or fail?

Because upstream engines block it. A 2023 GitHub issue documented Google blocking fresh instances after about five consecutive searches, with instances that had a working Google engine dropping from 66 of 91 to 25 within days. Rate limiting and HTTP 429 errors remain live issues, which is why searx.space publishes per-engine crash rates and the project ships a Limiter component.

### Does SearXNG cost anything or show ads?

No on both counts. SearXNG is AGPL-3.0 free software with no advertising, no subscription tier, no API metering and no telemetry, and there is no company behind it to monetise anything. Public instances are funded by their operators, usually personally. That is also the model's weak point: instances disappear when an operator loses interest or stops paying for the bandwidth.

### Can I use SearXNG as a search API for an AI agent?

Technically yes, and many self-hosted LLM agents and RAG pipelines do exactly that, using a local instance for free unmetered JSON search. Do it on your own instance. Pointing an agent at a volunteer's public instance drives the rate limiting and CAPTCHA blocking that degrades the service for human users, and gives you no reliability guarantee for a production system.

## Sources

* [docs.searxng.org/](https://docs.searxng.org/)
* [github.com/searxng/searxng](https://github.com/searxng/searxng)
* [github.com/searxng/searxng/issues/2515](https://github.com/searxng/searxng/issues/2515)
* [searx.space/](https://searx.space/)
* [en.wikipedia.org/wiki/SearXNG](https://en.wikipedia.org/wiki/SearXNG)
* [en.wikipedia.org/wiki/Searx](https://en.wikipedia.org/wiki/Searx)
* [ngi.eu/blog/2019/12/05/searx-privacy-respecting-meta-search-engine-ngi/](https://ngi.eu/blog/2019/12/05/searx-privacy-respecting-meta-search-engine-ngi/)
* [nlnet.nl/project/SearxRelease/](https://nlnet.nl/project/SearxRelease/)

## Quick facts

Results from

Up to 269 third-party services, per instance

Own crawler

None; no index at all

Operator

Community project; no company

License

AGPL-3.0

Launched

Forked from searx, mid-2021

Predecessor

searx (2013); archived 7 Sep 2023

Business model

None: no ads, no subscriptions

Public instances

About 70 well maintained (docs, Aug 2026)

AI answers

None built in

Market share

Not measurable by any method

[Visit docs.searxng.org](https://docs.searxng.org/)

## More meta-search engines

* [Presearch](/presearch/)
* [Dogpile](/dogpile/)
* [WebCrawler](/webcrawler/)

## Related search engines

[![Presearch logo (In use since 2021)](/assets/logos/presearch-current.1395fdeb.webp)Meta-search enginesPresearchCrypto-rewarded search run over volunteer nodes that fetch other engines' results; own-index claim unverified.Resold results](/presearch/)

[![Dogpile logo (In use by January 2019)](/assets/logos/dogpile-current.33411b96.webp)Meta-search enginesDogpileMetasearch engine launched in 1996, now a System1 property. No crawler of its own — it merges feeds bought from other engines.Resold results](/dogpile/)

[![WebCrawler logo (2018–present)](/assets/logos/webcrawler-current.7c57678b.webp)Meta-search enginesWebCrawlerThe first full-text web search engine (1994). Today a System1-owned front end serving outside feeds, with no index of its own.Resold results](/webcrawler/)

SearchEngines.Net

An independent reference on search engines — who runs which index, who resells whose results, and how any of it works.

**Independent reference.** SearchEngines.Net is not a search engine and is not affiliated with any company listed here. Nothing on this site is for sale, no placement can be bought, and no engine has reviewed these pages before publication. Corrections are welcome — see [contact](/contact/).

## Browse

[All search engines](/directory/)[Major global engines](/major-global-search-engines/)[Privacy engines](/privacy-search-engines/)[AI search engines](/ai-search-engines/)[Engines that closed](/defunct-search-engines/)

## Learn

[Guides](/guides/)[How search engines work](/guides/how-search-engines-work/)[The history of search](/guides/history-of-search-engines/)[Change your default engine](/how-to/change-default-search-engine/)[Glossary](/glossary/)

© 2026 SearchEngines.Net[About](/about/) · [Contact](/contact/) · [Privacy](/privacy-policy/) · [Terms](/terms/) · [Disclaimer](/disclaimer/) · [Sitemap](/sitemap.xml) · [EntityMap](/entitymap.html)

[Top](#top)