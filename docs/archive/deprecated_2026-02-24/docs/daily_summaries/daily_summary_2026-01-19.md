# Daily Summary - 2026-01-19

## Summary of Work

Dagens fokus var att få Genesis-Core MCP **remote linking mot ChatGPT** att fungera stabilt även via tunnels/proxies.

Den blockerande observationen var att vissa setups (t.ex. Cloudflare _quick tunnel_) kan svara `200 text/event-stream` på `GET /sse` men ändå **inte leverera första SSE-bytes** (ingen flush), vilket bryter handshake i klienter som väntar på första `event: endpoint`.

För att göra remote-länkningen robust implementerades därför en **JSON-only kompatibilitetsväg** på `POST /mcp` som inte kräver en långlivad SSE-stream.

## Key Changes

- **Remote MCP: JSON-only fallback på `POST /mcp`**
  - Stödjer JSON-RPC: `initialize`, `tools/list`, `tools/call`, `ping`.
  - Designad för att fungera när `FastMCP`/"Streamable HTTP" inte är tillgängligt i aktuell `mcp`-version.
  - Gör det möjligt att länka ChatGPT mot `https://<host>/mcp` utan att vara beroende av att `GET /sse` flushar.

- **ASGI-routing i fallback-läget**
  - `GET /sse` och legacy `POST /mcp?session_id=...` finns kvar för kompatibilitet.
  - Nya JSON-only vägen triggas när `POST /mcp` saknar `session_id` i query.

- **Docs uppdaterade**
  - Förtydligar att rekommenderad URL för ChatGPT är `POST /mcp` (inte `/sse`).
  - Noterar att SSE kan buffras genom vissa tunnels/proxies och att `POST /mcp` ofta är en bättre första probe.

## Verification

- Lokal verifikation:
  - `GET /healthz` → `200 OK`
  - `POST /mcp` → `initialize`/`tools/list`/`tools/call(ping)` → `200 OK`

- Publik verifikation via tunnel:
  - `POST /mcp` → `initialize`/`tools/list`/`tools/call(ping)` → `200 OK`

- QA:
  - `pre-commit run --all-files` ✅

## Next Steps

- Implementera en mer "aktiv" Streamable HTTP-transport (session-/event-hantering) när det behövs.
- Om URL-stabilitet krävs: byt från quick tunnel till named tunnel (eller annan reverse-proxy) och dokumentera driftflödet.
