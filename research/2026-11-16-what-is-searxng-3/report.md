SearXNG is a free, open-source metasearch engine written in Python that aggregates results from dozens of upstream search services (Google, Bing, DuckDuckGo, Wikipedia, and many more) while not tracking or profiling its users [1][2][5]. It began in mid-2021 as a fork of the earlier searx project and is licensed under the GNU Affero General Public License (AGPL-3.0) [2][5]. Users can access it through volunteer-run public instances listed at searx.space, or install and run their own private instance [1][4][5].

## What it is

SearXNG is a metasearch engine: it has no crawler, no user-agent, and no stored index of any kind [4]. Every result comes from a third-party engine, fetched live at the moment a query is submitted, and merged into a single results page [4]. It is free software with 100% open code, and the community is open to contributions from anyone [1]. The project is driven by an open community and developed on GitHub under the `searxng` organization by volunteer maintainers [4][5]. As of the documentation build referenced here (2026.11.17), the repository holds 9,892 commits on master, 39.6k stars, and 3.6k forks [3].

## How it works

A user submits a query to a SearXNG instance; the instance forwards that query to a configurable set of upstream search engines, strips identifying data from the outbound requests, merges and re-ranks what comes back, and displays one combined page [4]. The documentation lists up to 260 configured search services [5]; Wikipedia cites 251 possible search services as of 2026 [2]; and an independent reference page cites up to 269 [4]. Results can be grouped into categories including General, Images, Videos, News, Social Media, Music, Files, IT, and Science [2]. A bang syntax (e.g., `!wp paris`) lets users force a specific engine or category, and `!!wfr` redirects directly to an external engine [2][7].

SearXNG also ships with answerers (deterministic lookups such as calculations and Wikidata facts), infoboxes, a calculator, a unit converter, hash functions, and other plugins [1][5]. It explicitly ships no LLM answer engine, no chat interface, and no AI summary [4].

## Privacy model

SearXNG protects privacy in three ways: it removes private data (cookies, IP address, browser fingerprint) from requests sent to upstream search services; it does not forward anything from third-party services through search engines (e.g., no advertisements); and it removes private data from requests going to the result pages themselves [6]. Cookies and JavaScript are optional [5]. SearXNG can be configured to route queries through a proxy or the Tor network for additional anonymity [5][6]. It does not serve ads or tracking content [6].

On a public instance, the user must trust the instance administrator, who can technically log every query, and whose stated logging policy cannot be independently verified [6][8]. Self-hosting eliminates the need to trust a stranger but means upstream engines see a single IP address for all of that user's searches [6][8].

## Instances and deployment

SearXNG is server-side software hosted by many instances, both public and private [2]. A directory of public instances is maintained at searx.space, which publishes uptime, response time, TLS and CSP grades, HTML modification checks, version, and whois location for each [2][4]. The documentation cites about 70 well-maintained instances [5]. Private instances can run on a local network, a company VPN, or a single user's desktop [6]. Installation is supported via Docker containers, a scripted host installer, or step-by-step manual setup with uWSGI, NGINX, or Apache [5].

SearXNG has no business model: no advertising, no subscriptions, no API metering, no telemetry, and no company behind it [4]. Public instances are funded by their operators, usually out of pocket, which is the project's chief sustainability risk [4].

## Features and syntax

Beyond basic web search, SearXNG supports:

- **Engine and category selection** via `!` prefix (e.g., `!images Wau Holland`, `!map paris`) [7]
- **Language filtering** via `:` prefix (e.g., `:fr !wp Wau Holland`) [7]
- **External bangs** via `!!` prefix, redirecting directly to a DuckDuckGo-style external search [7]
- **Automatic redirect** to the first result via `!!` in the query [7]
- **Special queries** such as `random uuid`, `avg 123 548`, `md5 lorem ipsum`, and `user-agent` [7]
- **OpenSearch support** for adding SearXNG to a browser's default search bar [1]
- **58 translations** available via Weblate [5]

## History and relationship to searx

Work on the predecessor project **searx** began in October 2013, created by Adam Tauber, inspired by the Seeks project [4][8]. It received European public funding through NGI Zero and NLnet around 2019 [4]. In mid-2021, contributors forked searx into SearXNG, citing slow bug fixes and the need for engine reliability metrics and user themes [4]. The "NG" stands for "next generation" [8]. SearXNG has rolling releases, dependencies updated more frequently, and engines fixed faster than searx had been [8]. On 7 September 2023, the original searx repository was effectively archived and declared "no longer maintained" [4][8]. SearXNG is now the sole actively maintained line of the project [4]. The SearXNG documentation build string referenced in these sources reads 2026.11.17+cf3c20177 [1][5][6][7].

## Limitations and operational considerations

Because SearXNG has no index, its results are only as good as the upstream engines it queries; when an upstream engine stops responding, results simply get thinner [4]. A notable incident in June 2023 saw Google actively blocking SearXNG instances, causing tracked instances with a working Google engine to fall from 66 of 91 to 25 within days [4]. Rate limiting, HTTP 429 errors, and CAPTCHA blocks remain ongoing operational concerns [4][8]. When an upstream engine answers with a CAPTCHA or rate-limit page, SearXNG suspends that engine for a set period (180 seconds for a plain refusal up to 1,296,000 seconds / 15 days for a Cloudflare CAPTCHA) [8].

SearXNG has become a de facto search backend for AI systems: self-hosted LLM agents and retrieval-augmented generation pipelines routinely run a local instance for free, unmetered JSON search [4]. The JSON API is off by default (`formats: [html]`) and must be explicitly enabled in settings [8]. SearXNG ships no generative-AI answers of any kind [4].

## Where to find it

- Source code: github.com/searxng/searxng [1][3]
- Documentation: docs.searxng.org [1][2][3][5]
- Public instances: searx.space [1][2][5]
- Community chat: #searxng:matrix.org [1][5]
- Translations: translate.codeberg.org/projects/searxng [1][5]

## Sources

[1] About SearXNG — https://docs.searxng.org/user/about.html

[2] Contents — https://en.wikipedia.org/wiki/SearXNG

[3] Navigation Menu — https://github.com/searxng/searxng

[4] SearXNG — https://www.searchengines.net/searxng/

[5] Welcome to SearXNG — https://docs.searxng.org/

[6] Why use a private instance? — https://docs.searxng.org/own-instance.html

[7] Search syntax — https://docs.searxng.org/user/search-syntax.html

[8] Searx vs SearXNG: is Searx dead? — https://www.ssdnodes.com/learn/searx-vs-searxng
