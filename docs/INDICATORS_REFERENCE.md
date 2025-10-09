# TECHNICAL INDICATORS REFERENCE GUIDE
## Trading Indicators Cheat Sheet för Feature Engineering

**Skapad:** 2025-10-09  
**Syfte:** Referensguide för att välja och förstå indikatorer vid model training  
**Target:** Single-user trading bot (Genesis-Core)

---

## 📋 INNEHÅLLSFÖRTECKNING

1. [Trend Indicators](#trend-indicators)
2. [Momentum Indicators](#momentum-indicators)
3. [Volatility Indicators](#volatility-indicators)
4. [Volume Indicators](#volume-indicators)
5. [Support/Resistance Indicators](#supportresistance-indicators)
6. [Multi-Timeframe Indicators](#multi-timeframe-indicators)
7. [Feature Combinations](#feature-combinations)
8. [Timeframe Guidelines](#timeframe-guidelines)
9. [Genesis-Core Current Features](#genesis-core-current-features)

---

## 1. TREND INDICATORS

### 📈 EMA (Exponential Moving Average)

**Syfte:** Identifiera trend direction och trend strength  
**Best för:** Trend-following strategies, smoothing price action

**Parametrar:**
```python
ema_period: int = 20  # Vanliga: 9, 20, 50, 200
```

**Timeframe Guidance:**
- **1m-5m:** 9-20 period (snabb respons)
- **15m-1h:** 20-50 period (balans)
- **4h-1d:** 50-200 period (långsiktig trend)

**Feature Ideas:**
```python
# Basic
ema_20 = ema(close, 20)

# Position relative to EMA
price_vs_ema = (close - ema_20) / ema_20  # Normalized distance

# EMA slope (trend strength)
ema_slope = (ema_20 - ema_20.shift(5)) / ema_20.shift(5)

# EMA cross
ema_fast_above_slow = (ema(close, 9) > ema(close, 20)).astype(int)

# Multiple EMA alignment (trend confirmation)
ema_alignment = (
    (ema_9 > ema_20) & 
    (ema_20 > ema_50) & 
    (ema_50 > ema_200)
).astype(int)
```

**Pros:**
- ✅ Snabbare än SMA (reagerar mer på recent data)
- ✅ Smooth, mindre noise än price

**Cons:**
- ❌ Lagging indicator (reagerar efter price movement)
- ❌ Falskt signals i sideways markets

---

### 📊 MACD (Moving Average Convergence Divergence)

**Syfte:** Identifiera momentum shifts och trend changes  
**Best för:** Divergence trading, momentum confirmation

**Parametrar:**
```python
fast_period: int = 12
slow_period: int = 26
signal_period: int = 9
```

**Timeframe Guidance:**
- **1h-4h:** Standard (12, 26, 9) fungerar bra
- **1d:** Kan öka till (26, 52, 18) för mindre noise

**Feature Ideas:**
```python
macd_line = ema(close, 12) - ema(close, 26)
signal_line = ema(macd_line, 9)
histogram = macd_line - signal_line

# Features
macd_histogram_normalized = histogram / close  # Normalized
macd_cross = (macd_line > signal_line).astype(int)
macd_divergence = detect_divergence(close, macd_line)  # Custom function
```

**Pros:**
- ✅ Fångar momentum shifts tidigt
- ✅ Works well med divergence analysis

**Cons:**
- ❌ Lagging (uses EMAs)
- ❌ Många false signals i ranging markets

---

### 🎯 ADX (Average Directional Index)

**Syfte:** Mäta trend STRENGTH (inte direction!)  
**Best för:** Filter för trend vs ranging markets

**Parametrar:**
```python
adx_period: int = 14  # Standard
```

**Interpretation:**
- **ADX < 20:** Weak trend / ranging market
- **ADX 20-25:** Emerging trend
- **ADX > 25:** Strong trend
- **ADX > 50:** Very strong trend

**Timeframe Guidance:**
- **All timeframes:** 14 period är standard och fungerar bra

**Feature Ideas:**
```python
adx = calculate_adx(high, low, close, 14)

# Market state classification
market_state = np.where(adx > 25, 'trending', 'ranging')

# ADX slope (strengthening/weakening)
adx_slope = adx - adx.shift(5)

# Combined with +DI/-DI
plus_di = calculate_plus_di(high, low, close, 14)
minus_di = calculate_minus_di(high, low, close, 14)
trend_direction = (plus_di > minus_di).astype(int)
```

**Pros:**
- ✅ Excellent för att undvika ranging markets
- ✅ Non-directional (works för both bull/bear)

**Cons:**
- ❌ Lagging indicator
- ❌ Doesn't tell direction (behöver +DI/-DI)

---

## 2. MOMENTUM INDICATORS

### ⚡ RSI (Relative Strength Index)

**Syfte:** Identifiera overbought/oversold conditions  
**Best för:** Mean reversion, divergence trading

**Parametrar:**
```python
rsi_period: int = 14  # Standard
```

**Interpretation:**
- **RSI > 70:** Overbought (möjlig correction)
- **RSI < 30:** Oversold (möjlig bounce)
- **RSI 40-60:** Neutral zone

**Timeframe Guidance:**
- **1m-15m:** 9 period (snabbare signals)
- **1h-4h:** 14 period (standard)
- **1d:** 14-21 period (smooth)

**Feature Ideas:**
```python
rsi_14 = calculate_rsi(close, 14)

# Normalized RSI (0-1 range)
rsi_normalized = rsi_14 / 100

# RSI zones
rsi_overbought = (rsi_14 > 70).astype(int)
rsi_oversold = (rsi_14 < 30).astype(int)

# RSI divergence
rsi_bull_div = detect_bullish_divergence(close, rsi_14)
rsi_bear_div = detect_bearish_divergence(close, rsi_14)

# RSI slope
rsi_momentum = rsi_14 - rsi_14.shift(3)
```

**Pros:**
- ✅ Bounded (0-100), easy to interpret
- ✅ Works well för mean reversion

**Cons:**
- ❌ Can stay overbought/oversold i strong trends
- ❌ False signals i trending markets

---

### 🌊 Stochastic Oscillator

**Syfte:** Compare current close to recent range  
**Best för:** Overbought/oversold, momentum shifts

**Parametrar:**
```python
k_period: int = 14  # %K period
d_period: int = 3   # %D smoothing
```

**Interpretation:**
- **Stoch > 80:** Overbought
- **Stoch < 20:** Oversold
- **%K crosses %D:** Momentum shift

**Timeframe Guidance:**
- **1h-4h:** (14, 3) standard
- **Fast Stochastic:** (5, 3) för snabbare signals

**Feature Ideas:**
```python
k_line = stochastic_k(high, low, close, 14)
d_line = sma(k_line, 3)

# Features
stoch_overbought = (k_line > 80).astype(int)
stoch_oversold = (k_line < 20).astype(int)
stoch_cross = (k_line > d_line).astype(int)
```

**Pros:**
- ✅ Sensitiv till momentum changes
- ✅ Good för range-bound markets

**Cons:**
- ❌ Very noisy i trending markets
- ❌ Many false signals

---

### 📉 Rate of Change (ROC)

**Syfte:** Mäta percentage change over time  
**Best för:** Momentum strength, velocity

**Parametrar:**
```python
roc_period: int = 9  # Lookback period
```

**Feature Ideas:**
```python
roc = ((close - close.shift(9)) / close.shift(9)) * 100

# Multi-period ROC
roc_fast = calculate_roc(close, 5)
roc_slow = calculate_roc(close, 14)

# ROC acceleration
roc_acceleration = roc - roc.shift(3)
```

**Pros:**
- ✅ Direct measure of momentum
- ✅ Unbounded (kan capture extremes)

**Cons:**
- ❌ Very volatile
- ❌ No overbought/oversold levels

---

## 3. VOLATILITY INDICATORS

### 📏 ATR (Average True Range)

**Syfte:** Mäta market volatility  
**Best för:** Position sizing, stop-loss placement, volatility filtering

**Parametrar:**
```python
atr_period: int = 14  # Standard
```

**Timeframe Guidance:**
- **All timeframes:** 14 period är standard

**Feature Ideas:**
```python
atr_14 = calculate_atr(high, low, close, 14)

# ATR as % of price (normalized)
atr_pct = atr_14 / close

# Volatility regime
volatility_regime = np.where(
    atr_pct > atr_pct.rolling(50).mean() * 1.5,
    'high_vol',
    'normal_vol'
)

# ATR expansion/contraction
atr_change = (atr_14 - atr_14.shift(5)) / atr_14.shift(5)
```

**Pros:**
- ✅ Essential för risk management
- ✅ Adaptive to market conditions

**Cons:**
- ❌ Lagging (moving average)
- ❌ Doesn't predict direction

---

### 📊 Bollinger Bands

**Syfte:** Dynamic support/resistance baserat på volatility  
**Best för:** Mean reversion, breakout detection

**Parametrar:**
```python
bb_period: int = 20  # SMA period
bb_std: float = 2.0  # Standard deviations
```

**Timeframe Guidance:**
- **1h-4h:** (20, 2.0) standard
- **Higher TF:** Kan öka period till 50

**Feature Ideas:**
```python
bb_middle = sma(close, 20)
bb_std = close.rolling(20).std()
bb_upper = bb_middle + (bb_std * 2)
bb_lower = bb_middle - (bb_std * 2)

# Position inom bands (redan i Genesis-Core!)
bb_position = (close - bb_lower) / (bb_upper - bb_lower)

# Band width (volatility measure)
bb_width = (bb_upper - bb_lower) / bb_middle

# Squeeze detection (low volatility)
bb_squeeze = bb_width < bb_width.rolling(50).quantile(0.2)

# Touch/break upper/lower
bb_touch_upper = (close >= bb_upper * 0.99).astype(int)
bb_touch_lower = (close <= bb_lower * 1.01).astype(int)
```

**Pros:**
- ✅ Adapts to volatility
- ✅ Visual och intuitive
- ✅ **Redan implementerad i Genesis-Core!**

**Cons:**
- ❌ Lagging (uses SMA)
- ❌ False breakouts

---

### 🎲 Historical Volatility

**Syfte:** Mäta realized volatility  
**Best för:** Regime classification, risk adjustment

**Parametrar:**
```python
hv_period: int = 20  # Lookback period
annualize: bool = True  # Convert to annual %
```

**Feature Ideas:**
```python
returns = close.pct_change()
hist_vol = returns.rolling(20).std() * np.sqrt(252)  # Annualized

# Volatility percentile
vol_percentile = hist_vol.rolling(252).rank(pct=True)

# Volatility regime
vol_regime = pd.cut(
    vol_percentile,
    bins=[0, 0.33, 0.67, 1.0],
    labels=['low_vol', 'med_vol', 'high_vol']
)
```

---

## 4. VOLUME INDICATORS

### 📊 Volume

**Syfte:** Konfirmera price movements  
**Best för:** Breakout confirmation, divergence

**Feature Ideas:**
```python
volume_sma = volume.rolling(20).mean()

# Volume ratio
volume_ratio = volume / volume_sma

# High volume (anomaly detection)
high_volume = (volume > volume_sma * 2).astype(int)

# Volume trend
volume_trend = volume_sma.diff(5) / volume_sma.shift(5)

# Price-volume divergence
pv_divergence = (
    (close > close.shift(5)) & 
    (volume < volume.shift(5))
).astype(int)
```

**Timeframe Guidance:**
- **1h-4h:** Volume är mest reliable
- **1m-15m:** Very noisy, use with caution

---

### 📈 OBV (On-Balance Volume)

**Syfte:** Cumulative volume flow  
**Best för:** Trend confirmation, divergence

**Feature Ideas:**
```python
obv = calculate_obv(close, volume)

# OBV trend
obv_sma = obv.rolling(20).mean()
obv_trend = (obv > obv_sma).astype(int)

# OBV divergence
obv_divergence = detect_divergence(close, obv)
```

---

### 💰 VWAP (Volume Weighted Average Price)

**Syfte:** Average price weighted by volume  
**Best för:** Intraday support/resistance, institutional levels

**Timeframe Guidance:**
- **1m-1h:** Most useful intraday
- **Daily reset:** VWAP resets varje dag

**Feature Ideas:**
```python
vwap = calculate_vwap(high, low, close, volume)

# Position relative to VWAP
price_vs_vwap = (close - vwap) / vwap

# VWAP bands (±1 std dev)
vwap_std = calculate_vwap_std(high, low, close, volume)
vwap_upper = vwap + vwap_std
vwap_lower = vwap - vwap_std
```

**Pros:**
- ✅ Institutional reference point
- ✅ Dynamic support/resistance

**Cons:**
- ❌ Primarily intraday tool
- ❌ Requires volume data

---

## 5. SUPPORT/RESISTANCE INDICATORS

### 🎯 Pivot Points

**Syfte:** Calculate potential support/resistance levels  
**Best för:** Intraday trading, target levels

**Parametrar:**
```python
pivot_type: str = 'standard'  # standard, fibonacci, woodie, camarilla
```

**Feature Ideas:**
```python
pivot = (high_prev + low_prev + close_prev) / 3
r1 = (2 * pivot) - low_prev
s1 = (2 * pivot) - high_prev
r2 = pivot + (high_prev - low_prev)
s2 = pivot - (high_prev - low_prev)

# Distance to levels
dist_to_r1 = (r1 - close) / close
dist_to_s1 = (close - s1) / close
```

---

### 📍 Support/Resistance Zones

**Syfte:** Identify price levels with historical significance  
**Best för:** Entry/exit points, breakout trading

**Feature Ideas:**
```python
# Recent swing highs/lows
swing_high = close.rolling(10).max()
swing_low = close.rolling(10).min()

# Distance to swing levels
dist_to_swing_high = (swing_high - close) / close
dist_to_swing_low = (close - swing_low) / close

# Number of touches (strength)
resistance_strength = count_touches(close, swing_high, tolerance=0.01)
```

---

## 6. MULTI-TIMEFRAME INDICATORS

### 🔄 Higher Timeframe Trend

**Syfte:** Align med larger trend (trade in direction of HTF)  
**Best för:** Trend filtering, confluence

**Example (Trading 1h, using 4h HTF):**
```python
# On 1h chart, calculate 4h indicators
htf_ema_20 = resample_to_htf(close, '1h', '4h').rolling(20).mean()
htf_rsi = calculate_rsi(resample_to_htf(close, '1h', '4h'), 14)
htf_trend = (htf_ema_20 > htf_ema_20.shift(1)).astype(int)

# Features
htf_trend_aligned = (
    (close > htf_ema_20) if htf_trend == 1 else (close < htf_ema_20)
).astype(int)
```

**Timeframe Ratios:**
- **Trading 15m:** Use 1h HTF (4x)
- **Trading 1h:** Use 4h HTF (4x)
- **Trading 4h:** Use 1d HTF (6x)

**Pros:**
- ✅ Dramatically reduces false signals
- ✅ Aligns med institutional flow

---

### 🎯 Trend Confluence

**Syfte:** Count how many indicators agree on direction  
**Best för:** High-confidence signals

**Feature (redan i Genesis-Core!):**
```python
trend_confluence = (
    (close > ema_20) +           # Price above EMA
    (ema_9 > ema_20) +          # Fast EMA > Slow EMA
    (rsi > 50) +                # RSI bullish
    (macd_line > signal_line) + # MACD bullish
    (adx > 25)                  # Strong trend
) / 5  # Normalize to 0-1

# 0.0 = All bearish
# 0.5 = Neutral
# 1.0 = All bullish
```

---

## 7. FEATURE COMBINATIONS

### 🎨 Recommended Feature Sets

#### **Minimal Set (Current Genesis-Core)**
```python
features = [
    'bb_position',        # Volatility-adjusted price position
    'trend_confluence',   # Multi-indicator trend agreement
    'rsi'                # Momentum
]
# → 3 features (currently underperforming)
```

#### **Basic Trend-Following Set**
```python
features = [
    'price_vs_ema',      # Trend position
    'ema_slope',         # Trend strength
    'adx',               # Trend quality filter
    'rsi',               # Momentum
    'bb_position',       # Volatility context
    'volume_ratio'       # Confirmation
]
# → 6 features
```

#### **Momentum + Mean Reversion Set**
```python
features = [
    'rsi',               # Momentum
    'rsi_divergence',    # Reversal signals
    'bb_position',       # Overbought/oversold
    'bb_squeeze',        # Volatility breakout
    'stoch_k',           # Fast momentum
    'volume_spike'       # Confirmation
]
# → 6 features
```

#### **Robust Multi-Timeframe Set**
```python
features = [
    # Current TF
    'bb_position',
    'rsi',
    'adx',
    'atr_pct',
    
    # Higher TF
    'htf_ema_trend',
    'htf_rsi',
    'htf_adx',
    
    # Confluence
    'trend_confluence',
    'price_vs_htf_ema',
    'volume_ratio'
]
# → 10 features (recommended for stability)
```

#### **Advanced Kitchen Sink**
```python
features = [
    # Trend
    'ema_9', 'ema_20', 'ema_50',
    'ema_slope',
    'price_vs_ema',
    'ema_alignment',
    
    # Momentum
    'rsi', 'rsi_divergence',
    'macd_histogram',
    'stoch_k', 'stoch_d',
    'roc',
    
    # Volatility
    'atr_pct',
    'bb_position', 'bb_width', 'bb_squeeze',
    'hist_vol', 'vol_percentile',
    
    # Volume
    'volume_ratio',
    'obv_trend',
    'price_vs_vwap',
    
    # HTF
    'htf_ema_trend',
    'htf_rsi',
    'htf_adx',
    
    # Meta
    'trend_confluence',
    'regime_classification'
]
# → 27 features (risk of overfitting, use with caution!)
```

---

## 8. TIMEFRAME GUIDELINES

### ⏰ Timeframe Selection Matrix

| Timeframe | Pros | Cons | Recommended For |
|-----------|------|------|----------------|
| **1m** | Fast signals, many trades | Very noisy, high slippage | Scalping (NOT recommended för ML) |
| **5m** | Decent signal count | Still noisy | Day trading |
| **15m** | Balance speed/noise | Requires attention | Active trading |
| **1h** | Good signal/noise ratio | Moderate trade frequency | Swing trading (RECOMMENDED) |
| **4h** | Clean signals, stable | Fewer trades | Position trading (RECOMMENDED) |
| **1d** | Very stable, low noise | Very few signals | Long-term (low frequency) |

### 🎯 Genesis-Core Recommendation

**Primary Timeframe:** `1h` eller `4h`
- ✅ Best signal/noise ratio för ML
- ✅ Enough data för backtesting
- ✅ Manageable trade frequency
- ✅ Lower slippage impact

**Current Issue:**
- 1h med endast 3 features → Inte tillräckligt information
- Förslag: Lägg till 4-7 features från "Robust Multi-Timeframe Set"

---

## 9. GENESIS-CORE CURRENT FEATURES

### ✅ Implementerade Features

#### **1. bb_position**
```python
# Bollinger Band Position (0-1 range)
bb_position = (close - bb_lower) / (bb_upper - bb_lower)

# 0.0 = At lower band (oversold)
# 0.5 = At middle (SMA20)
# 1.0 = At upper band (overbought)
```
**Analysis:**
- ✅ Good: Volatility-adjusted, bounded
- ⚠️ Limitation: Lagging, needs confirmation

#### **2. trend_confluence**
```python
# Multi-indicator trend agreement (0-1 range)
trend_confluence = sum([
    close > ema_20,
    ema_9 > ema_20,
    rsi > 50,
    # ... more conditions
]) / total_conditions
```
**Analysis:**
- ✅ Good: Combines multiple signals
- ❌ Problem: **CRITICAL DRIFT detected (PSI=0.305)**
- 🔧 Fix: Recalculate eller ta bort denna feature

#### **3. rsi**
```python
rsi = calculate_rsi(close, 14)
```
**Analysis:**
- ✅ Good: Standard momentum indicator
- ⚠️ Limitation: Alone är inte tillräckligt

### ❌ Current Issue

**Problem:**
```
Only 3 features → Low predictive power
AUC = 0.49 (random guessing)
trend_confluence has CRITICAL drift
```

**Solution:**
```
Add 4-7 more features från "Robust Multi-Timeframe Set"
→ Target: 7-10 features för optimal balance
```

---

## 🚀 NEXT STEPS FÖR GENESIS-CORE

### **Immediate Actions:**

1. **Fix Drift Issue**
   ```python
   # Option A: Recalculate trend_confluence
   # Option B: Ta bort och ersätt med andra features
   ```

2. **Add Essential Features**
   ```python
   # Minimum additions:
   - adx (trend strength filter)
   - ema_slope (trend direction)
   - atr_pct (volatility context)
   - volume_ratio (confirmation)
   ```

3. **Test 4h Timeframe**
   ```bash
   # 4h kan ge mer stabila signals
   python scripts/precompute_features.py --symbol tBTCUSD --timeframe 4h
   python scripts/train_model.py --symbol tBTCUSD --timeframe 4h --version v12_4h
   ```

4. **Feature Importance Analysis**
   ```bash
   # Se vilka features är verkligen prediktiva
   python scripts/analyze_feature_importance.py --symbol tBTCUSD --timeframe 1h
   ```

---

## 📚 REFERENSER

- **Technical Analysis Basics:** 
  - Murphy, John J. "Technical Analysis of the Financial Markets"
  
- **ML for Trading:**
  - López de Prado, Marcos. "Advances in Financial Machine Learning"
  
- **Indicator Implementations:**
  - TA-Lib: https://ta-lib.org/
  - Pandas-TA: https://github.com/twopirllc/pandas-ta

---

## 🎯 SAMMANFATTNING

### **Key Takeaways:**

1. **Diversifiera Features:**
   - Trend + Momentum + Volatility + Volume
   - Minst 6-10 features för robust ML

2. **Använd Higher Timeframe:**
   - 4h eller 1d för mer stabila signals
   - Reduce noise, improve edge

3. **Combine Complementary Indicators:**
   - Trend (EMA, ADX)
   - Momentum (RSI, MACD)
   - Volatility (ATR, BB)
   - Volume (confirmation)

4. **Avoid Overfitting:**
   - 7-10 features är sweet spot
   - 27+ features = risk för overfit

5. **Test Systematically:**
   - Grid search över feature combinations
   - Use Decision Matrix för objective selection
   - Validate med Purged WFCV

**Lycka till med champion hunting! 🏆**


