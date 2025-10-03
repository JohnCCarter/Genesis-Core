import asyncio
import json
import json as _json
from pathlib import Path

import httpx
from fastapi import Body, FastAPI
from fastapi.responses import HTMLResponse

from core.config.authority import ConfigAuthority
from core.config.settings import get_settings
from core.config.validator import append_audit, diff_config, validate_config
from core.io.bitfinex import read_helpers as bfx_read
from core.io.bitfinex.exchange_client import get_exchange_client
from core.observability.metrics import get_dashboard
from core.server_config_api import router as config_router
from core.strategy.evaluate import evaluate_pipeline

app = FastAPI()
app.include_router(config_router)
_AUTH = ConfigAuthority()


@app.on_event("startup")
def _log_config_version() -> None:
    try:
        _, h, v = _AUTH.get()
        print(f"CONFIG_VERSION={v} CONFIG_HASH={h[:12]}")
    except Exception as e:
        print(f"CONFIG_READ_FAILED: {e}")


# Whitelist av tillåtna TEST-spotpar för paper-trading
TEST_SPOT_WHITELIST: set[str] = {
    "tTESTBTC:TESTUSD",
    "tTESTBTC:TESTUSDT",
    "tTESTETH:TESTUSD",
    "tTESTSOL:TESTUSD",
    "tTESTADA:TESTUSD",
    "tTESTALGO:TESTUSD",
    "tTESTAPT:TESTUSD",
    "tTESTAVAX:TESTUSD",
    "tTESTDOGE:TESTUSD",
    "tTESTDOT:TESTUSD",
    "tTESTEOS:TESTUSD",
    "tTESTFIL:TESTUSD",
    "tTESTLTC:TESTUSD",
    "tTESTNEAR:TESTUSD",
    "tTESTXAUT:TESTUSD",
    "tTESTXTZ:TESTUSD",
}


@app.get("/paper/whitelist")
def paper_whitelist() -> dict:
    """Returnera whitelist av tillåtna TEST-spotpar för UI-val."""
    return {"symbols": sorted(TEST_SPOT_WHITELIST)}


@app.get("/health")
def health() -> dict:
    try:
        _, h, v = _AUTH.get()
        return {"status": "ok", "config_version": v, "config_hash": h}
    except Exception:
        return {"status": "ok", "config_version": None, "config_hash": None}


@app.get("/observability/dashboard")
def observability_dashboard() -> dict:
    return get_dashboard()


@app.get("/config/defaults")
def get_strategy_defaults() -> dict:
    """Läs och returnera strategy defaults från filsystemet.

    Källfil: config/strategy/defaults.json
    """
    p = Path.cwd() / "config" / "strategy" / "defaults.json"
    if not p.exists():
        return {"error": "not_found"}
    try:
        return _json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"error": "invalid_json"}


@app.post("/config/validate")
def config_validate(payload: dict = Body(...)) -> dict:
    errors = validate_config(payload)
    return {"valid": len(errors) == 0, "errors": errors}


@app.post("/config/diff")
def config_diff(payload: dict = Body(...)) -> dict:
    old = payload.get("old", {}) or {}
    new = payload.get("new", {}) or {}
    changes = diff_config(old, new)
    return {"changes": changes}


@app.post("/config/audit")
def config_audit(payload: dict = Body(...)) -> dict:
    changes = payload.get("changes", []) or []
    user = str(payload.get("user") or "system")
    append_audit(changes, user=user)
    return {"status": "ok", "appended": len(changes)}


