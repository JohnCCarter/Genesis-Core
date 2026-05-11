# Year worker clean-clone admissibility matrix

Date: 2026-05-07
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `proposed / non-authoritative / manual-draft / blocked`
Simulation state: `blocked`
Dispatch allowed: `false`
Execution authority: `none`
Proof authority: `none`
Shared truth effect: `none`

This artifact is a simulation/specimen only. It is non-authoritative, non-operational, and fail-closed on unresolved refs. It does **not** authorize dispatch, execution, materialization, admission, or proof of runtime readiness.

## Classification legend

- **reconstructable** — the clean clone can determine this directly from declared docs/manifests
- **partially reconstructable** — the clean clone can identify the surface but not complete it honestly
- **blocked** — the clean clone can determine that advancement must stop
- **intentionally unresolved** — the source docs deliberately leave this open
- **requires future implementation** — no honest completion path exists yet from docs only
- **forbidden to infer** — a tempting but invalid leap from declared docs to operational meaning

## Matrix

| Surface | Classification | Clean-clone verdict | Evidence source | Fail-closed consequence | Forbidden inference |
| --- | --- | --- | --- | --- | --- |
| bundle identity | reconstructable | yes | root packet + lineage summary | none | n/a |
| 11-object traversal order | reconstructable | yes | root packet + lineage summary + object refs | none | n/a |
| root `prev_ref: null` | reconstructable | yes | root packet | none | n/a |
| terminal `next_ref: null` | reconstructable | yes | lineage summary | none | n/a |
| `dispatch_allowed: false` everywhere | reconstructable | yes | all blocked objects | dispatch stays blocked | that one later object could override the chain |
| absence of execution authority | reconstructable | yes | all blocked objects | execution stays prohibited | that runtime shape equals execution permission |
| absence of proof authority | reconstructable | yes | all blocked objects | no readiness/proof claim allowed | that structural coherence equals proof |
| absence of shared-truth effect | reconstructable | yes | all blocked objects | no truth-promotion allowed | that integration shapes update shared truth now |
| queue non-authorizing semantics | reconstructable | yes | queue object | queue cannot promote dispatch | queue presence implies dispatch |
| envelope scope boundaries | reconstructable | yes | envelope | scope widening remains blocked | envelope presence implies runtime activation |
| overlay anti-tuning boundary | reconstructable | yes | generated overlay | tuning remains forbidden | metadata-only overlay implies config mutation |
| output anti-global-claim boundary | reconstructable | yes | output contract | worker stays year-local only | output contract implies global truth |
| integration-plane ownership of cross-year meaning | reconstructable | yes | intake + cross-year objects | year worker cannot interpret globally | cross-year categories imply admission |
| baseline config identity | partially reconstructable | descriptive only | queue/runtime objects | attestation remains blocked | repo path+selector implies admissible config |
| runtime entrypoint identity | partially reconstructable | descriptive only | dependency/runtime objects | command cannot be executed | tracked script ref implies reviewed runtime path |
| placeholder hash visibility | reconstructable | yes | multiple objects | hash binding stays unresolved | placeholder equals bound hash |
| bound manifest hash set | blocked | absent | dependency manifest | hash-based advancement stops | placeholder chain is good enough |
| materialized overlay payload | blocked | absent | dependency manifest + overlay object | runtime preflight must stop | overlay draft equals payload |
| runtime command rendering | blocked | `rendered_command: null` | runtime manifest | no command may be claimed | command template fields imply runnable command |
| output artifacts | blocked | none produced | output contract | no execution evidence exists | empty artifact list proves success/failure |
| intake receipt validation | intentionally unresolved | cannot complete | integration intake | intake remains specimen-only | intake schema implies receipts are valid |
| cross-year admission | blocked | not admitted | cross-year object | synthesis cannot start | categories imply recurring effect |
| replay reproducibility | requires future implementation | no | coherence report + gap report | operational claims remain forbidden | structural chain proves replay correctness |
| resumability/idempotency | requires future implementation | no | gap report | restart/re-entry claims remain forbidden | clean clone would naturally be resumable |
| cloud dispatch/runtime integration | requires future implementation | no | gap report | dispatch remains false | docs-only chain implies cloud readiness |

## Summary verdict

- structurally reconstructable surfaces: `strong`
- partially reconstructable surfaces: `honestly bounded`
- blocked/intentionally unresolved surfaces: `explicit`
- future-implementation surfaces: `numerous but declared`

## Recommended reading order

1. root packet
2. traversal map
3. coherence report
4. gap report
5. input manifest

## What this matrix does not prove

- that operational admissibility is close
- that future implementation will be simple
- that blocked surfaces should be unblocked next
