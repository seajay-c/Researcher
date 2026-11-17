## What is SearXNG?

SearXNG is a free, open-source internet metasearch engine that aggregates results from up to 260 search services while never tracking or profiling its users [1][3]. It is a fork of the earlier Searx project and is licensed under the GNU Affero General Public License (AGPL-3.0) [2][3]. Its tagline is "Search without being tracked" [3].

## Origins and Development

SearXNG is a fork of the well-known Searx metasearch engine, which was itself inspired by the Seeks project [1]. Development of SearXNG began in the middle of 2021 [3]. The project is driven by an open community and is developed in public on GitHub, where the repository has approximately 39.6k stars, 3.6k forks, and 9,892 commits on the master branch [2]. The code is 100% open and everyone is welcome to contribute [1].

## Privacy Features

SearXNG protects user privacy through several mechanisms [4]:

- It removes private data from requests going to external search services, meaning it does not send cookies to those engines and generates a random browser profile for every request [4].
- It does not serve ads or tracking content, unlike most commercial search services [4].
- It hides both the referring page and the search query from the results pages being visited [4].
- It never shares anything with a third party and cannot be used to compromise the user [1].
- It can be used over Tor for online anonymity [3].
- JavaScript and cookies are optional in the interface [3].

The IP address used for outgoing requests will be that of the SearXNG instance, but the instance can also be configured to use a proxy or Tor [4].

## How It Works

SearXNG acts as a metasearch engine: it takes the user's query, sends it to multiple upstream search services simultaneously, and aggregates the results into a single list [1][3]. It provides basic privacy by mixing queries with searches on other platforms without storing search data [1]. A stats page contains anonymous usage statistics about the engines used [1]. SearXNG supports the OpenSearch specification, allowing it to be added to a browser's search bar or set as the default search engine [1].

## Community and Public Instances

The project maintains a community chat on Matrix at `#searxng:matrix.org` [1][3]. Public instances are listed and monitored at searx.space, which tracks response times, TLS grades, CSP grades, uptime, and engine availability [5]. At the time of writing, searx.space lists 75 online HTTPS instances and 12 online Tor hidden-service instances [5]. The documentation notes that public instances, due to higher traffic, may be more likely to be blocked by upstream search providers, and recommends that users who can self-host do so for a more consistent experience [4][5].

## Self-Hosting

SearXNG can be installed on one's own server using Docker containers, installation scripts, or step-by-step manual instructions [1][3]. When running a private instance, users have full control over source code, logging settings, and preferences; settings are stored locally on the user's machine rather than in browser cookies [4]. The documentation explicitly encourages users who care about privacy to run their own instance [1].

## Technical Details

The codebase is written in Python and includes modules for search processing, bot detection, caching, favicons, weather, and database support (SQLite and Valkey) [1][3]. The project supports 58 translations, managed through Weblate [1][3]. Built-in plugins include a calculator, unit converter, infinite scroll, Tor check, and time-zone tools [1][3]. The repository also contains a Go module (`go.mod`), a `package.json`, and a `mise.toml`, indicating polyglantic tooling [2]. The current documentation version is 2026.11.17+cf3c20177 [1][3].

## Acknowledgements

The following organizations have provided SearXNG access to their paid plans at no cost: Docker, Tuta, and BrowserStack [3].

## Failures

- gather: 3 tool calls failed in a row; last error: Error: web_url_read error: 🚫 Website Error (404): Page not found. Retry with a different query or source.
- gather: 3 tool calls failed in a row; last error: Error: web_url_read error: 🚫 Website Error (404): Page not found. Retry with a different query or source.
- gather: 3 tool calls failed in a row; last error: Error: web_url_read error: 🚫 Website Error (404): Page not found. Retry with a different query or source.
- gather: 3 tool calls failed in a row; last error: Error: web_url_read error: 🚫 Website Error (404): Page not found. Retry with a different query or source.
- gather: 3 tool calls failed in a row; last error: Error: web_url_read error: 🚫 Website Error (404): Page not found. Retry with a different query or source.
- gather: 3 tool calls failed in a row; last error: Error: web_url_read error: 🚫 Website Error (404): Page not found. Retry with a different query or source.
- gather: 3 tool calls failed in a row; last error: Error: web_url_read error: 🚫 Website Error (404): Page not found. Retry with a different query or source.
- gather: 3 tool calls failed in a row; last error: Error: web_url_read error: 🚫 Website Error (404): Page not found. Retry with a different query or source.
- gather: 3 tool calls failed in a row; last error: Error: web_url_read error: 🚫 Website Error (404): Page not found. Retry with a different query or source.
- gather: 3 tool calls failed in a row; last error: Error: web_url_read error: 🚫 Website Error (404): Page not found. Retry with a different query or source.

## Sources

[1] About SearXNG[¶](#about-searxng "Link to this heading") — https://docs.searxng.org/user/about.html

[2] Navigation Menu — https://github.com/searxng/searxng

[3] Welcome to SearXNG[¶](#welcome-to-searxng "Link to this heading") — https://docs.searxng.org/

[4] Why use a private instance?[¶](#why-use-a-private-instance "Link to this heading") — https://docs.searxng.org/own-instance.html

[5] 75 online instances — https://searx.space/
