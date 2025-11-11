## 2025-11-11 – Backtestinstrumentering & championåterställning

- Återskapade championbacktestet `results/backtests/tBTCUSD_1h_20251023_162506.json` genom att extrahera från arkivet `results/backtests/_archive/20251110_131936.zip`.
- Instrumenterade `src/core/backtest/engine.py` med HTF/LTF-fibstatistik och bar-felloggning. Resultatfiler innehåller nu `{"debug": {...}}` med räknare och listan `bar_errors`.
- Körning `tBTCUSD_1h_20251111_181048.json` visar 7 586 processade barer (alla med fib-kontekst) och 934 barer som faller på `"<" not supported between instances of 'dict' and 'float'`.
- Nästa steg: spåra var dictionaries jämförs mot floats i confidence/riskkedjan och fixa så att backtestet passerar samtliga 8 640 barer