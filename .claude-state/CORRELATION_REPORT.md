# 전략 상관관계 분석 리포트

_Generated: 2026-04-11_
_데이터: 합성 OHLCV 500 캔들 (quality_audit와 동일)_

## 분석 범위

QUALITY_AUDIT.csv의 PASS 전략 중 현재 코드베이스에 존재하는 21개.

## 결과

| 항목 | 수치 |
|------|------|
| 분석 전략 | 21개 |
| 높은 상관 쌍 (\|r\| ≥ 0.7) | 0개 |
| 다양성 선정 (greedy) | 21개 |

## 🔥 높은 상관관계 쌍

상관계수 절대값 0.7 이상 — 하나는 중복으로 판단.

_(없음)_

## ✅ 다양성 확보된 전략 (Greedy 선정)

상관관계 0.7 미만의 전략들만 남긴 포트폴리오. 이 조합으로 앙상블 시 분산 효과 최대.

- `acceleration_band`
- `cmf`
- `dema_cross`
- `elder_impulse`
- `engulfing_zone`
- `frama`
- `htf_ema`
- `linear_channel_rev`
- `lob_maker`
- `momentum_quality`
- `narrow_range`
- `order_flow_imbalance_v2`
- `positional_scaling`
- `price_action_momentum`
- `price_cluster`
- `relative_volume`
- `roc_ma_cross`
- `supertrend_multi`
- `value_area`
- `volatility_cluster`
- `wick_reversal`

## 📁 결과 파일

- `.claude-state/CORRELATION_MATRIX.csv` — 전체 상관 행렬
- `scripts/correlation_analysis.py` — 재실행용 스크립트
