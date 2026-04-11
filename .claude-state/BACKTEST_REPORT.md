# 전략 품질 감사 리포트

_Generated: 2026-04-11_
_Data: 합성 OHLCV 500 캔들 (BTC-like, GBM + regime changes)_
_Fee: 0.1% | Slippage: 0.05%_

## 📊 요약

| 항목 | 수치 |
|------|------|
| 발견된 전략 클래스 | **390개** |
| 백테스트 완료 | 385개 |
| **PASS** | **23개** (6.0%) |
| **FAIL** | **362개** (94.0%) |
| 에러 | 5개 |
| Sharpe 중앙값 | 0.000 |
| Sharpe 평균 | -0.299 |

## ✅ PASS 전략 (23개)

기준: Sharpe ≥ 1.0, Max DD ≤ 20%, Profit Factor ≥ 1.5, Trades ≥ 15

| # | Name | Sharpe | WinRate | PF | MDD | Trades | Return |
|---|------|--------|---------|-----|-----|--------|--------|
| 1 | cmf | 6.853 | 57.1% | 2.29 | 4.3% | 28 | 15.57% |
| 2 | wick_reversal | 6.506 | 54.3% | 2.03 | 3.5% | 35 | 16.83% |
| 3 | elder_impulse | 6.290 | 62.5% | 2.70 | 3.5% | 16 | 10.88% |
| 4 | momentum_quality | 5.535 | 51.8% | 1.92 | 3.2% | 27 | 12.46% |
| 5 | engulfing_zone | 5.501 | 60.0% | 2.50 | 3.3% | 15 | 9.18% |
| 6 | supertrend_multi | 5.379 | 48.0% | 1.97 | 4.4% | 25 | 10.98% |
| 7 | value_area | 5.244 | 53.3% | 1.84 | 5.0% | 30 | 11.70% |
| 8 | price_action_momentum | 5.239 | 58.8% | 2.24 | 2.2% | 17 | 9.06% |
| 9 | order_flow_imbalance_v2 | 5.003 | 51.6% | 1.77 | 4.3% | 31 | 11.58% |
| 10 | htf_ema | 4.913 | 52.0% | 1.85 | 3.2% | 25 | 10.30% |
| 11 | linear_channel_rev | 4.622 | 50.0% | 1.85 | 5.3% | 24 | 9.28% |
| 12 | price_cluster | 4.507 | 53.3% | 2.06 | 2.2% | 15 | 7.30% |
| 13 | frama | 4.372 | 51.4% | 1.62 | 4.6% | 35 | 10.50% |
| 14 | narrow_range | 4.310 | 50.0% | 1.61 | 4.3% | 34 | 10.11% |
| 15 | nr7 | 4.310 | 50.0% | 1.61 | 4.3% | 34 | 10.11% |
| 16 | lob_maker | 4.093 | 56.2% | 1.93 | 2.3% | 16 | 6.36% |
| 17 | dema_cross | 3.805 | 50.0% | 1.70 | 3.2% | 20 | 6.99% |
| 18 | zero_lag_ema | 3.805 | 50.0% | 1.70 | 3.2% | 20 | 6.99% |
| 19 | relative_volume | 3.762 | 50.0% | 1.76 | 3.3% | 18 | 6.54% |
| 20 | positional_scaling | 3.724 | 50.0% | 1.74 | 3.3% | 18 | 6.47% |
| 21 | acceleration_band | 3.452 | 48.1% | 1.51 | 5.2% | 27 | 7.08% |
| 22 | volatility_cluster | 3.372 | 50.0% | 1.70 | 4.3% | 16 | 5.46% |
| 23 | roc_ma_cross | 2.985 | 50.0% | 1.58 | 2.5% | 18 | 4.92% |

## ❌ 주요 FAIL 사유

### 패턴 1: 거래 횟수 부족 (`trades < 15`)
대부분 FAIL 전략의 원인. Sharpe/승률이 좋아 보여도 표본이 부족.
- `adaptive_rsi`: Sharpe 6.66 하지만 10회만 거래
- `crossover_confluence`: Sharpe 6.46, 6회 거래
- `ema_dynamic_support`: Sharpe 5.95, 11회 거래
- `price_pattern_recog`: WR 100% 하지만 단 2회 거래 → 우연

### 패턴 2: Profit Factor 부족 (`PF < 1.5`)
거래는 많지만 기대값이 낮음. 실제 운영시 수수료로 잠식.
- `ema_stack`, `guppy`, `trend_momentum_blend`, `trim_ma_cross` 등

### 패턴 3: 중복 전략 (동일한 Sharpe/WR)
로직이 실질적으로 동일한 쌍 존재 → 즉시 제거 가능
- `narrow_range` ≡ `nr7` (Sharpe 4.310, 동일)
- `dema_cross` ≡ `zero_lag_ema` (Sharpe 3.805, 동일)
- `relative_volume` ≡ `positional_scaling` (유사)

## 🐛 로드/실행 에러 (5개)

핵심 전략인데 필요한 지표(`donchian_high`, `ema20`, `vwap`)가 합성 데이터에 없음.
운영 시 DataFeed가 계산해주지만, 오디트 스크립트에서는 별도 계산 필요.

- `donchian_breakout.DonchianBreakoutStrategy`: `donchian_high` 미존재
- `ema_cross.EmaCrossStrategy`: `ema20` 미존재
- `volume_breakout.VolumeBreakoutStrategy`: `ema20` 미존재
- `vpt_confirm.VolumePriceTrendConfirmStrategy`: `ema20` 미존재
- `vwap_reversion.VWAPReversionStrategy`: `vwap` 미존재

## 🎯 권장 조치

### 1. 즉시 삭제/비활성화 대상 (추정 ~340개)
- Sharpe < 0.5 or Trades < 15 or PF < 1.5 전략
- 중복 쌍 중 하나 (narrow_range↔nr7, dema↔zero_lag 등)

### 2. 상위 23개 PASS 전략 심층 검증
- 실제 거래소 데이터 (1년+)로 재백테스트
- Walk-Forward 검증 (IS/OOS 비율)
- 서로 다른 시장 레짐(불/베어/횡보)에서 안정성 확인
- PASS 전략 중 신호 상관관계 분석 → 다양성 확보

### 3. 에러 5개 수정
합성 데이터 생성 함수에 `donchian_high`, `ema20`, `vwap` 등 지표 추가

### 4. 합성 데이터의 한계
현재 결과는 **단일 합성 데이터셋 기반**이므로, 실제 운영 성능 보장 아님.
하지만 "거래 횟수 부족", "PF 낮음" 같은 FAIL 패턴은 실전에서도 동일하게 실패할 가능성이 높음.

## 📁 전체 결과

- CSV: `.claude-state/QUALITY_AUDIT.csv`
- 스크립트: `scripts/quality_audit.py`
