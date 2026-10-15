# 3. The widget runs in an iframe served by the gateway

Date: 2026-10-15

## Status

Accepted. See decision 17 in [the plan](https://github.com/ragbridge-ai/ragbridge/blob/main/docs/plans/chat-roadmap.md).

## Context

The widget is added to pages that this project does not control: their CSS, their scripts,
sometimes a content management system's. The widget shows a conversation, which may be a
private one, and holds a session token. The host page's styles must not break it, and the
host page's JavaScript must not be able to read the conversation or the token.

## Decision

1. **A small loader script on the host page opens an iframe whose document the gateway
   serves.** Everything the user sees and every request to the gateway happens inside it.
2. **The frame is served with a `Content-Security-Policy` whose `frame-ancestors` is built
   from the tenant's allowed origins**, so a site that is not on the list cannot frame it.
3. **The loader and the frame talk by `postMessage` with exact origins in both directions.**
   The token reaches the frame this way and never appears in a URL.

## Alternatives considered

- **Shadow DOM inside the host page.** It isolates CSS but not JavaScript: the host page's
  scripts could still read the conversation and the token.
- **Rendering directly into the host page.** The host's CSS would affect it and its
  JavaScript could read everything.
- **A script that calls the gateway from the host page's own origin.** The token would sit
  in the host page's memory, readable by every script on it.

## Consequences

- The cost of the isolation is a frame to size, to make accessible and to keep in step with
  its host: the loader resizes it, and the frame carries its own labels and keyboard
  handling.
- The gateway needs each tenant's list of allowed origins and serves the frame with a header
  that depends on the tenant.
- The widget's own code is plain JavaScript with no build step, and its tests run in a real
  browser (the plan's decisions 18 and 19).
