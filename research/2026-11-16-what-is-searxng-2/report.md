SearXNG is a free and open-source metasearch engine that aggregates results from multiple upstream search services while storing little to no information about its users [1][2][3]. It was created in March 2021 as a community fork of the earlier searX project, which has since been archived [2][7]. Written in Python and licensed under the GNU Affero General Public License (AGPL-3.0), it can be run as a public or self-hosted private instance [2][3].

## What It Does

SearXNG functions by sending a user's query to upstream search engines and returning the aggregated results [2]. As of 2026, it lists 251 possible search services to draw from, including Google, Bing, DuckDuckGo, and Qwant [2]. It supports categorical searching across categories such as General, Images, Videos, News, Social Media, Music, Files, IT, and Science [2]. It also supports "bangs": appending an exclamation point and a shortcut key (e.g. `!g`) searches only that particular engine, while a double exclamation (e.g. `!!w`) redirects directly to the external engine [2].

## Privacy Model

SearXNG does not generate a profile about the user, does not share anything with third parties, and serves no ads or tracking content [1][5]. It protects privacy in three ways: (1) removing private data from requests going to search services, (2) not forwarding anything from third-party services (e.g. advertisements), and (3) removing private data from requests going to the results pages being visited [5]. Removing private data means not sending cookies to external search engines and generating a random browser profile for every request [5]. The instance's IP address is what the upstream engines see, but SearXNG can also be configured to route traffic through a proxy or Tor [5].

## Origin and Relationship to searX

SearXNG was forked from searX, itself inspired by the Seeks project [1]. The fork was created in mid-2021 by former searX maintainers who disagreed with the original project's decision to add engine metrics, viewing those metrics as insufficiently privacy-respecting [4][7]. The searX GitHub repository was archived in September 2023, and SearXNG became the actively maintained successor [7]. The searX project later clarified that it would continue as a more minimalist, stability-focused alternative, while SearXNG offers rolling releases, more frequent dependency updates, faster engine fixes, and a JavaScript-based user interface [4].

## Deployment and Instances

SearXNG is server-side software and is hosted by both public and private instances [2]. Public instances are open to anyone with internet access; private instances may run on a local network, a user's desktop, or behind a VPN [2][5]. A community-maintained list of public instances is available at searx.space [1][2]. Users are encouraged to always use an instance operated by people they trust [5]. For those who cannot or do not want to self-host, public instances provide access to a privacy-respecting search service [5].

## Technical Details

The project is written in Python and HTML and runs on Linux, FreeBSD, and macOS [2]. It supports the OpenSearch standard, allowing it to be added to a browser's search bar and set as the default search engine in Firefox, Microsoft Edge, Chromium, and Safari [1][2]. The codebase includes components for bot detection, caching, Valkey and SQLite databases, favicons, weather, and a suite of built-in plugins (Calculator, Hash Values, Hostnames, Infinite Scroll, Self-Info, Tor Check, Unit Converter, Time Zone) [1]. The repository on GitHub (github.com/searxng/searxng) has approximately 39.6 k stars and 3.6 k forks as of the current data [3].

## Community and Development

The project is driven by an open community and invites contributions via its GitHub repository, translations through Weblate (translate.codeberg.org), and discussion on Matrix at #searxng:matrix.org [1][3]. Documentation is hosted at docs.searxng.org and covers user information, administrator configuration, developer guides, engine implementations, result types, and source-code references [1][5].

## Sources

[1] About SearXNG — https://docs.searxng.org/user/about.html

[2] Contents — https://en.wikipedia.org/wiki/SearXNG

[3] Navigation Menu — https://github.com/searxng/searxng

[4] Navigation Menu — https://github.com/searx/searx

[5] Why use a private instance? — https://docs.searxng.org/own-instance.html

[6] Navigation Menu — https://github.com/searxng/searxng/releases

[7] Contents — https://en.wikipedia.org/wiki/Searx
