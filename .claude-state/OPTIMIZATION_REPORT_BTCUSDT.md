# Strategy Optimization Report — BTC/USDT

_Generated: 2026-04-17T15:29:29.385056Z_
_Data: 4320 candles (2025-10-19 16:00:00+00:00 ~ 2026-04-17 15:00:00+00:00)_
_Slippage: 0.1% | Fee: 0.1%_

## relative_volume

| Params | AvgSharpe | AvgReturn | AvgPF | AvgTrades | MC_p | Consistency | Pass |
|--------|-----------|-----------|-------|-----------|------|-------------|------|
| _RVOL_BUY_SELL=1.6, _RSI_BUY_MAX=60, _RSI_SELL_MIN=40 | -0.083 | -0.09% | 1.436 | 15.5 | 0.491 | 0/4 | FAIL |
| _RVOL_BUY_SELL=1.6, _RSI_BUY_MAX=68, _RSI_SELL_MIN=40 | -0.359 | -1.19% | 1.32 | 22.0 | 0.5095 | 0/4 | FAIL |
| _RVOL_BUY_SELL=1.6, _RSI_BUY_MAX=68, _RSI_SELL_MIN=32 | -0.618 | -2.00% | 1.212 | 27.5 | 0.51 | 0/4 | FAIL |
| _RVOL_BUY_SELL=1.6, _RSI_BUY_MAX=60, _RSI_SELL_MIN=32 | -0.766 | -1.80% | 1.142 | 21.0 | 0.523 | 0/4 | FAIL |
| _RVOL_BUY_SELL=1.3, _RSI_BUY_MAX=68, _RSI_SELL_MIN=32 | -0.967 | -2.60% | 1.151 | 34.5 | 0.5465 | 0/4 | FAIL |

### 레짐별 성과 (best params)

| Regime | Chunks | AvgSharpe | AvgReturn | AvgTrades | Candles |
|--------|--------|-----------|-----------|-----------|---------|
| TREND_UP | 11 | -1.281 | +0.04% | 1.5 | 350 |
| TREND_DOWN | 19 | -1.914 | -0.26% | 1.8 | 739 |
| RANGING | 31 | -3.887 | -0.68% | 2.2 | 1213 |

## narrow_range

| Params | AvgSharpe | AvgReturn | AvgPF | AvgTrades | MC_p | Consistency | Pass |
|--------|-----------|-----------|-------|-----------|------|-------------|------|
| ATR_THRESHOLD=0.75, VOL_SPIKE_MULT=1.0 | -0.481 | -0.92% | 42449940736.824 | 3.0 | -1 | 0/4 | FAIL |
| ATR_THRESHOLD=0.75, VOL_SPIKE_MULT=1.2 | -0.481 | -0.92% | 42449940736.824 | 3.0 | -1 | 0/4 | FAIL |
| ATR_THRESHOLD=0.75, VOL_SPIKE_MULT=1.5 | -0.556 | -1.08% | 42449940736.666 | 3.0 | -1 | 0/4 | FAIL |
| ATR_THRESHOLD=0.85, VOL_SPIKE_MULT=1.5 | -1.561 | -1.81% | 1.193 | 10.0 | -1 | 0/4 | FAIL |
| ATR_THRESHOLD=0.85, VOL_SPIKE_MULT=1.2 | -1.678 | -1.98% | 1.165 | 10.0 | -1 | 0/4 | FAIL |

### 레짐별 성과 (best params)

| Regime | Chunks | AvgSharpe | AvgReturn | AvgTrades | Candles |
|--------|--------|-----------|-----------|-----------|---------|
| TREND_UP | 11 | 1.253 | +0.51% | 0.5 | 350 |
| TREND_DOWN | 19 | -0.569 | -0.08% | 0.3 | 739 |
| RANGING | 31 | -3.705 | -0.68% | 0.6 | 1213 |

## value_area

| Params | AvgSharpe | AvgReturn | AvgPF | AvgTrades | MC_p | Consistency | Pass |
|--------|-----------|-----------|-------|-----------|------|-------------|------|
| _VA_MULT=0.7, _MIN_BREACH=1.0 | -2.274 | -3.48% | 0.728 | 11.0 | -1 | 0/4 | FAIL |
| _VA_MULT=0.7, _MIN_BREACH=1.5 | -2.274 | -3.48% | 0.728 | 11.0 | -1 | 0/4 | FAIL |
| _VA_MULT=0.7, _MIN_BREACH=2.0 | -2.274 | -3.48% | 0.728 | 11.0 | -1 | 0/4 | FAIL |
| _VA_MULT=0.5, _MIN_BREACH=1.0 | -3.328 | -5.06% | 0.583 | 11.8 | -1 | 0/4 | FAIL |
| _VA_MULT=0.5, _MIN_BREACH=1.5 | -3.328 | -5.06% | 0.583 | 11.8 | -1 | 0/4 | FAIL |

### 레짐별 성과 (best params)

| Regime | Chunks | AvgSharpe | AvgReturn | AvgTrades | Candles |
|--------|--------|-----------|-----------|-----------|---------|
| TREND_UP | 11 | 0.692 | +0.19% | 1.1 | 350 |
| TREND_DOWN | 19 | -1.255 | +0.02% | 1.4 | 739 |
| RANGING | 31 | -4.063 | -0.66% | 1.8 | 1213 |

## 요약

- **최적화 전략**: 3개
- **PASS**: 0개
