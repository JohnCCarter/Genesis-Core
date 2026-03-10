# Privacy Policy — Genesis-Core MCP Remote Actions

**Effective date:** 2026-02-04

This Privacy Policy explains how the Genesis-Core **MCP remote server** ("Service") handles data when you use it via
ChatGPT “Connect to MCP” / public actions.

> Note: This document is provided for transparency and operational clarity. It is not legal advice.

## What the Service is

The Service is a self-hosted HTTP endpoint that exposes read-only project tools (for example: searching files and reading
project documents) over the Model Context Protocol (MCP).

## Data we may process

When you use the Service, we may process:

- **Request data** you send to the Service (for example: JSON-RPC payloads, tool names, and tool arguments).
- **File paths and snippets** returned by tools (for example: content of files you request to read).
- **Operational metadata** such as timestamps and request outcome (success/error).
- **Network metadata** typically present in HTTP requests, such as IP address and user agent (often handled at the reverse
  proxy / tunnel level).

## What we do NOT intentionally collect

- We do not intentionally collect payment information.
- We do not intentionally collect sensitive personal data.

## How data is used

We use data to:

- Provide the requested tool functionality.
- Monitor reliability and prevent abuse.
- Debug errors and investigate security incidents.

## Logs and retention

The Service may write logs for operational and security purposes. Retention depends on the server configuration and the
hosting environment. If you want stricter retention, reduce log verbosity and rotate/purge logs on the host.

## Sharing and third parties

Depending on your setup, requests may pass through third parties such as:

- **Your reverse proxy / tunnel provider** (for example Cloudflare) which may process network metadata.
- **Your MCP client** (for example ChatGPT/OpenAI) which may process the prompts you provide and any tool outputs the
  client receives.

We do not sell personal data.

## Security controls

The Service is designed to reduce risk via:

- **Read-only safe mode** (disables write/execute tools).
- **Path allowlisting** and blocked patterns to prevent access to sensitive files.
- Optional **shared-secret header** enforcement for `/mcp` (if enabled).

## Your choices

If you operate this Service yourself, you control:

- Which directories are accessible via allowlists.
- Whether the endpoint is publicly reachable.
- Whether additional access controls (e.g. Cloudflare Access) are required.

## Contact

For privacy questions, contact: **REPLACE_WITH_YOUR_CONTACT_EMAIL**

## Changes

We may update this policy from time to time. Update the effective date above when you make material changes.