@app.get("/ui", response_class=HTMLResponse)
def ui_page() -> str:
    return """
<!doctype html>
<html lang=\"sv\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Genesis-Core – Minimal Test UI</title>
  <style>
    body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 20px; }
    textarea { width: 100%; height: 160px; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
    pre { background: #f6f8fa; padding: 12px; overflow: auto; }
    button { padding: 8px 14px; cursor: pointer; }
    .row { display: grid; grid-template-columns: 1fr; gap: 12px; max-width: 960px; }
  </style>
  </head>
<body>
  <h1>Genesis‑Core – Minimal test</h1>
  <div id="status" style="margin:6px 0; color:#374151; font-size:14px;">Config: <span id="cfg_ver">-</span> | <span id="cfg_hash">-</span></div>
  <div class=\"row\">
    <label>Order‑symbol (TEST)</label>
    <select id=\"symbol_select\"></select>

    <label>Timeframe</label>
    <select id=\"timeframe_select\">
      <option value=\"1m\">1m</option>
      <option value=\"5m\">5m</option>
      <option value=\"15m\">15m</option>
      <option value=\"1h\">1h</option>
      <option value=\"4h\">4h</option>
      <option value=\"1D\">1D</option>
    </select>

    <label>Policy JSON</label>
    <textarea id=\"policy\">{\n  \"symbol\": \"tBTCUSD\",\n  \"timeframe\": \"1m\"\n}</textarea>
    <div id=\"policy_err\" style=\"color:#b91c1c\"></div>

    <label>Configs JSON</label>
    <textarea id=\"configs\">{\n  \"features\": {\n    \"percentiles\": {\"ema_delta_pct\": [-0.05, 0.05], \"rsi\": [-1, 1]},\n    \"versions\": {\"feature_set\": \"v1\"}\n  },\n  \"thresholds\": {\"entry_conf_overall\": 0.5, \"regime_proba\": {\"balanced\": 0.5}},\n  \"gates\": {\"hysteresis_steps\": 2, \"cooldown_bars\": 0},\n  \"risk\": {\"risk_map\": [[0.6, 0.005], [0.7, 0.01]]},\n  \"ev\": {\"R_default\": 1.5}\n}</textarea>
    <div id=\"configs_err\" style=\"color:#b91c1c\"></div>

    <label>Candles JSON</label>
    <textarea id=\"candles\">{\n  \"open\": [1,2,3,4],\n  \"high\": [2,3,4,5],\n  \"low\": [0.5,1.5,2.5,3.5],\n  \"close\": [1.5,2.5,3.5,4.5],\n  \"volume\": [10,11,12,13]\n}</textarea>
    <div id=\"candles_err\" style=\"color:#b91c1c\"></div>

    <div style=\"display:flex; gap:8px;\">
      <button id=\"run\">Kör pipeline</button>
      <button id=\"save\">Spara</button>
      <button id=\"restore\">Återställ</button>
      <button id=\"fetch_pub\">Hämta publika candles</button>
      <button id=\"auth\">Auth‑check</button>
      <!-- overrides inaktiveras när SSOT används -->
      <button id=\"propose_cfg\">Föreslå ändring</button>
      <button id=\"submit_paper\">Submit paper order</button>
      <button id=\"reset_defaults\">Återställ defaults</button>
      <button id=\"clear_cache\">Rensa cache</button>
    </div>
    <div>
      <h3>Result</h3>
      <pre id=\"out\"></pre>
      <div id=\"summary\"></div>
    </div>
  </div>
  <script>
    const el = (id) => document.getElementById(id);
    const err = (id, msg) => { el(id).textContent = msg || ''; };
    const getJSON = (id, errId) => {
      try { const v = JSON.parse(el(id).value || '{}'); err(errId, ''); return v; }
      catch (e) { err(errId, 'Ogiltig JSON'); throw e; }
    };
    async function loadWhitelist() {
      const sel = el('symbol_select');
      try {
        const r = await fetch('/paper/whitelist');
        const data = await r.json();
        const symbols = Array.isArray(data.symbols) ? data.symbols.slice().sort() : [];
        sel.innerHTML = '';
        for (const s of symbols) {
          const opt = document.createElement('option');
          opt.value = s; opt.textContent = s; sel.appendChild(opt);
        }
      } catch {
        sel.innerHTML = '';
        ['tTESTBTC:TESTUSD'].forEach(s => { const o = document.createElement('option'); o.value=s; o.textContent=s; sel.appendChild(o); });
      }
    }
    const syncPolicyFromInputs = () => {
      try {
        const pol = getJSON('policy','policy_err');
        // Endast timeframe synkas in i policy; symbol hanteras separat för order
        pol.timeframe = el('timeframe_select')?.value || pol.timeframe || '1m';
        el('policy').value = JSON.stringify(pol, null, 2);
      } catch {}
    };
    const syncInputsFromPolicy = () => {
      try {
        const pol = getJSON('policy','policy_err');
        const symSel = el('symbol_select');
        if (symSel && symSel.options && symSel.options.length) {
          symSel.value = pol.symbol || symSel.value;
        }
        const tfSel = el('timeframe_select');
        if (tfSel) tfSel.value = pol.timeframe || '1m';
      } catch {}
    };
    let lastData = null;
    const renderSummary = (data) => {
      try {
        const a = data.result?.action;
        const sz = data.meta?.decision?.size;
        const reasons = data.meta?.decision?.reasons || [];
        el('summary').innerHTML = `<div>Action: <b>${a}</b> &nbsp; Size: <b>${(sz??0).toFixed(4)}</b></div>` +
          (reasons.length ? `<div>Reasons: ${reasons.map(r=>`<span>[${r}]</span>`).join(' ')}</div>` : '');
        lastData = data;
      } catch { el('summary').textContent = ''; }
    };
    const save = () => {
      localStorage.setItem('ui_policy', el('policy').value);
      localStorage.setItem('ui_configs', el('configs').value);
      localStorage.setItem('ui_candles', el('candles').value);
    };
    const restore = () => {
      const p = localStorage.getItem('ui_policy'); if (p) el('policy').value = p;
      const c = localStorage.getItem('ui_configs'); if (c) el('configs').value = c;
      const d = localStorage.getItem('ui_candles'); if (d) el('candles').value = d;
    };
    const clearCache = () => {
      try {
        localStorage.removeItem('ui_policy');
        localStorage.removeItem('ui_configs');
        localStorage.removeItem('ui_candles');
        err('policy_err',''); err('configs_err',''); err('candles_err','');
      } catch {}
    };
    async function hydrateConfigsFromDefaultsIfEmpty() {
      try {
        if ((el('configs').value || '').trim()) return; // redan satt lokalt
        const r = await fetch('/config/runtime');
        if (!r.ok) return;
        const data = await r.json();
        if (data && data.cfg) {
          el('configs').value = JSON.stringify(data.cfg, null, 2);
        }
      } catch {}
    }
    async function loadHealth() {
      try {
        const r = await fetch('/health');
        if (!r.ok) return;
        const d = await r.json();
        if (d) {
          if (el('cfg_ver')) el('cfg_ver').textContent = String(d.config_version ?? '-');
          if (el('cfg_hash')) el('cfg_hash').textContent = String(d.config_hash ?? '-').slice(0, 12);
        }
      } catch {}
    }
    el('save').addEventListener('click', save);
    el('restore').addEventListener('click', restore);
    el('clear_cache').addEventListener('click', () => { clearCache(); el('configs').value=''; hydrateConfigsFromDefaultsIfEmpty(); });
    el('reset_defaults').addEventListener('click', async () => { clearCache(); el('configs').value=''; await hydrateConfigsFromDefaultsIfEmpty(); save(); });
    el('timeframe_select').addEventListener('change', syncPolicyFromInputs);
    el('fetch_pub').addEventListener('click', async () => {
      try {
        const pol = getJSON('policy','policy_err');
        const tf = pol.timeframe || '1m';
        const sym = pol.symbol || 'tBTCUSD';
        const r = await fetch(`/public/candles?symbol=${encodeURIComponent(sym)}&timeframe=${encodeURIComponent(tf)}&limit=120`);
        const data = await r.json();
        el('candles').value = JSON.stringify(data, null, 2);
      } catch {}
    });
    el('auth').addEventListener('click', async () => {
      const r = await fetch('/auth/check');
      const data = await r.json();
      el('summary').innerHTML = `<div>Auth: ${data.ok ? 'OK' : 'FAIL'} (wallets=${data.wallets||0}, positions=${data.positions||0})</div>`;
    });
    // overrides borttagen i SSOT-läge
    el('propose_cfg').addEventListener('click', async () => {
      try {
        const rt = await fetch('/config/runtime');
        if (!rt.ok) { err('configs_err','Kunde inte läsa runtime'); return; }
        const rtData = await rt.json();
        const expected = Number(rtData?.version || 0);
        const patch = getJSON('configs','configs_err');
        const r = await fetch('/config/runtime/propose', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ patch, actor: 'ui', expected_version: expected })});
        if (!r.ok) { const t = await r.text(); err('configs_err', 'Propose fel: '+t); return; }
        const data = await r.json();
        el('configs').value = JSON.stringify(data.cfg, null, 2);
        save();
      } catch { err('configs_err','Propose fel'); }
    });
    el('run').addEventListener('click', async () => {
      let payload;
      try {
        payload = {
          policy: getJSON('policy','policy_err'),
          configs: getJSON('configs','configs_err'),
          candles: getJSON('candles','candles_err'),
          state: {}
        };
      } catch { return; }
      const r = await fetch('/strategy/evaluate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      const data = await r.json();
      el('out').textContent = JSON.stringify(data, null, 2);
      renderSummary(data);
    });
    // Autoload saved
    restore();
    hydrateConfigsFromDefaultsIfEmpty();
    loadWhitelist().then(syncInputsFromPolicy);
    loadHealth();

    el('submit_paper').addEventListener('click', async () => {
      try {
        if (!lastData) { err('policy_err','Kör pipeline först'); return; }
        const pol = getJSON('policy','policy_err');
        const action = lastData?.result?.action;
        const size = Number(lastData?.meta?.decision?.size || 0);
        if (!action || size <= 0) { err('configs_err','Ingen giltig order (action/size)'); return; }
        const orderSymbol = el('symbol_select')?.value || 'tTESTBTC:TESTUSD';
        const payload = { symbol: orderSymbol, side: action, size: size, type: 'MARKET' };
        const r = await fetch('/paper/submit', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        const data = await r.json();
        el('out').textContent = JSON.stringify(data, null, 2);
      } catch { err('configs_err','Submit fel'); }
    });
  </script>
</body>
</html>
"""


