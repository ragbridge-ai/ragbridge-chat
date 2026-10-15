# 1. The host application is the identity provider, and signs session tokens with Ed25519

Date: 2026-10-15

## Status

Accepted. See decision 5 in [the plan](https://github.com/ragbridge-ai/ragbridge/blob/main/docs/plans/chat-roadmap.md).

## Context

The gateway answers end users' questions from documents that only some of them may read, so
it must know who is asking and which access groups they belong to. The applications that
embed the chat already log their users in. Asking the gateway to log them in again would
mean it holds passwords or integrates with each application's single sign-on, and would put
the credentials of every tenant's users in one more place.

## Decision

1. **The host application logs its users in, as it already does, and signs a short session
   token for them.** The gateway never handles passwords or single sign-on.
2. **The token is signed with Ed25519, and the gateway stores only the public key.** A leak
   of the gateway's database cannot mint a token. The host keeps the private key.
3. **Ed25519 because the host can sign it without extra packages.** PHP's `ext-sodium` signs
   it, and Python verifies it through `PyJWT` with `cryptography`.
4. **Visitors who are not logged in get an anonymous session issued by the gateway itself**,
   limited to the `public` access group.

The claims, their checks and the 15-minute lifetime limit are specified in the plan and are
implemented with token verification.

## Alternatives considered

- **HS256 (a shared secret).** The gateway would hold the secret and so could mint a token
  for any user of the host application, and a leak of its database would do the same.
- **The gateway as an identity provider** (accounts, passwords, OAuth or SAML). It is the
  feature this decision exists to avoid: every integration would become a login system.
- **Opaque session ids that the host registers with the gateway on every login.** It needs a
  call from the host's login path to the gateway, makes the gateway a dependency of logging
  in, and gives the gateway state to keep in step with the host's sessions.

## Consequences

- A host application must hold a private key and add a route that issues a token; the PHP
  client will provide both.
- A token cannot be revoked before it expires. That is why its lifetime is short, and why a
  user who loses a group stops getting answers from its documents at the next message, not
  at the next login: every message is retrieved with the groups in the *current* token.
- The gateway needs a way to register a tenant's public key and to rotate it; that is a
  command-line tool, not an endpoint (the same reasoning as the core's API keys).
