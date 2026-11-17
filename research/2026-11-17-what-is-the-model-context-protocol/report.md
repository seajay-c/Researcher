The Model Context Protocol (MCP) is an open-source standard and open framework, introduced by Anthropic in November 2024, that standardizes how AI applications—such as large language models—connect to and exchange data with external tools, systems, and data sources [4]. It is often described as a "USB-C port for AI applications": just as USB-C provides a single physical interface for connecting devices, MCP provides a single protocol for connecting AI applications to external systems [2]. MCP was created at Anthropic by engineers David Soria Parra and Justin Spahr-Summers [4][8], and as of the latest specification revision (2026-07-28), it is a stateless, JSON-RPC 2.0–based protocol governed under the Linux Foundation's Agentic AI Foundation [4][6].

## Origin and Purpose

MCP was announced by Anthropic on November 25, 2024, as an open standard for connecting AI assistants to the systems where data lives, including content repositories, business tools, and development environments [1]. The protocol was designed to address information silos and legacy systems that previously forced developers to build a custom connector for every new data source—an "N×M" data integration problem [4]. By providing a universal, open standard, MCP replaces fragmented integrations with a single protocol, giving AI systems reliable access to the data they need [1].

MCP was inspired by the Language Server Protocol (LSP), which standardizes how programming-language support is added across an ecosystem of development tools; in a similar way, MCP standardizes how additional context and tools are integrated into the ecosystem of AI applications [5][4].

## Core Architecture

MCP follows a client–server architecture with three participants: **Hosts** (LLM applications that initiate connections), **Clients** (connectors within the host application), and **Servers** (services that provide context and capabilities) [5]. MCP focuses solely on the protocol for context exchange and does not dictate how AI applications use LLMs or manage the provided context [3].

The protocol is organized into two layers [3][5]:

- **Data layer:** Defines the JSON-RPC 2.0–based protocol for client–server communication, including capability and version discovery, and core primitives [3].
- **Transport layer:** Defines the communication mechanisms and channels (e.g., STDIO for local servers, Streamable HTTP for remote servers) that enable data exchange, including connection establishment, message framing, and authorization [3].

The data layer implements a stateless exchange protocol: every request carries the protocol version, client identity, and relevant capabilities in a `_meta` field, so the server can process each request independently [3][6]. A mandatory `server/discover` request allows clients to query a server's supported versions, capabilities, and identity before issuing other requests [3].

## Core Primitives

MCP defines three core primitives that **servers** can expose to clients [3][5]:

- **Tools:** Executable functions that AI applications can invoke to perform actions (e.g., file operations, API calls, database queries) [3].
- **Resources:** Data sources that provide contextual information to AI applications (e.g., file contents, database records, API responses) [3].
- **Prompts:** Reusable templates that help structure interactions with language models (e.g., system prompts, few-shot examples) [3].

Each primitive type has associated methods for discovery (`*/list`), retrieval (`resources/read`, `prompts/get`), or execution (`tools/call`) [3]. Clients may also offer **Elicitation**, a server-initiated request for additional information from users [5].

## Specification and SDKs

The MCP project comprises the specification, SDKs in multiple programming languages (Python, TypeScript, C#, Java), development tools such as the MCP Inspector, and reference server implementations [3][4][8]. The schema is defined in TypeScript and also made available as JSON Schema for wider compatibility [8]. The official documentation is hosted at modelcontextprotocol.io and built using Mintlify [8][2].

The 2026-07-28 specification revision, described by lead maintainer David Soria Parra as the most substantial change since the addition of authorization, made the protocol core stateless by removing the `initialize`/`initialized` handshake and the `Mcp-Session-Id` header [4][6]. Each request now travels independently, carrying its protocol version, client identity, and capabilities in `_meta`, meaning any request can land on any server instance behind a plain round-robin load balancer without shared storage [6]. The revision also introduced Multi Round-Trip Requests (MRTR), header-based routing, cacheable list results, authorization hardening, and a formal extensions framework [6].

## Extensions

Beyond the core protocol, MCP defines optional, opt-in extensions negotiated through per-request capabilities [5]:

- **Tasks:** Asynchronous execution of long-running operations, with polling, mid-flight input, and durable handles [5].
- **Skills over MCP:** Rich, structured instructions for agent workflows, discovered and consumed through MCP [5].
- **MCP Apps:** Interactive UI elements (charts, forms, video players) rendered inline within conversations [5][4].

## Adoption and Ecosystem

MCP has achieved broad cross-vendor adoption. OpenAI officially adopted MCP in March 2025, integrating it across products including the ChatGPT desktop app; in September 2025, OpenAI added MCP support to ChatGPT apps for third-party access [4]. Google DeepMind also embraced the standard in April 2025 [4]. Microsoft, AWS, and others have built MCP into their platforms [4][7]. Development tools including Visual Studio Code, Cursor, Zed, Replit, Codeium, Sourcegraph, and MCPJam all support MCP [2].

In December 2025, Anthropic donated MCP to the Agentic AI Foundation (AAIF), a directed fund under the Linux Foundation co-founded by Anthropic, Block, and OpenAI [4]. By mid-2026, more than 10,000 MCP servers had been deployed in production, with the protocol's SDKs downloaded over 97 million times per month [4]. Tier 1 SDKs (TypeScript and Python) crossed the 1 billion total downloads threshold, with close to half-a-billion downloads per month across Tier 1 SDKs [6]. The MCP Registry, launched in September 2025, had grown to close to two thousand entries with 407% growth from its initial batch [7]. In April 2026, Salesforce's Headless 360 platform began routing customer and agent interactions via MCP, and by late May reported 4.5 million MCP calls processed since launch [4].

## Security Considerations

The specification outlines key security principles: user consent and control, data privacy, and tool safety (treating tools as arbitrary code execution) [5]. MCP has also been subject to several reported security vulnerabilities, including prompt injection issues, tool poisoning attacks, and a critical remote code execution vulnerability in `mcp-remote` (CVE-2025-6514) [4]. A May 2026 NSA publication addressed security design considerations for AI-driven automation using MCP [4].

## Governance and Community

MCP is governed through a community of maintainers, working groups, and Specification Enhancement Proposals (SEPs) [8][7]. Contributions to the specification are discussed and approved in the relevant working group before a pull request or SEP is opened [8]. The project is licensed under the MIT License [8]. Community engagement occurs through a Discord server, GitHub, events such as the MCP Dev Summit, MCP Night, and MCP Dev Days, and thousands of independent worldwide communities [7]. The MCP Dev Summit North America in New York City (April 2026) drew approximately 1,200 attendees [4].

## Sources

[1] Introducing the Model Context Protocol — https://www.anthropic.com/news/model-context-protocol

[2] Get started — https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro

[3] Get started — https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture

[4] Contents — https://en.wikipedia.org/wiki/Model_Context_Protocol

[5] Base Protocol — https://modelcontextprotocol.io/specification/2026-07-28

[6] The 2026-07-28 Specification — https://blog.modelcontextprotocol.io/posts/2026-07-28/

[7] One Year of MCP: November 2025 Spec Release — https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/

[8] Navigation Menu — https://github.com/modelcontextprotocol/modelcontextprotocol
