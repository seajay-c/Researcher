---
n: 7
url: https://docs.searxng.org/user/search-syntax.html
title: Search syntax
fetched_at: 2026-11-17T05:50:37.537206Z
---

 

Contents Menu Expand Light mode Dark mode Auto light/dark, in light mode Auto light/dark, in dark mode [Skip to content](#furo-main-content) 

[SearXNG Documentation (2026.11.17+cf3c20177)](../index.html) 

[ ![Logo](../_static/searxng-wordmark.svg) SearXNG Documentation (2026.11.17+cf3c20177) ](../index.html)

* [User information](index.html)
  * [Search syntax](#)
  * [Configured Engines](configured%5Fengines.html)
  * [About SearXNG](about.html)
* [Why use a private instance?](../own-instance.html)
* [Administrator documentation](../admin/index.html)
  * [Settings](../admin/settings/index.html)
    * [settings.yml](../admin/settings/settings.html)
    * [engines:](../admin/settings/settings%5Fengines.html)
    * [brand:](../admin/settings/settings%5Fbrand.html)
    * [general:](../admin/settings/settings%5Fgeneral.html)
    * [search:](../admin/settings/settings%5Fsearch.html)
    * [server:](../admin/settings/settings%5Fserver.html)
    * [ui:](../admin/settings/settings%5Fui.html)
    * [preferences:](../admin/settings/settings%5Fpreferences.html)
    * [redis:](../admin/settings/settings%5Fredis.html)
    * [valkey:](../admin/settings/settings%5Fvalkey.html)
    * [outgoing:](../admin/settings/settings%5Foutgoing.html)
    * [categories\_as\_tabs:](../admin/settings/settings%5Fcategories%5Fas%5Ftabs.html)
    * [plugins:](../admin/settings/settings%5Fplugins.html)
  * [Installation](../admin/installation.html)
  * [Installation container](../admin/installation-docker.html)
  * [Installation Script](../admin/installation-scripts.html)
  * [Step by step installation](../admin/installation-searxng.html)
  * [Granian](../admin/installation-granian.html)
  * [uWSGI](../admin/installation-uwsgi.html)
  * [NGINX](../admin/installation-nginx.html)
  * [Apache](../admin/installation-apache.html)
  * [SearXNG maintenance](../admin/update-searxng.html)
  * [Answer CAPTCHA from server’s IP](../admin/answer-captcha.html)
  * [Favicons](../admin/searx.favicons.html)
  * [Limiter](../admin/searx.limiter.html)
  * [Administration API](../admin/api.html)
  * [Architecture](../admin/architecture.html)
  * [List of plugins](../admin/plugins.html)
  * [Buildhosts](../admin/buildhosts.html)
* [Developer documentation](../dev/index.html)
  * [Development Quickstart](../dev/quickstart.html)
  * [Git Commits & Change Management](../dev/commits.html)
  * [How to contribute](../dev/contribution%5Fguide.html)
  * [Extended Types](../dev/extended%5Ftypes.html)
  * [Engine Implementations](../dev/engines/index.html)
    * [Engine Library](../dev/engines/enginelib.html)
    * [SearXNG’s engines loader](../dev/engines/engines.html)
    * [Engine Overview](../dev/engines/engine%5Foverview.html)
    * [Demo Online Engine](../dev/engines/demo/demo%5Fonline.html)
    * [XPath Engine](../dev/engines/xpath.html)
    * [MediaWiki Engine](../dev/engines/mediawiki.html)
    * [JSON Engine](../dev/engines/json%5Fengine.html)
    * [500px](../dev/engines/online/500px.html)
    * [Alpine Linux Packages](../dev/engines/online/alpinelinux.html)
    * [Anna’s Archive](../dev/engines/online/annas%5Farchive.html)
    * [Arch Linux](../dev/engines/online/archlinux.html)
    * [arXiv](../dev/engines/online/arxiv.html)
    * [Astrophysics Data System (ADS)](../dev/engines/online/astrophysics%5Fdata%5Fsystem.html)
    * [Azure Resources](../dev/engines/online/azure.html)
    * [Bing Engines](../dev/engines/online/bing.html)
    * [Bpb](../dev/engines/online/bpb.html)
    * [Brave Engines](../dev/engines/online/brave.html)
    * [BT4G](../dev/engines/online/bt4g.html)
    * [ChinaSo](../dev/engines/online/chinaso.html)
    * [CORE](../dev/engines/online/core.html)
    * [Crossref](../dev/engines/online/crossref.html)
    * [Dailymotion](../dev/engines/online/dailymotion.html)
    * [Discourse Forums](../dev/engines/online/discourse.html)
    * [DuckDuckGo Engines](../dev/engines/online/duckduckgo.html)
    * [Europe PMC](../dev/engines/online/europepmc.html)
    * [Exa API Engine](../dev/engines/online/exaapi.html)
    * [Geizhals](../dev/engines/online/geizhals.html)
    * [Gitea](../dev/engines/online/gitea.html)
    * [Github Code](../dev/engines/online/github%5Fcode.html)
    * [GitLab](../dev/engines/online/gitlab.html)
    * [Google Engines](../dev/engines/online/google.html)
    * [Hugging Face](../dev/engines/online/huggingface.html)
    * [Jina Engine](../dev/engines/online/jina.html)
    * [Kagi Engines](../dev/engines/online/kagi.html)
    * [Lemmy](../dev/engines/online/lemmy.html)
    * [Marginalia Search](../dev/engines/online/marginalia.html)
    * [Mastodon](../dev/engines/online/mastodon.html)
    * [Moviepilot](../dev/engines/online/moviepilot.html)
    * [Matrix Rooms Search (MRS)](../dev/engines/online/mrs.html)
    * [Mwmbl Engine](../dev/engines/online/mwmbl.html)
    * [Odysee](../dev/engines/online/odysee.html)
    * [OpenAlex](../dev/engines/online/openalex.html)
    * [Open Library](../dev/engines/online/openlibrary.html)
    * [Peertube Engines](../dev/engines/online/peertube.html)
    * [Piped](../dev/engines/online/piped.html)
    * [PubMed](../dev/engines/online/pubmed.html)
    * [Qwant](../dev/engines/online/qwant.html)
    * [RadioBrowser](../dev/engines/online/radio%5Fbrowser.html)
    * [ReaderFunded](../dev/engines/online/readerfunded.html)
    * [Recoll Engine](../dev/engines/online/recoll.html)
    * [Repology](../dev/engines/online/repology.html)
    * [Reuters](../dev/engines/online/reuters.html)
    * [Semantic Scholar](../dev/engines/online/semantic%5Fscholar.html)
    * [Soundcloud](../dev/engines/online/soundcloud.html)
    * [Sourcehut](../dev/engines/online/sourcehut.html)
    * [Springer Nature](../dev/engines/online/springer.html)
    * [Startpage Engines](../dev/engines/online/startpage.html)
    * [Tagesschau API](../dev/engines/online/tagesschau.html)
    * [Torznab WebAPI](../dev/engines/online/torznab.html)
    * [Tube Archivist](../dev/engines/online/tubearchivist.html)
    * [Void Linux binary packages](../dev/engines/online/void.html)
    * [Wallhaven](../dev/engines/online/wallhaven.html)
    * [Wikimedia](../dev/engines/online/wikipedia.html)
    * [Yacy](../dev/engines/online/yacy.html)
    * [Yahoo Engine](../dev/engines/online/yahoo.html)
    * [Yandex Search API](../dev/engines/online/yandex%5Fapi.html)
    * [Z-Library](../dev/engines/online/zlibrary.html)
    * [Offline Concept](../dev/engines/offline%5Fconcept.html)
    * [Demo Offline Engine](../dev/engines/demo/demo%5Foffline.html)
    * [Command Line Engines](../dev/engines/offline/command-line-engines.html)
    * [NoSQL databases](../dev/engines/offline/nosql-engines.html)
    * [Local Search APIs](../dev/engines/offline/search-indexer-engines.html)
    * [SQL Engines](../dev/engines/offline/sql-engines.html)
    * [Tineye](../dev/engines/online%5Furl%5Fsearch/tineye.html)
  * [Result Types](../dev/result%5Ftypes/index.html)
    * [Result](../dev/result%5Ftypes/base%5Fresult.html)
    * [Main Search Results](../dev/result%5Ftypes/main%5Fresult.html)
      * [Main Results](../dev/result%5Ftypes/main/mainresult.html)
      * [Key-Value Results](../dev/result%5Ftypes/main/keyvalue.html)
      * [Code Results](../dev/result%5Ftypes/main/code.html)
      * [Paper Results](../dev/result%5Ftypes/main/paper.html)
      * [File Results](../dev/result%5Ftypes/main/file.html)
      * [Image Results](../dev/result%5Ftypes/main/image.html)
      * [Video Results](../dev/result%5Ftypes/main/video.html)
    * [Answer Results](../dev/result%5Ftypes/answer.html)
    * [Correction Results](../dev/result%5Ftypes/correction.html)
    * [Suggestion Results](../dev/result%5Ftypes/suggestion.html)
    * [Infobox Results](../dev/result%5Ftypes/infobox.html)
  * [Simple Theme Templates](../dev/templates.html)
  * [Search API](../dev/search%5Fapi.html)
  * [Plugins](../dev/plugins/index.html)
    * [Plugin Development](../dev/plugins/development.html)
    * [Built-in Plugins](../dev/plugins/builtins.html)
      * [Calculator](../dev/plugins/calculator.html)
      * [Hash Values](../dev/plugins/hash%5Fplugin.html)
      * [Hostnames](../dev/plugins/hostnames.html)
      * [Infinite scroll](../dev/plugins/infinite%5Fscroll.html)
      * [Self-Info](../dev/plugins/self%5Finfo.html)
      * [Tor check](../dev/plugins/tor%5Fcheck.html)
      * [Unit Converter](../dev/plugins/unit%5Fconverter.html)
      * [Time Zone](../dev/plugins/time%5Fzone.html)
  * [Answerers](../dev/answerers/index.html)
    * [Answerer Development](../dev/answerers/development.html)
    * [Built-in Answerers](../dev/answerers/builtins.html)
      * [Random](../dev/answerers/random.html)
      * [Statistics](../dev/answerers/statistics.html)
  * [Translation](../dev/translation.html)
  * [Makefile & ./manage](../dev/makefile.html)
  * [reST primer](../dev/reST.html)
  * [Tooling box searxng\_extra](../dev/searxng%5Fextra/index.html)
    * [searxng\_extra/update/](../dev/searxng%5Fextra/update.html)
* [DevOps tooling box](../utils/index.html)
  * [utils/searxng.sh](../utils/searxng.sh.html)
* [Source-Code](../src/index.html)
  * [Custom message extractor (i18n)](../src/searx.babel%5Fextract.html)
  * [Bot Detection](../src/searx.botdetection.html)
  * [Caches](../src/searx.cache.html)
  * [SearXNG Exceptions](../src/searx.exceptions.html)
  * [Favicons (source)](../src/searx.favicons.html)
  * [Online /info](../src/searx.infopage.html)
  * [Locales](../src/searx.locales.html)
  * [Search](../src/searx.search.html)
  * [Search processors](../src/searx.search.processors.html)
  * [Settings Loader](../src/searx.settings.html)
  * [SQLite DB](../src/searx.sqlitedb.html)
  * [Utility functions for the engines](../src/searx.utils.html)
  * [Valkey DB](../src/searx.valkeydb.html)
  * [Valkey Library](../src/searx.valkeylib.html)
  * [Weather](../src/searx.weather.html)

[ Back to top ](#) 

[ View this page ](https://github.com/searxng/searxng/blob/master/docs/user/search-syntax.rst?plain=true "View this page") 

[ Edit this page ](https://github.com/searxng/searxng/edit/master/docs/user/search-syntax.rst "Edit this page") 

# Search syntax[¶](#search-syntax "Link to this heading")

SearXNG comes with a search syntax by which you can modify the categories, engines, languages, and more. See the `preferences` for the list of engines, categories, and languages.

## `!` Select engine and category[¶](#select-engine-and-category "Link to this heading")

To set category and/or engine names, use a `!` prefix. To give a few examples:

* Search Wikipedia for **paris**:

  * `!wp paris`
  * `!wikipedia paris`
* Search in category **map** for **paris**:

  * `!map paris`
* Image search

  * `!images Wau Holland`

Abbreviations of the engines and languages are also accepted. Engine/category modifiers are chainable and inclusive. For example, `!map !ddg !wp paris` searches in the map category and searches DuckDuckGo and Wikipedia for **paris**.

## `:` Select language[¶](#select-language "Link to this heading")

To select a language filter use a `:` prefix. To give an example:

* Search Wikipedia with a custom language:

  * `:fr !wp Wau Holland`

## `!!<bang>` External bangs[¶](#bang-external-bangs "Link to this heading")

SearXNG supports the external bangs from [DuckDuckGo](https://duckduckgo.com/bang). To directly jump to a external search page use the `!!` prefix. To give an example:

* Search Wikipedia with a custom language:

  * `!!wfr Wau Holland`

Please note that your search will be performed directly in the external search engine. SearXNG cannot protect your privacy with this.

## `!!` automatic redirect[¶](#automatic-redirect "Link to this heading")

When including `!!` within your search query (separated by spaces), you will automatically be redirected to the first result. This behavior is comparable to the “Feeling Lucky” feature from DuckDuckGo. To give an example:

* Search for a query and get redirected to the first result

  * `!! Wau Holland`

Please keep in mind that the result you are being redirected to can’t be verified for trustworthiness and SearXNG cannot protect your personal privacy when using this feature. Use it at your own risk.

## Special Queries[¶](#special-queries "Link to this heading")

In the `preferences` page you find keywords for _special queries_. To give a few examples:

* Generate a random UUID

  * `random uuid`
* Find the average

  * `avg 123 548 2.04 24.2`
* Show the _user agent_ of your browser (needs to be activated)

  * `user-agent`
* Convert strings to different hash digests (needs to be activated)

  * `md5 lorem ipsum`
  * `sha512 lorem ipsum`

[ Next Configured Engines ](configured%5Fengines.html) [ Previous User information ](index.html) 

Copyright © SearXNG team 

Made with [Furo](https://github.com/pradyunsg/furo) 

[💾](https://github.com/searxng/searxng/) [🌐](https://searx.space/) 

On this page 

* [Search syntax](#)
  * [! Select engine and category](#select-engine-and-category)
  * [: Select language](#select-language)
  * [!!<bang> External bangs](#bang-external-bangs)
  * [!! automatic redirect](#automatic-redirect)
  * [Special Queries](#special-queries)