---
n: 8
url: https://www.ssdnodes.com/learn/searx-vs-searxng
title: Searx vs SearXNG: is Searx dead?
fetched_at: 2026-11-17T05:51:33.889413Z
---

 

[SSD Nodes Learn](/learn) [Hosting plans →](/learn/deals/performance-vps?from=searx-vs-searxng) 

[Guides](/learn) [About](https://www.ssdnodes.com/about/) [SSD Nodes VPS](/learn/deals/performance-vps?from=searx-vs-searxng) Language: English ▾ 
* ✓English
* [ Français](https://www.ssdnodes.com/learn/lang/fr/searx-vs-searxng)
* [ 中文](https://www.ssdnodes.com/learn/lang/zh-hans/searx-vs-searxng)
* [ العربية](https://www.ssdnodes.com/learn/lang/ar/searx-vs-searxng)
* [ हिन्दी](/learn/lang/hi)
* [ Tiếng Việt](/learn/lang/vi)
* [ Español](https://www.ssdnodes.com/learn/lang/es/searx-vs-searxng)
* [ Português](https://www.ssdnodes.com/learn/lang/pt/searx-vs-searxng)
* [ Deutsch](https://www.ssdnodes.com/learn/lang/de/searx-vs-searxng)
* [ Русский](https://www.ssdnodes.com/learn/lang/ru/searx-vs-searxng)
* [ বাংলা](/learn/lang/bn)
* [ 日本語](https://www.ssdnodes.com/learn/lang/ja/searx-vs-searxng)
* [ 한국어](https://www.ssdnodes.com/learn/lang/ko/searx-vs-searxng)
* [ Italiano](https://www.ssdnodes.com/learn/lang/it/searx-vs-searxng)
* [ Türkçe](https://www.ssdnodes.com/learn/lang/tr/searx-vs-searxng)
* [ فارسی](https://www.ssdnodes.com/learn/lang/fa/searx-vs-searxng)
* [ polski](https://www.ssdnodes.com/learn/lang/pl/searx-vs-searxng)
* [ Nederlands](/learn/lang/nl)
* [ ไทย](https://www.ssdnodes.com/learn/lang/th/searx-vs-searxng)
* [ Українська](/learn/lang/uk)
* [ Bahasa Indonesia](https://www.ssdnodes.com/learn/lang/id/searx-vs-searxng)
* [ Bahasa Melayu](/learn/lang/ms)
* [ Naijá](/learn/lang/pcm)
* [ मराठी](/learn/lang/mr)
* [ 繁體中文](https://www.ssdnodes.com/learn/lang/zh-hant/searx-vs-searxng)
* [ Filipino](/learn/lang/tl)
* [ Kiswahili](/learn/lang/sw)
* [ עברית](/learn/lang/he)
* [ اردو](/learn/lang/ur)
* [ தமிழ்](/learn/lang/ta)
* [ తెలుగు](/learn/lang/te)

[](#) × 

[Blog](/learn) › [Guides](/learn/guides) › Searx vs SearXNG: is Searx dead? 

[Guides](/learn/guides) ![Matt Connor](https://www.ssdnodes.com/learn/assets/matt-connor.webp)By [Matt Connor](https://www.ssdnodes.com/learn/about) 2026-10-18 

# Searx vs SearXNG: is Searx dead?

Searx has taken no code commit since 2023 and SearXNG carries the project now. Check the status yourself, then see what changed for a new instance.

## Searx or SearXNG: which one should you install?

Searx and SearXNG are two different projects with almost the same name, and only one of them still gets fixes. Install SearXNG. The original Searx has taken no code commit since April 2023, and its own README states the position in one line: "Searx is no longer maintained."

That leaves a practical problem rather than a philosophical one. The two projects share a screenshot, most of a configuration file and half a name, so a guide written for one looks like it applies to the other. It does not. The settings file lives somewhere else, the bot protection is new, and the package name is gone from current Ubuntu. What follows is the split itself, the commands to check the status for yourself, and the list of things that changed for the person standing an instance up.

## What Searx is, and where SearXNG came from

Searx is a metasearch engine. It keeps no index of its own. It takes your query, forwards it to other search services such as Bing, DuckDuckGo or Wikipedia, then merges what comes back into one results page. The benefit is that those services see the server's address instead of yours. The cost is maintenance. Every engine is a small piece of code that parses somebody else's HTML or API, so an engine breaks whenever that upstream changes. A metasearch engine is only as healthy as the people fixing its engine modules.

The searx repository was created in October 2013\. In April 2021 a former maintainer started SearXNG as a fork of it. The "NG" stands for next generation. Searx's own README describes both projects side by side, and that description is still the clearest summary of the split:

> SearxNG is a fork of searx, created by a former maintainer of searx.

> SearxNG has rolling releases, dependencies updated more frequently, and engines are fixed faster.

The disagreement behind the fork was about diagnostics. Searx treated usage data as something an instance should not hold, and its default settings say so out loud: `enable_stats: False # activate /stats page - note: it may leak usage data`. SearXNG made the opposite call, and ships `enable_metrics: true` in its defaults. Those metrics are what fill the response time bars and the error pages that make a broken engine easy to find and fix. Both positions are defensible. Only one of them kept shipping code.

Free guide: VPS Security — 6 Critical Steps to Secure Your VPS Servers

The server-hardening playbook we hand new customers — 17 pages, with the exact commands. Free, by email.

Send me the guide 

Company 

One confirmation click, then the PDF is in your inbox. Unsubscribe anytime.

## Is Searx dead? How to check for yourself

"Dead" is not a status GitHub reports, so read the two signals that exist and decide. The first is whether the repository is archived, and when it last saw a push.

Copy

```
curl -s https://api.github.com/repos/searx/searx | jq -r '.archived, .pushed_at'
curl -s https://api.github.com/repos/searxng/searxng | jq -r '.archived, .pushed_at'
```

On 18 October 2026 the first command prints `false` and `2026-05-14T10:02:22Z`. The second prints `false` and a recent timestamp, usually from the last day or two. Note the first value. The searx repository is not archived and nobody locked the door, which is why the question keeps coming back.

`pushed_at` is a weak signal on its own, because it moves for a push to any branch, including a one line documentation change. Read the commit list instead.

Copy

```
curl -s 'https://api.github.com/repos/searx/searx/commits?per_page=5' \
  | jq -r '.[] | .commit.committer.date[:10] + "  " + (.commit.message | split("\n")[0])'
```

As of 18 October 2026 that prints:

Copy

```
2026-05-14  [doc] add hister reference
2023-09-07  Searx is no longer maintained
2023-04-05  Fix quoting issue in search_operator plugin (#3479)
2023-04-04  Bump pallets-sphinx-themes from 2.0.2 to 2.0.3 (#3450)
2023-04-04  Update searx.data - update_wikidata_units.py (#3454)
```

Read it from the bottom up. Ordinary work stops in April 2023\. The September 2023 commit is the maintainers writing the notice into the README. The single commit since then is documentation, because the original author moved to Hister, a search tool that indexes pages and files you choose instead of querying other engines. That is a different idea, and a useful one if what you actually want is [a personal search engine over your own content](/learn/self-host-hister-personal-search-engine).

The second signal is packaging, and packaging is what most old tutorials quietly depend on.

* PyPI holds twenty `searx` releases, from 0.1.2 in January 2014 to 0.17.0 in July 2020, and every one is still downloadable. `pip install searx` succeeds and gives you the newest of them, 0.17.0, which is code from nine months before the fork existed.
* Debian shipped searx 1.1.0 in Debian 12 (bookworm) and still carries it in unstable. It was removed from testing in October 2023, so Debian 13 (trixie) has no searx package at all.
* Ubuntu last shipped it in 23.10 (mantic), at version 1.1.0\. The last LTS release with it is 22.04, at version 1.0.0, and the package was deleted from 24.04 before that release came out. On Ubuntu 24.04, `sudo apt install searx` ends with `E: Unable to locate package searx`.
* searx.space, the public instance directory the project always pointed people at, now lists SearXNG instances.

So here is the honest status. The code is public, it still runs, and you can clone and start it today. What you do not get is engine fixes or security updates, and for a metasearch engine that is the whole job. Engines rot on somebody else's schedule. An unmaintained instance returns fewer results every month without anybody touching the box.

## What the fork changed for a new instance

### The settings file moved, and it is now an overlay

On Searx you edited `searx/settings.yml` inside the source tree. On SearXNG the file lives at `/etc/searxng/settings.yml`, and the process finds it through the `SEARXNG_SETTINGS_PATH` environment variable. The template the installer copies there is short:

Copy

```
use_default_settings: true

general:
  debug: false
  instance_name: "SearXNG"

search:
  safe_search: 2
  autocomplete: 'duckduckgo'
  formats:
    - html

server:
  # Is overwritten by ${SEARXNG_SECRET}
  secret_key: "ultrasecretkey"
  limiter: true
  image_proxy: true

valkey:
  # URL to connect valkey database. Is overwritten by ${SEARXNG_VALKEY_URL}.
  url: valkey://localhost:6379/0
```

`use_default_settings: true` is the line that changes how you work. With it, your file holds overrides only, and every key you leave out comes from the defaults shipped inside the package. Without it, your file has to describe the whole configuration, engine by engine. That is how people end up with an instance that starts cleanly and finds nothing. An old Searx settings file pasted into this path is a complete configuration with different key names, so it takes the second route and takes it badly.

### The secret key stops the process

Copy

```
sudo -H sed -i -e "s/ultrasecretkey/$(openssl rand -hex 16)/g" \
              "/etc/searxng/settings.yml"
```

Run that once, after copying the template. Skip it and SearXNG logs one line and exits with status 1, because `webapp.py` compares the key against the template value before it serves anything:

Copy

```
server.secret_key is not changed. Please use something else instead of ultrasecretkey.
```

The check is skipped when `general.debug` is true, so an instance can run fine in a debug session and then refuse to start under systemd or in a container. A container restarting in a loop with that line in `docker compose logs` is this check firing, not a broken image.

### The limiter is new, and it needs Valkey

Searx had no rate limiting inside the application. Public Searx instances put separate services in front of it, filtron for request filtering and morty for proxying result content. Neither repository has taken a commit since January 2023: filtron's last commit is from that month, and morty's is from April 2021.

SearXNG does that work itself. Rate limiting and bot detection are the limiter, switched on with `server.limiter`. It is `false` in the shipped defaults and `true` in the installer's template, and it needs a Valkey database to hold its counters. Valkey is a fork of Redis, and Ubuntu 24.04 packages it:

Copy

```
sudo apt install -y valkey-server
```

Copy

```
server:
  limiter: true

valkey:
  url: valkey://localhost:6379/0
```

Guides written before that rename configure a `redis:` block instead, so copy the key name from the current limiter documentation. Fine tuning lives in a second file, `/etc/searxng/limiter.toml`, and `server.public_instance: true` turns on the stricter bot detection a public instance needs, including the link token method. The visible result is that some requests are answered with HTTP 429 instead of results, including your own requests if you script against the instance. That has its own page here: [why a SearXNG instance answers 429 Too Many Requests](/learn/searxng-rate-limits-and-429-errors).

### Engines suspend themselves, and the timeouts are long

When an upstream service answers with a CAPTCHA or a rate limit page, SearXNG raises a typed exception and stops asking that engine for a set time instead of retrying into a block. The defaults ship in `searx/settings.yml` under `search.suspended_times`. These are the 6 published values as of October 2026:

ChartSearXNG default engine suspension times, in seconds

The data behind this chart

[
  {
    "label": "SearxEngineAccessDenied",
    "suspend_seconds": "180"
  },
  {
    "label": "SearxEngineCaptcha",
    "suspend_seconds": "3,600"
  },
  {
    "label": "SearxEngineTooManyRequests",
    "suspend_seconds": "180"
  },
  {
    "label": "cf_SearxEngineCaptcha",
    "suspend_seconds": "1,296,000"
  },
  {
    "label": "cf_SearxEngineAccessDenied",
    "suspend_seconds": "86,400"
  },
  {
    "label": "recaptcha_SearxEngineCaptcha",
    "suspend_seconds": "604,800"
  }
]

A plain access denied answer parks that engine for **180** seconds. A CAPTCHA parks it for **3,600** seconds. A Cloudflare CAPTCHA parks it for **1,296,000** seconds, which is fifteen days, and a Google reCAPTCHA for **604,800** seconds, which is a week. The long values are deliberate, because asking again after a service has already flagged the address is how an instance IP gets blocked for good.

While an engine is suspended the results page skips it and reports it in the sidebar block titled "Messages from the search engines", and `/stats/errors` lists what failed. A fresh instance returning thin results is usually showing you this, not a broken install.

### The JSON API is off by default

The shipped default is `formats: [html]` and nothing else, so the API that every script wants is closed until you open it.

Copy

```
curl -s -o /dev/null -w '%{http_code}\n' \
  'http://127.0.0.1:8888/search?q=test&format=json'
```

That prints `403`, because the search route calls `flask.abort(403)` when the requested format is not listed in `search.formats`. Add the format and restart the service:

Copy

```
search:
  formats:
    - html
    - json
```

The searx settings file has no `formats` key at all, so its JSON output was simply there for the asking. Every script and snippet from that era assumes the same, and the failure mode is a bare 403 with no explanation. If you are wiring an instance into tooling, [giving an agent a SearXNG endpoint to search with](/learn/browser-search-skill-searxng-agents) starts with this one setting.

## Why copy-pasted Searx tutorials fail

Each of these lines appears in guides that still rank, and each one fails or misleads on a current install.

* `sudo apt install searx` on Ubuntu 24.04 stops at `E: Unable to locate package searx`, because the package last shipped in 23.10 and was deleted from 24.04 before release.
* `pip install searx` succeeds and installs 0.17.0 from July 2020\. Nothing warns you that it predates the fork.
* `git clone https://github.com/asciimoo/searx` still works, because GitHub redirects the old owner name. It checks out the current default branch, where a May 2026 documentation commit sits on application code that stopped changing in April 2023.
* Steps that edit `searx/settings.yml` in the source tree change nothing on SearXNG, which reads `/etc/searxng/settings.yml`.
* Steps that install filtron or morty are rebuilding parts SearXNG already contains.
* A `redis:` URL for the limiter is one rename behind the current `valkey:` key.

SearXNG guides rot too, and the clone URL is the fastest way to date one. The compose files used to live in a separate `searxng-docker` repository. That repository is now archived, its last push was in March 2026, and its files moved into `container/` in the main repository. The current container quickstart from the documentation is:

Copy

```
mkdir -p ./searxng/core-config/
cd ./searxng/
curl -fsSL \
    -O https://raw.githubusercontent.com/searxng/searxng/master/container/docker-compose.yml \
    -O https://raw.githubusercontent.com/searxng/searxng/master/container/.env.example
cp -i .env.example .env
nano .env
docker compose up -d
```

Edit `.env` before the last command. The image maps environment variables onto settings keys, so `SEARXNG_SECRET` becomes `server.secret_key` and `SEARXNG_BASE_URL` becomes `server.base_url`. The scripted host install is a different path with the same outcome:

Copy

```
git clone https://github.com/searxng/searxng.git searxng
cd searxng
sudo -H ./utils/searxng.sh install all
```

That creates the `searxng` user, the virtual environment under `/usr/local/searxng` and the uWSGI service, which is the reference setup in the SearXNG documentation. The longer walkthrough of that path is [installing SearXNG on your own VPS](/learn/searxng-self-hosted-search).

## Public instance or your own instance

A public instance is somebody else's server terminating your TLS (transport layer security) connection, so the software there reads your query as plain text. SearXNG's own documentation puts the trust question plainly: you have to trust the administrator, and you cannot know whether requests are logged, aggregated or passed to a third party. The visible list is short and complete. The operator's stack can see the query text, the time, the IP address the request arrives from, the browser user agent, and the preference cookie holding your settings. The operator also controls the code, so any patch they apply runs on every search you make there.

One default makes this easier to log by accident. Searx sent searches as POST. SearXNG ships `method: "GET"`, with the comment that POST keeps search queries out of the browser history but causes usability problems. With GET the query sits in the request line, so it lands in the reverse proxy access log by default, and in the browser history. That is ordinary web server behaviour. It is worth knowing before you choose whose server it happens on.

Running your own instance moves the trust rather than removing it. You control the code and the logs, and if you would rather not publish a hostname or a TLS certificate for a single user box at all, [reaching it over a v3 onion service](/learn/host-onion-site-on-a-vps) keeps the instance off public DNS while you still get to it from anywhere. In exchange, the upstream engines see one address for all of your searches, and on a single user instance every query traces back to you instead of mixing into a crowd. A busy public instance gives you that crowd and takes the logs away from you. Pick the property you care about, and if you want the full risk list first, [whether SearXNG is safe to use](/learn/is-searxng-safe) works through it. Location history deserves the same thinking with higher stakes, because a phone reporting its position all day reveals more than any search log, and [comparing self-hosted location trackers](/learn/self-hosted-location-tracking-apps) is the place to start if you want that data on a box you control.

One practical note for a VPS. Datacentre address ranges get flagged faster than home connections, so a new instance meets CAPTCHAs on some engines within the first few searches. That is the suspension behaviour above doing its job, not a misconfiguration. If the same engines keep coming back blocked after their suspension expires, [reading the actual error before changing anything](/learn/fix-searxng-engine-captcha-errors) will save you guessing at fixes.

## If you already run a Searx instance

Nothing breaks the day you read this. The box keeps working until the next upstream change breaks another engine, and then it stays broken. Plan the move, and do not port the configuration file. Start from the SearXNG template, then re-add only what you deliberately changed: the instance name, `safe_search`, the engines you enabled or disabled by name, and your interface defaults. Engine names and options changed in the fork, so check each one against the current documentation rather than assuming the key still exists. Filtron rules and a morty URL have no equivalent, because those jobs moved inside the application.

Run the new instance on a different port while the old one is still up. It is working when the front page returns 200, a search returns results from more than one engine, and `/stats/errors` is either empty or listing failures you understand. Then move the reverse proxy over and stop the old service.

Free guide: VPS Security — 6 Critical Steps to Secure Your VPS Servers

The server-hardening playbook we hand new customers — 17 pages, with the exact commands. Free, by email.

Send me the guide 

Company 

One confirmation click, then the PDF is in your inbox. Unsubscribe anytime.

## FAQ

### Is Searx dead in 2026?

The repository is not archived, so nothing stops you cloning it, but the project is not maintained. The last code commit landed in April 2023, and the README carries the line "Searx is no longer maintained." Check it yourself with `curl -s https://api.github.com/repos/searx/searx | jq -r '.pushed_at'` and then read the recent commit messages, because a push date alone can come from a documentation edit. For a metasearch engine, unmaintained means results get worse on their own, since every engine module depends on an upstream site that keeps changing.

### Can I still install Searx with apt or pip?

Not on current systems, and not usefully where you can. Ubuntu last packaged searx in 23.10 at version 1.1.0, and the last LTS release with it is 22.04 at version 1.0.0\. It was deleted from 24.04 before release, so `sudo apt install searx` on 24.04 returns `E: Unable to locate package searx`. Debian shipped 1.1.0 in Debian 12 and dropped it from testing in October 2023, so Debian 13 has no package. PyPI still serves every searx release, and the newest is 0.17.0 from July 2020, which is older than the fork itself. Install SearXNG instead.

### Will my old searx settings.yml work in SearXNG?

No. Copy the values, not the file. SearXNG reads `/etc/searxng/settings.yml` and expects `use_default_settings: true` at the top, so your file acts as an overlay on the shipped defaults. An old searx file is a full configuration with different key names, and it has no `limiter`, no `valkey` block and no `formats` list. Start from the template at `utils/templates/etc/searxng/settings.yml` and re-add your changes one at a time.

### Why does my own SearXNG instance return fewer results than a public one?

Some engines are suspended. When an engine answers with a CAPTCHA or a rate limit page, SearXNG stops querying it for a fixed time, from 180 seconds for a plain refusal up to 1,296,000 seconds for a Cloudflare CAPTCHA. The results page reports this under "Messages from the search engines", and `/stats/errors` lists the failures with their reasons. Datacentre addresses are flagged sooner than home connections, so a new VPS instance sees it early.

### Should I use a public SearXNG instance or run my own?

Run your own if you want control of the code and the logs, and accept that upstream engines then see a single address for all of your searches. Use a public instance if mixing your queries with other people's matters more to you than knowing what gets logged. On a public instance the operator can see the query text, the time, your IP address and your user agent, and can change the code whenever they like. A stated logging policy cannot be verified from outside.

## Was this article useful?

Yes No Report a mistake 

Your email (optional) 

Only if you want a reply. We never add it to a mailing list.

Send 

![Matt Connor](https://www.ssdnodes.com/learn/assets/matt-connor.webp) 

Written by

[Matt Connor](https://www.ssdnodes.com/learn/about) — Founder & CEO, SSD Nodes

Founder & CEO of SSD Nodes, the VPS hosting provider he has run for 15 years. These guides cover the Linux server work that goes with it: setup, security, and networking.

[Read full bio →](https://www.ssdnodes.com/learn/about) 

[#searxng](/learn?tag=searxng)[#searx](/learn?tag=searx)[#search](/learn?tag=search)[#privacy](/learn?tag=privacy)[#self-hosting](/learn?tag=self-hosting) 

## Related

* [What the n8n Sustainable Use License allows](/learn/n8n-sustainable-use-license-explained) Guides
* [Add an Onion-Location header to your site](/learn/onion-location-header-for-your-site) Guides
* [Coding agent telemetry: what gets sent](/learn/coding-agent-telemetry-what-gets-sent) Guides
* [Tailscale pricing and plans: what you really pay](/learn/tailscale-pricing-explained) Guides

Free guide: VPS Security — 6 Critical Steps to Secure Your VPS Servers

The server-hardening playbook we hand new customers — 17 pages, with the exact commands. Free, by email.

[Get the free guide →](/learn/get/6-steps-server-security) 

× 

Free guide: VPS Security — 6 Critical Steps to Secure Your VPS Servers

17 pages, exact commands. Get the PDF by email.

Send me the guide 

Company 

One confirmation click, then the PDF is in your inbox. Unsubscribe anytime.

© SSD Nodes — guides for people who run their own servers. [RSS](https://www.ssdnodes.com/learn/rss.xml) · [Sitemap](https://www.ssdnodes.com/learn/sitemap.xml)