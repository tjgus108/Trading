# Strategy Optimization Report — BTC/USDT

_Generated: 2026-04-17T15:21:48.162902Z_
_Data: 4320 candles (2025-10-19 16:00:00+00:00 ~ 2026-04-17 15:00:00+00:00)_
_Slippage: 0.1% | Fee: 0.1%_

## relative_volume

| Params | AvgSharpe | AvgReturn | AvgPF | AvgTrades | MC_p | Consistency | Pass |
|--------|-----------|-----------|-------|-----------|------|-------------|------|
| _RVOL_BUY_SELL=1.6, _RSI_BUY_MAX=60, _RSI_SELL_MIN=40 | 3.446 | +6.71% | 2.204 | 14.5 | 0.428 | 0/2 | FAIL |
| _RVOL_BUY_SELL=1.6, _RSI_BUY_MAX=68, _RSI_SELL_MIN=40 | 2.842 | +6.34% | 1.916 | 20.0 | 0.44 | 0/2 | FAIL |
| _RVOL_BUY_SELL=1.6, _RSI_BUY_MAX=68, _RSI_SELL_MIN=32 | 2.018 | +4.99% | 1.61 | 24.5 | 0.444 | 0/2 | FAIL |
| _RVOL_BUY_SELL=1.3, _RSI_BUY_MAX=68, _RSI_SELL_MIN=40 | 1.894 | +5.44% | 1.759 | 27.5 | 0.456 | 0/2 | FAIL |
| _RVOL_BUY_SELL=1.3, _RSI_BUY_MAX=68, _RSI_SELL_MIN=32 | 1.641 | +5.30% | 1.505 | 32.0 | 0.485 | 0/2 | FAIL |

### 레짐별 성과 (best params)

| Regime | Chunks | AvgSharpe | AvgReturn | AvgTrades | Candles |
|--------|--------|-----------|-----------|-----------|---------|
| TREND_UP | 11 | -1.281 | +0.04% | 1.5 | 350 |
| TREND_DOWN | 19 | -1.914 | -0.26% | 1.8 | 739 |
| RANGING | 31 | -3.887 | -0.68% | 2.2 | 1213 |

## narrow_range

| Params | AvgSharpe | AvgReturn | AvgPF | AvgTrades | MC_p | Consistency | Pass |
|--------|-----------|-----------|-------|-----------|------|-------------|------|
| ATR_THRESHOLD=0.75, VOL_SPIKE_MULT=1.0 | -0.068 | -0.58% | 84899881471.774 | 2.5 | -1 | 0/2 | FAIL |
| ATR_THRESHOLD=0.75, VOL_SPIKE_MULT=1.2 | -0.068 | -0.58% | 84899881471.774 | 2.5 | -1 | 0/2 | FAIL |
| ATR_THRESHOLD=0.75, VOL_SPIKE_MULT=1.5 | -0.068 | -0.58% | 84899881471.774 | 2.5 | -1 | 0/2 | FAIL |
| ATR_THRESHOLD=0.95, VOL_SPIKE_MULT=1.0 | -0.897 | -2.08% | 0.99 | 17.0 | 0.537 | 0/2 | FAIL |
| ATR_THRESHOLD=0.95, VOL_SPIKE_MULT=1.5 | -1.039 | -2.20% | 0.968 | 17.0 | 0.536 | 0/2 | FAIL |

### 레짐별 성과 (best params)

| Regime | Chunks | AvgSharpe | AvgReturn | AvgTrades | Candles |
|--------|--------|-----------|-----------|-----------|---------|
| TREND_UP | 11 | 1.253 | +0.51% | 0.5 | 350 |
| TREND_DOWN | 19 | -0.569 | -0.08% | 0.3 | 739 |
| RANGING | 31 | -3.705 | -0.68% | 0.6 | 1213 |

## value_area

| Params | AvgSharpe | AvgReturn | AvgPF | AvgTrades | MC_p | Consistency | Pass |
|--------|-----------|-----------|-------|-----------|------|-------------|------|
| _VA_MULT=0.7, _MIN_BREACH=1.0 | -2.388 | -3.70% | 0.706 | 12.0 | -1 | 0/2 | FAIL |
| _VA_MULT=0.7, _MIN_BREACH=1.5 | -2.388 | -3.70% | 0.706 | 12.0 | -1 | 0/2 | FAIL |
| _VA_MULT=0.7, _MIN_BREACH=2.0 | -2.388 | -3.70% | 0.706 | 12.0 | -1 | 0/2 | FAIL |
| _VA_MULT=0.5, _MIN_BREACH=1.0 | -2.784 | -4.52% | 0.658 | 13.0 | -1 | 0/2 | FAIL |
| _VA_MULT=0.5, _MIN_BREACH=1.5 | -2.784 | -4.52% | 0.658 | 13.0 | -1 | 0/2 | FAIL |

### 레짐별 성과 (best params)

| Regime | Chunks | AvgSharpe | AvgReturn | AvgTrades | Candles |
|--------|--------|-----------|-----------|-----------|---------|
| TREND_UP | 11 | 0.692 | +0.19% | 1.1 | 350 |
| TREND_DOWN | 19 | -1.255 | +0.02% | 1.4 | 739 |
| RANGING | 31 | -4.063 | -0.66% | 1.8 | 1213 |

## 요약

- **최적화 전략**: 3개
- **PASS**: 0개
