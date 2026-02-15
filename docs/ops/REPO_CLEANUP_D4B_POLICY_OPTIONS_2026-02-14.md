# Repo Cleanup D4B Policy Options (2026-02-14)

## Syfte

Ge beslutsunderlag för hur `results/**` kan bli spårbart i framtida cleanup-trancher.

D4B i denna commit är docs-only. Ingen ignore-policy ändras här.

## Utgångsläge

- D4A dokumenterade trackability-blocker för `results/**`.
- Evidens: `.gitignore:212` innehåller `results/`.
- Därför är move-only execution för `results/**` inte verifierbar i git-diff under nuvarande policy.

## Policyalternativ (föreslagna)

### Alternativ A — Selektiv spårning av curated bundles

**Status:** `föreslagen`
**Risknivå:** medel
**Idé:** Behåll bred ignore för `results/**`, men tillåt explicit spårning av ett begränsat, reproducerbart delträd (t.ex. bundles/metadata).

**Fördelar**

- Låg påverkan på repo-storlek jämfört med full öppning.
- Tydlig governance för vad som får checkas in.

**Nackdelar**

- Kräver strikt process för vad som räknas som curated.
- Risk för policy-drift om undantag växer över tid.

**Kräver**

- Separat kontrakt för ignore-policy.
- Explicit requester-godkännande.
- Opus pre-/post-audit på policyändring.

### Alternativ B — Full spårning av valda results-subträd

**Status:** `föreslagen`
**Risknivå:** hög
**Idé:** Tillåt spårning av hela subträd under `results/` (ex. `results/hparam_search/<run>`).

**Fördelar**

- Maximal diff-spårbarhet för move-only cleanup.

**Nackdelar**

- Stor risk för repo-bloat och tung historik.
- Hög operativ risk för oavsiktliga stora commits.

**Kräver**

- Separat kontrakt med retention och volymgränser.
- Tydlig rollback-plan.
- Extra gate för storlekskontroll.

### Alternativ C — Ingen policyändring, fortsatt out-of-band

**Status:** `föreslagen`
**Risknivå:** låg
**Idé:** Behåll nuvarande ignore-policy; hantera `results/**` endast via lokal drift och separat rapportering.

**Fördelar**

- Ingen repo- eller CI-risk från stora artefakter.

**Nackdelar**

- Ingen commit-nivåspårbarhet för results-cleanup.

**Kräver**

- Operativ rutin för extern loggning/versionering av cleanup-händelser.

## Rekommenderad ordning (föreslagen)

1. Starta med **Alternativ A** i en separat, liten policy-kontraktstranche.
2. Kör pilot på en enda curated artefaktklass.
3. Utvärdera diff-storlek, reviewbarhet och rollback innan eventuell utökning.

## Vad som inte är infört i D4B

- Ingen ändring i `.gitignore`.
- Ingen `results/**` move-only execution.
- Ingen ändring i runtime/API/config.
