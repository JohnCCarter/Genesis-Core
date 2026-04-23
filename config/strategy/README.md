# Strategy config layout

`config/strategy/` är organiserad efter ansvar först och timeframe därefter där det passar.

## Struktur

- `champions/`
  - Aktiv strategi-authority för pipeline/backtest.
  - Freeze-känslig zon. Flytta eller ändra inte casually i cleanup-slices.
- `candidates/<timeframe>/`
  - Kandidatfiler och snapshots som ännu inte är champion-authority.
  - Se `config/strategy/candidates/README.md` för naming convention och vad som hör hemma i kandidatbanken.
- `composable/<timeframe>/`
  - Experimentella och iterativa strategibyggblock per timeframe.
  - Underkataloger som `poc/` och `phase2/` används för kampanj/fas inom samma timeframe.

## Regler för nya filer

- Lägg nya kandidatfiler under rätt timeframe, till exempel `candidates/1h/`.
- Följ kandidatbankens namngivningskonvention för nya filer; byt inte namn på redan packet-förankrade kandidater i opportunistiska slices.
- Lägg nya composable YAML-filer under rätt timeframe, till exempel `composable/1h/phase2/`.
- Skapa inte spekulativa timeframe-mappar utan faktiska filer som behöver bo där.
- Håll `champions/` separat från kandidater och experimentfiler.

## Notering

Den här strukturen är avsedd att minska lösa filer inför fortsatt 1h/6h-arbete utan att röra champion-zonen.
