# ADR-0082: The coach's model fallback as shipped, with refusals and token-limit errors kept out of it

Status: ACCEPTED (founder, 2026-10-13; drafted by Claude Code from the ruling)
Requirements: T34 (DEF-123), T92 (DEF-153), T36 (DEF-125)
Changes: ADR-0067 point 4 (how a content-filter refusal is kept from the fallback)
Depends on: ADR-0059 decision 2 (`ModelFallbackMiddleware`), ADR-0080 (the turn deadline), ADR-0044 (the four levels)

## Context

ADR-0059 decision 2 puts T34's fallback on LangChain's `ModelFallbackMiddleware`. ADR-0067 point 4 says
that middleware treats a content-filter refusal as not retryable. It does not: in the pinned langchain
(`requirements.txt`) it catches every exception except `GraphBubbleUp` and sends the request to the next
model, with no filter. As shipped, a `content_filter` refusal (T92) and a token-limit HTTP 400 (§4.8,
T36) would both go to gpt-4o-mini.

## Decision

1. **The fallback is `ModelFallbackMiddleware` as shipped**: premium (gpt-4o) first, then the operational
   deployment (gpt-4o-mini) with the coach's temperature, token cap and request timeout.
2. **A function middleware inside it keeps two errors out.** Declared inside the retry, so innermost of the
   three: a `content_filter` refusal or a token-limit 400 becomes a reply marked with the reason, which
   neither the retry nor the fallback sees as a failure. The executor reads the mark and writes the reply
   in code: T92's guidance reply for a refusal, the level-4 reply for a token limit.
3. **The order, outermost first:** the call limit, the fallback, the retry, the marker. The retry ends
   with an error (`on_failure="error"`) so the fallback hears it; the call limit counts one call however
   many attempts and models it took.
4. **Levels built: 1, 2 and 4.** Level 1: gpt-4o, retried with backoff. Level 2: gpt-4o-mini, retried
   with backoff. Level 4: when both fail, the executor answers in code, naming the phase and the captured
   count and saying progress is saved; the exchange is marked as a refusal is, so the resent message is
   not doubled. **Level 3 (Redis) is not built.**
5. **Inside the turn deadline (ADR-0080).** A fast failure (5xx, 429, connection) reaches gpt-4o-mini in
   seconds. A request timeout and its retry already pass the deadline, whose reply answers first.

## Consequences

- ADR-0067 point 4 holds through the marker, not through the fallback middleware.
- A failed coach call that used to end in the move's reply written in code now falls back to
  gpt-4o-mini, and when both fail ends in the level-4 reply.

## Rejected

- **A hand-written fallback with a filter** (`@wrap_model_call` and `request.override(model=…)`): overturns
  ADR-0059 decision 2 and rule 0.24.
- **`with_fallbacks(exceptions_to_handle=…)` on the coach model**: unproven with `create_agent`'s
  structured reply.
