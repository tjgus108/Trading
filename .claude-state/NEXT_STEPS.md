# 실전 Bybit 데이터 시뮬레이션 결과 기반 — 작업 방향 전환

_Updated: 2026-04-13_

## ⛔ 핵심 교훈: 합성 데이터 과적합 확인

합성 데이터 Sharpe 4.26이었던 OFI_v2가 실제 Bybit에서 **-12.65%**.
합성 데이터 +15.76%였던 linear_channel_rev가 실제에서 **-18.85%**.

**합성 데이터 기반 SIM 개선 대부분이 과적합이었음.**

## ✅ 실제 Bybit 데이터에서 살아남은 전략 (3 PASS)

| 전략 | Return | Sharpe | PF | Trades |
|------|--------|--------|-----|--------|
| **trima** | +11.28% | 3.74 | 2.21 | 28 |
| **bull_bear_power** | +9.56% | 2.47 | 1.56 | 49 |
| **adaptive_ma_cross** | +8.57% | 3.17 | 2.05 | 27 |

## 🎯 다음 작업 (우선순위)

### 1. 실전 데이터 기반 품질 감사 재실행 (최우선)
- `scripts/quality_audit.py`를 실제 Bybit 데이터로 재실행
- 합성 데이터 PASS 22개 vs 실전 PASS 비교
- 실전 PASS 전략만 STRATEGY_REGISTRY에 활성화

### 2. 실전 PASS 3개 전략 심층 분석
- trima, bull_bear_power, adaptive_ma_cross의 공통점 파악
- 왜 이 3개만 실전에서 살아남았는지 분석
- Walk-Forward 검증 (IS/OOS 70/30)

### 3. 실전 유망 전략 (근접 PASS) 개선
- engulfing_zone (+5.42%, PF 3.48 but 8 trades)
- relative_volume (+5.07%, PF 1.45)
- vol_adj_trend (+4.43%, PF 2.44 but 11 trades)

### 4. 과적합된 전략 분석 및 원인 규명
- 합성에서 +17.85% → 실전 -12.65%가 된 OFI_v2 분석
- 과적합 공통 패턴 도출 → 향후 방지

## ⛔ 금지
- 합성 데이터만으로 전략 최적화 금지
- 새 전략 파일 생성 금지
- 실전 데이터 검증 없이 PASS 판정 금지
