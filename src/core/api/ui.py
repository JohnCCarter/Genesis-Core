from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/ui", response_class=HTMLResponse)
def ui_page() -> str:
    return """
<!doctype html>
<html lang="sv">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
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
  <div class="row">
    <label>Order‑symbol (TEST)</label>
    <select id="symbol_select" disabled></select>
    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#374151;">
      <input type="checkbox" id="auto_thresholds" checked />
      <label for="auto_thresholds">Auto‑trösklar per symbol</label>
      <input type="checkbox" id="low_threshold_test" />
      <label for="low_threshold_test">Låg tröskel (test)</label>
    </div>
    <div id="symbol_info" style="font-size:12px; color:#6b7280"></div>

    <label>Timeframe</label>
    <select id="timeframe_select">
      <option value="1m">1m</option>
      <option value="5m">5m</option>
      <option value="15m">15m</option>
      <option value="1h">1h</option>
      <option value="4h">4h</option>
      <option value="1D">1D</option>
    </select>

    <label>Policy‑symbol (real)</label>
    <select id="policy_symbol_select"></select>

    <label>Bearer token (för /config/runtime/propose)</label>
    <div style="display:flex; gap:8px; align-items:center;">
      <input id="bearer" type="password" placeholder="Bearer token" style="flex:1; padding:6px;" />
      <button id="save_bearer">Spara token</button>
    </div>

    <label>Policy JSON</label>
    <textarea id="policy">{\n  "symbol": "tBTCUSD",\n  "timeframe": "1m"\n}</textarea>
    <div id="policy_err" style="color:#b91c1c"></div>

    <label>Configs JSON</label>
    <textarea id="configs">{\n  "features": {\n    "percentiles": {"ema_delta_pct": [-0.05, 0.05], "rsi": [-1, 1]},\n    "versions": {"feature_set": "v1"}\n  },\n  "thresholds": {"entry_conf_overall": 0.5, "regime_proba": {"balanced": 0.5}},\n  "gates": {"hysteresis_steps": 2, "cooldown_bars": 0},\n  "risk": {"risk_map": [[0.6, 0.005], [0.7, 0.01]]},\n  "ev": {"R_default": 1.5}\n}</textarea>
    <div id="configs_err" style="color:#b91c1c"></div>

    <label>Candles JSON</label>
    <textarea id="candles">{\n  "symbol": "tETHUSD",\n  "open": [1,2,3,4],\n  "high": [2,3,4,5],\n  "low": [0.5,1.5,2.5,3.5],\n  "close": [1.5,2.5,3.5,4.5],\n  "volume": [10,11,12,13]\n}</textarea>
    <div id="candles_err" style="color:#b91c1c"></div>

    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#374151;">
      <input type="checkbox" id="ri_observability_opt_in" />
      <label for="ri_observability_opt_in">SCPE RI runtime-observability (opt-in)</label>
    </div>

    <div style="display:flex; gap:8px;">
      <button id="run">Kör pipeline</button>

      <button id="restore">Återställ</button>
      <button id="fetch_pub">Hämta publika candles</button>
      <button id="auth">Auth‑check</button>
      <!-- overrides inaktiveras när SSOT används -->
      <button id="propose_cfg">Föreslå ändring</button>
      <button id="submit_paper">Submit paper order</button>
      <button id="reset_defaults">Återställ defaults</button>
      <button id="clear_cache">Rensa cache</button>
    </div>
    <div id="symbol_mismatch_warning" style="display:none; color:#dc2626; font-size:14px; margin-top:8px; padding:8px; background:#fef2f2; border:1px solid #fecaca; border-radius:4px;">
      ⚠️ Varning: Policy-symbol matchar inte Candles-data. Klicka "Hämta publika candles" för att uppdatera.
    </div>
    <div id="ui_status" style="display:none; color:#065f46; font-size:13px; margin-top:6px;"></div>
    <div>
      <h3>Result</h3>
      <pre id="out"></pre>
      <div id="summary"></div>
    </div>

    <div style="margin-top:16px; border-top:1px solid #e5e7eb; padding-top:12px;">
      <h3 style="margin:4px 0;">Wallets</h3>
      <div style="display:flex; gap:8px; align-items:center;">
        <button id="refresh_wallets">Uppdatera</button>
        <label style="font-size:12px; color:#374151;"><input type="checkbox" id="auto_wallets" /> Auto‑refresh 5s</label>
      </div>
      <pre id="wallets_out"></pre>
    </div>

    <div style="margin-top:16px; border-top:1px solid #e5e7eb; padding-top:12px;">
      <h3 style="margin:4px 0;">Positions</h3>
      <div style="display:flex; gap:8px; align-items:center;">
        <button id="refresh_positions">Uppdatera</button>
        <label style="font-size:12px; color:#374151;"><input type="checkbox" id="auto_positions" /> Auto‑refresh 5s</label>
      </div>
      <pre id="positions_out"></pre>
    </div>

    <div style="margin-top:16px; border-top:1px solid #e5e7eb; padding-top:12px;">
      <h3 style="margin:4px 0;">Orders</h3>
      <div style="display:flex; gap:8px; align-items:center;">
        <button id="refresh_orders">Uppdatera</button>
        <label style="font-size:12px; color:#374151;"><input type="checkbox" id="auto_orders" /> Auto‑refresh 5s</label>
      </div>
      <pre id="orders_out"></pre>
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
        // Fyll policy-symboler (real) från whitelist (map TEST->real)
        const realSel = el('policy_symbol_select');
        if (realSel) {
          realSel.innerHTML = '';
          const reals = symbols.map(s => testToReal(s));
          const uniqueReals = Array.from(new Set(reals)).sort();
          for (const rs of uniqueReals) {
            const opt = document.createElement('option');
            opt.value = rs; opt.textContent = rs; realSel.appendChild(opt);
          }
        }
        await refreshSymbolInfo();
        syncInputsFromPolicy();
      } catch {
        sel.innerHTML = '';
        ['tTESTBTC:TESTUSD'].forEach(s => { const o = document.createElement('option'); o.value=s; o.textContent=s; sel.appendChild(o); });
        const realSel = el('policy_symbol_select');
        if (realSel) { realSel.innerHTML = ''; ['tBTCUSD','tETHUSD'].forEach(rs=>{ const o=document.createElement('option'); o.value=rs; o.textContent=rs; realSel.appendChild(o); }); }
        await refreshSymbolInfo();
      }
    }
    function testToReal(sym) {
      try {
        const u = (sym||'').toUpperCase();
        const core = u.replace(/^T/,'');
        const [base,quoteRaw] = core.includes(':') ? core.split(':',1).concat(core.split(':').slice(1).join(':')) : [core,'USD'];
        const quote = (quoteRaw||'USD').replace('TEST','');
        const baseClean = base.replace('TEST','');
        return 't'+baseClean+quote;
      } catch { return 'tBTCUSD'; }
    }
    function realToTest(real) {
      try {
        const u = (real||'').toUpperCase();
        const m = u.match(/^T?([A-Z]+)(USD|USDT)$/);
        const base = (m && m[1]) ? m[1] : 'BTC';
        const quote = (m && m[2]) ? m[2] : 'USD';
        const candidate = 'tTEST'+base+':'+'TEST'+quote;
        const sel = el('symbol_select');
        if (sel && Array.from(sel.options).some(o=>o.value===candidate)) return candidate;
        return 'tTESTBTC:TESTUSD';
      } catch { return 'tTESTBTC:TESTUSD'; }
    }
    async function refreshSymbolInfo() {
      try {
        // Läs från policy-symbol (real symbol) istället för order-symbol (TEST)
        const pol = getJSON('policy','policy_err');
        const realSym = pol.symbol || 'tBTCUSD';
        const testSym = realToTest(realSym);
        const r = await fetch(`/paper/estimate?symbol=${encodeURIComponent(testSym)}`);
        if (!r.ok) return;
        const d = await r.json();
        const min = Number(d.required_min||0);
        const minm = Number(d.min_with_margin||0);
        const px = Number(d.last_price||0);
        const usd = Number(d.usd_available||0);
        const est = Number(d.est_max_size||0);
        el('symbol_info').textContent = `Min: ${min} | Min+margin: ${minm} | Pris: ${px} | USD: ${usd} | Max≈ ${est}`;
        if (el('auto_thresholds')?.checked) {
          try {
            const cfg = getJSON('configs','configs_err');
            cfg.thresholds = cfg.thresholds || {};
            // välj låg tröskel om aktiverad, annars normal 0.5
            const low = !!el('low_threshold_test')?.checked;
            cfg.thresholds.entry_conf_overall = low ? 0.20 : 0.5;
            cfg.thresholds.regime_proba = { balanced: 0.5 };
            cfg.risk = cfg.risk || {};
            cfg.risk.risk_map = [[low ? 0.20 : 0.5, minm]];
            el('configs').value = JSON.stringify(cfg, null, 2);
            err('configs_err','');
          } catch {}
        }
      } catch {}
    }
    const syncPolicyFromInputs = () => {
      try {
        const pol = getJSON('policy','policy_err');
        // timeframe
        pol.timeframe = el('timeframe_select')?.value || pol.timeframe || '1m';
        // symbol från policy_symbol_select
        const ps = el('policy_symbol_select');
        if (ps && ps.value) pol.symbol = ps.value;
        el('policy').value = JSON.stringify(pol, null, 2);
        // härled TEST-symbol och synka order-select
        const derived = realToTest(pol.symbol||'tBTCUSD');
        const symSel = el('symbol_select');
        if (symSel) symSel.value = derived;
        // validera symbol-match
        validateSymbolMatch();
      } catch {}
    };
    const validateSymbolMatch = () => {
      try {
        const pol = getJSON('policy','policy_err');
        const candles = getJSON('candles','candles_err');
        const policySymbol = pol.symbol || '';
        const candlesSymbol = candles.symbol || '';
        const mismatch = policySymbol && candlesSymbol && policySymbol !== candlesSymbol;
        const warning = el('symbol_mismatch_warning');
        const runBtn = el('run');
        if (warning) warning.style.display = mismatch ? 'block' : 'none';
        if (runBtn) runBtn.disabled = mismatch;
      } catch {}
    };
    async function fetchCandlesForPolicy() {
      try {
        const pol = getJSON('policy','policy_err');
        const tf = pol.timeframe || '1m';
        const sym = pol.symbol || 'tBTCUSD';
        const r = await fetch(`/public/candles?symbol=${encodeURIComponent(sym)}&timeframe=${encodeURIComponent(tf)}&limit=120`);
        if (!r.ok) return false;
        const data = await r.json();
        const out = Object.assign({}, data, { symbol: sym, timeframe: tf });
        const has = Array.isArray(out.open) && out.open.length > 0;
        el('candles').value = JSON.stringify(out, null, 2);
        validateSymbolMatch();
        const st = el('ui_status'); if (st) { st.textContent = has ? 'Candles uppdaterade' : 'Inga candles hittades'; st.style.display = 'block'; setTimeout(()=>{ st.style.display='none'; }, 1500); }
        return has;
      } catch { return false; }
    }
    async function autoUpdateAfterPolicyChange() {
      try {
        syncPolicyFromInputs();
        const ok = await fetchCandlesForPolicy();
        if (!ok) return;
        // Uppdatera symbol-info och configs om auto-thresholds är aktivt
        await refreshSymbolInfo();
        // kör pipeline automatiskt
        const payload = {
          policy: getJSON('policy','policy_err'),
          configs: getJSON('configs','configs_err'),
          candles: getJSON('candles','candles_err'),
          state: buildRuntimeObservabilityState()
        };
        const r = await fetch('/strategy/evaluate', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
        const data = await r.json();
        el('out').textContent = JSON.stringify(data, null, 2);
        renderSummary(data);
        const st = el('ui_status'); if (st) { st.textContent = 'Pipeline uppdaterad'; st.style.display = 'block'; setTimeout(()=>{ st.style.display='none'; }, 1200); }
      } catch {}
    }
    const syncInputsFromPolicy = () => {
      try {
        const pol = getJSON('policy','policy_err');
        const symSel = el('symbol_select');
        const psSel = el('policy_symbol_select');
        if (psSel) psSel.value = pol.symbol || psSel.value || 'tBTCUSD';
        if (symSel) symSel.value = realToTest(pol.symbol||'tBTCUSD');
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
        const riObs = data.meta?.observability?.scpe_ri_v1;
        el('summary').innerHTML = `<div>Action: <b>${a}</b> &nbsp; Size: <b>${(sz??0).toFixed(4)}</b></div>` +
          (reasons.length ? `<div>Reasons: ${reasons.map(r=>`<span>[${r}]</span>`).join(' ')}</div>` : '') +
          (riObs ? `<div>RI obs: authority=<b>${riObs.authoritative_regime}</b> shadow=<b>${riObs.shadow_regime}</b> mismatch=<b>${riObs.regime_mismatch}</b></div>` : '');
        lastData = data;
      } catch { el('summary').textContent = ''; }
    };
    function buildRuntimeObservabilityState() {
      const state = {};
      if (el('ri_observability_opt_in')?.checked) {
        state.observability = { scpe_ri_v1: true };
      }
      return state;
    }
    const save = () => {
      localStorage.setItem('ui_policy', el('policy').value);
      localStorage.setItem('ui_configs', el('configs').value);
      localStorage.setItem('ui_candles', el('candles').value);
    };
    // autosave på förändring
    el('policy').addEventListener('input', save);
    el('configs').addEventListener('input', save);
    el('candles').addEventListener('input', save);
    const restore = () => {
      const p = localStorage.getItem('ui_policy'); if (p) el('policy').value = p;
      const c = localStorage.getItem('ui_configs'); if (c) el('configs').value = c;
      const d = localStorage.getItem('ui_candles'); if (d) el('candles').value = d;
      const st = el('ui_status'); if (st) { st.textContent = 'Lokalt UI återställt'; st.style.display = 'block'; setTimeout(()=>{ st.style.display = 'none'; }, 1500); }
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
    function loadBearer() {
      try { const b = localStorage.getItem('ui_bearer') || ''; if (el('bearer')) el('bearer').value = b; } catch {}
    }
    el('restore').addEventListener('click', () => { restore(); syncInputsFromPolicy(); validateSymbolMatch(); });
    const sb = el('save_bearer'); if (sb) sb.addEventListener('click', () => { try { const v = el('bearer')?.value || ''; localStorage.setItem('ui_bearer', v); } catch {} });
    el('clear_cache').addEventListener('click', () => { clearCache(); el('configs').value=''; hydrateConfigsFromDefaultsIfEmpty(); });
    el('reset_defaults').addEventListener('click', async () => { clearCache(); el('configs').value=''; await hydrateConfigsFromDefaultsIfEmpty(); save(); });
    el('timeframe_select').addEventListener('change', autoUpdateAfterPolicyChange);
    const symSel = el('symbol_select'); if (symSel) symSel.addEventListener('change', refreshSymbolInfo);
    const at = el('auto_thresholds'); if (at) at.addEventListener('change', refreshSymbolInfo);
    const lt = el('low_threshold_test'); if (lt) lt.addEventListener('change', refreshSymbolInfo);
    const psSel = el('policy_symbol_select'); if (psSel) psSel.addEventListener('change', autoUpdateAfterPolicyChange);
    el('fetch_pub').addEventListener('click', async () => {
      try {
        const pol = getJSON('policy','policy_err');
        const tf = pol.timeframe || '1m';
        const sym = pol.symbol || 'tBTCUSD';
        const r = await fetch(`/public/candles?symbol=${encodeURIComponent(sym)}&timeframe=${encodeURIComponent(tf)}&limit=120`);
        const data = await r.json();
        // injicera symbol/timeframe för validering
        const out = Object.assign({}, data, { symbol: sym, timeframe: tf });
        el('candles').value = JSON.stringify(out, null, 2);
        // validera efter uppdatering
        validateSymbolMatch();
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
        const bearer = localStorage.getItem('ui_bearer') || '';
        const headers = {'Content-Type':'application/json'};
        if (bearer) headers['Authorization'] = 'Bearer ' + bearer;
        const r = await fetch('/config/runtime/propose', { method:'POST', headers, body: JSON.stringify({ patch, actor: 'ui', expected_version: expected })});
        if (!r.ok) { const t = await r.text(); err('configs_err', 'Propose fel: '+t); return; }
        const data = await r.json();
        el('configs').value = JSON.stringify(data.cfg, null, 2);
        save();
        err('configs_err','');
        // refresh status panel
        loadHealth();
        // Visa bekräftelse
        const st = el('ui_status');
        if (st) {
          st.textContent = `✓ Config sparad (version ${data.version})`;
          st.style.display = 'block';
          st.style.color = '#065f46';
          setTimeout(() => { st.style.display = 'none'; }, 2500);
        }
      } catch (e) { err('configs_err','Propose fel: ' + String(e)); }
    });
    el('run').addEventListener('click', async () => {
      let payload;
      try {
        payload = {
          policy: getJSON('policy','policy_err'),
          configs: getJSON('configs','configs_err'),
          candles: getJSON('candles','candles_err'),
          state: buildRuntimeObservabilityState()
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
    loadWhitelist().then(() => {
      syncInputsFromPolicy();
      // validering efter att UI är laddat
      validateSymbolMatch();
    });
    loadHealth();
    loadBearer();

    el('submit_paper').addEventListener('click', async () => {
      try {
        if (!lastData) { err('policy_err','Kör pipeline först'); return; }
        const pol = getJSON('policy','policy_err');
        const candlesObj = getJSON('candles','candles_err');
        const hasData = Array.isArray(candlesObj?.open) && candlesObj.open.length>0;
        if (!hasData) { err('candles_err','Inga candles för vald symbol/timeframe'); return; }
        const action = lastData?.result?.action;
        let size = Number(lastData?.meta?.decision?.size || 0);
        const orderSymbol = el('symbol_select')?.value || realToTest(pol.symbol||'tBTCUSD');
        // Force min+margin om size <= 0: hämta estimate och sätt storlek därefter
        if (size <= 0 && action) {
          try {
            const est = await fetch(`/paper/estimate?symbol=${encodeURIComponent(orderSymbol)}`);
            if (est.ok) {
              const d = await est.json();
              const minm = Number(d.min_with_margin||0);
              const estMax = Number(d.est_max_size||0);
              size = Math.max(minm, isFinite(estMax) && estMax>0 ? Math.min(minm, estMax) : minm);
            }
          } catch {}
        }
        if (!action || size <= 0) { err('configs_err','Ingen giltig order (action/size)'); return; }
        const payload = { symbol: orderSymbol, side: action, size: size, type: 'MARKET' };
        const r = await fetch('/paper/submit', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        const data = await r.json();
        el('out').textContent = JSON.stringify(data, null, 2);
      } catch { err('configs_err','Submit fel'); }
    });

    async function fetchJSON(url, fallback={}) {
      try { const r = await fetch(url); if (!r.ok) return fallback; return await r.json(); } catch { return fallback; }
    }
    async function loadWallets() {
      const d = await fetchJSON('/account/wallets', {items:[]});
      el('wallets_out').textContent = JSON.stringify(d, null, 2);
    }
    async function loadPositions() {
      const d = await fetchJSON('/account/positions', {items:[]});
      el('positions_out').textContent = JSON.stringify(d, null, 2);
    }
    async function loadOrders() {
      const d = await fetchJSON('/account/orders', {items:[]});
      el('orders_out').textContent = JSON.stringify(d, null, 2);
    }
    let tW=null, tP=null, tO=null;
    el('refresh_wallets').addEventListener('click', loadWallets);
    el('refresh_positions').addEventListener('click', loadPositions);
    el('refresh_orders').addEventListener('click', loadOrders);
    el('auto_wallets').addEventListener('change', (e)=>{
      if (e.target.checked) { loadWallets(); tW = setInterval(loadWallets, 5000); }
      else { if (tW) clearInterval(tW); tW=null; }
    });
    el('auto_positions').addEventListener('change', (e)=>{
      if (e.target.checked) { loadPositions(); tP = setInterval(loadPositions, 5000); }
      else { if (tP) clearInterval(tP); tP=null; }
    });
    el('auto_orders').addEventListener('change', (e)=>{
      if (e.target.checked) { loadOrders(); tO = setInterval(loadOrders, 5000); }
      else { if (tO) clearInterval(tO); tO=null; }
    });
  </script>
</body>
</html>
"""