@app.post("/strategy/evaluate")
def strategy_evaluate(payload: dict = Body({})) -> dict:
    candles = payload.get("candles") or {
        "open": [1, 2, 3, 4],
        "high": [2, 3, 4, 5],
        "low": [0.5, 1.5, 2.5, 3.5],
        "close": [1.5, 2.5, 3.5, 4.5],
        "volume": [10, 11, 12, 13],
    }
    policy = payload.get("policy") or {"symbol": "tBTCUSD", "timeframe": "1m"}
    configs = payload.get("configs") or {}
    state = payload.get("state") or {}
    result, meta = evaluate_pipeline(candles, policy=policy, configs=configs, state=state)
    return {"result": result, "meta": meta}


@app.get("/public/candles")
def public_candles(symbol: str = "tBTCUSD", timeframe: str = "1m", limit: int = 120) -> dict:
    """Proxy till Bitfinex public candles och normaliserar till {open,high,low,close,volume}."""
    url = f"https://api-pub.bitfinex.com/v2/candles/trade:{timeframe}:{symbol}/hist"
    params = {"limit": max(1, min(int(limit), 500)), "sort": 1}
    r = httpx.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    opens: list[float] = []
    highs: list[float] = []
    lows: list[float] = []
    closes: list[float] = []
    volumes: list[float] = []
    if isinstance(data, list):
        for row in data:
            # Bitfinex format: [MTS, OPEN, CLOSE, HIGH, LOW, VOLUME]
            if isinstance(row, list) and len(row) >= 6:
                opens.append(float(row[1]))
                closes.append(float(row[2]))
                highs.append(float(row[3]))
                lows.append(float(row[4]))
                volumes.append(float(row[5]))
    return {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    }


