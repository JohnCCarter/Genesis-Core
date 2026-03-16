# Intelligence Event Schema

Status: ARCHITECTURE SPEC
Authority: Genesis-Core Intelligence Layer

## Purpose

Define the canonical `IntelligenceEvent` contract for the Genesis-Core Intelligence preparation phase.
This schema is the shared contract for all parallel editor work.

## Canonical model

`IntelligenceEvent` contains the following fields:

- `event_id`
- `source`
- `timestamp`
- `asset`
- `topic`
- `signal_type`
- `confidence`
- `references`
- `summary`

## Field rules

### `event_id`

- required
- non-empty string
- deterministic and stable for the producer context
- random or opaque stochastic ID generation is not allowed in v1

### `source`

- required
- non-empty string
- identifies the producing subsystem or upstream origin

### `timestamp`

- required
- ISO-8601 string
- must include timezone information

### `asset`

- required
- non-empty string
- canonical asset identifier for the event

### `topic`

- required
- non-empty string
- high-level semantic topic for the event payload

### `signal_type`

- required
- non-empty string
- category of signal or observation represented by the event

### `confidence`

- required
- finite float in the inclusive range `[0.0, 1.0]`

### `references`

- required field
- may be empty
- ordered collection of reference objects
- order must be preserved during serialization

Each reference object contains:

- `kind` — required non-empty string
- `ref` — required non-empty string
- `label` — optional string

### `summary`

- required
- non-empty string
- concise deterministic human-readable summary

## Serialization rules

- payloads must be JSON-serializable
- repeated serialization of the same event must be byte-for-byte identical
- JSON output must use stable key ordering
- serialization must not mutate the event object

## Validation rules

Validation in v1 is intentionally basic and deterministic:

- required strings must be non-empty after trimming
- timestamps must be timezone-aware ISO-8601 strings
- confidence must be finite and bounded to `[0.0, 1.0]`
- references must satisfy the required reference object fields
- validation must not read files, environment variables, services, or databases
