# Docs classification taxonomy routing guard

## Skill-ID

`docs_classification_taxonomy_routing`

## Syfte

Styr citation-bound klassificering av zone-guide- och routingytor i Genesis-Core utan att skapa ny authority, nya research conclusions eller readiness/promotion-semantik.

## Metadata

- Version: 0.1.0
- Status: dev
- Owners: fa06662
- Tags: docs, classification, routing, taxonomy, governance

## Regler

### Måste

- Behandla README- och indexytor som routing-/navigationsytor tills explicit textstöd visar något starkare.
- Kräva direkt citatstöd innan en yta märks `NON_AUTHORIZING`, `DORMANT` eller `ACTIVE` i knowledge-lagret.
- Falla tillbaka till `UNRESOLVED` när klassificeringen annars skulle kräva tvärdokument-syntes eller antaganden.
- Hålla README-förtydliganden korta, routingfokuserade och länkade till befintliga authority-index/regler.
- Separera artifact-status från conclusion-status när en zone-guide klassificeras.

### Får inte

- Behandla README-närvaro, mappnamn eller recency som bevis för authority.
- Skapa nya research conclusions eller nya aktiva authority-påståenden genom docs-syntes.
- Använda skillen som godkännande för readiness, promotion, runtime behavior eller PASS-semantik.
- Klassificera enskilda packets eller analysnoter när scopet bara gäller zon-guider och routingytor.

## Praktisk tillämpning

Om en zone-guide README behöver förtydligas, föredra formuleringar som:

- `This README is a routing surface ...`
- `It is non-authorizing ...`
- `If support is incomplete, classify as UNRESOLVED or omit the row.`

Undvik formuleringar som:

- `authoritative`
- `binding`
- `approved`
- `governs`
- `establishes conclusions`
- `promotion-ready`