@app.get("/auth/check")
async def auth_check() -> dict:
    """Read‑only smoke: wallets + positions (paper). Returnerar endast ok och antal poster."""
    w, p = await asyncio.gather(bfx_read.get_wallets(), bfx_read.get_positions())
    w_count = len(w) if isinstance(w, list) else 0
    p_count = len(p) if isinstance(p, list) else 0
    return {"ok": True, "wallets": w_count, "positions": p_count}


@app.get("/dev/overrides")
def dev_overrides() -> dict:
    """Returnera innehållet i dev.overrides.local.json om den finns, annars 404‑liknande svar."""
    p = Path.cwd() / "dev.overrides.local.json"
    if not p.exists():
        return {"error": "not_found"}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"error": "invalid_json"}


@app.post("/paper/submit")
async def paper_submit(payload: dict = Body(...)) -> dict:
    """Skicka en order till Bitfinex Paper (auth krävs via .env).

    OBS: Paper only – vi tvingar alltid testparet tTESTBTC:TESTUSD oavsett indata
    för att undvika risk för verklig handel.

    payload: {symbol, side:"LONG"|"SHORT"|"NONE", size:float, type?:"MARKET"|"LIMIT", price?:float}
    """
    # Använd endast symboler från whitelist; annars fall tillbaka till standard TEST-par
    requested_symbol = str(payload.get("symbol") or "tTESTBTC:TESTUSD").upper()
    symbol = requested_symbol if requested_symbol in TEST_SPOT_WHITELIST else "tTESTBTC:TESTUSD"
    side = str(payload.get("side") or "NONE").upper()
    size = float(payload.get("size") or 0.0)
    order_type = str(payload.get("type") or "MARKET").upper()
    price = payload.get("price")
    if side not in ("LONG", "SHORT") or size <= 0:
        return {"ok": False, "error": "invalid_action_or_size"}
    amount = size if side == "LONG" else -size

    # Bitfinex v2 order submit (MARKET/LIMIT):
    # endpoint: auth/w/order/submit, body: {type, symbol, amount, price?}
    # Bitfinex kräver EXCHANGE-* typer för spot/paper
    bfx_type = (
        "EXCHANGE MARKET"
        if order_type == "MARKET"
        else ("EXCHANGE LIMIT" if order_type == "LIMIT" else order_type)
    )
    body = {"type": bfx_type, "symbol": symbol, "amount": str(amount)}
    if order_type == "LIMIT" and price is not None:
        body["price"] = str(float(price))

    ec = get_exchange_client()
    try:
        resp = await ec.signed_request(method="POST", endpoint="auth/w/order/submit", body=body)
        data = resp.json() if hasattr(resp, "json") else {"status": resp.status_code}
        return {"ok": True, "exchange": "bitfinex", "request": body, "response": data}
    except httpx.HTTPStatusError as e:
        status = getattr(e.response, "status_code", None)
        text = getattr(e.response, "text", "")
        return {"ok": False, "status": status, "error": text or str(e)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/debug/auth")
def debug_auth() -> dict:
    """Maskerad vy av laddade auth‑nycklar (endast längd + suffix)."""
    s = get_settings()
    k = (s.BITFINEX_API_KEY or "").strip()
    masked = {
        "present": bool(k),
        "length": len(k),
        "suffix": k[-4:] if len(k) >= 4 else k,
    }
    return {"rest_api_key": masked}
