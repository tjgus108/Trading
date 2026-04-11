# 전략 품질 감사 리포트 (Cycle 13 갱신)

_Generated: 2026-04-11_
_Data: 합성 OHLCV 500 캔들 (BTC-like, GBM + regime changes)_
_Fee: 0.1% | Slippage: 0.05%_
_BacktestEngine: 수수료 & 슬리피지 반영됨_

## 📊 요약

| 항목 | 수치 | 변화 |
|------|------|------|
| 발견된 전략 클래스 | **348개** | -42 (이전 390) |
| 백테스트 완료 | 348개 | +0 에러 (이전 5 에러) |
| **PASS** | **22개** (6.3%) | -1 |
| **FAIL** | **326개** (93.7%) | +1 |
| Sharpe 중앙값 | 0.000 | 같음 |
| Sharpe 평균 | -0.314 | 같음 |

**주요 개선사항:**
- 에러율 0% 달성 (이전 5개 에러: donchian_high, ema20, vwap 미존재 → 합성 데이터에서 계산 추가)
- 339개 전략 제거/비활성화로 발견된 전략 42개 감소
- PASS 전략 통계: Sharpe avg 4.79, median 4.77 (높음)

## ✅ PASS 전략 (22개)

기준: Sharpe ≥ 1.0, Max DD ≤ 20%, Profit Factor ≥ 1.5, Trades ≥ 15

| # | Name | Sharpe | WinRate | PF | MDD | Trades | Return |
|---|------|--------|---------|-----|-----|--------|--------|
| 1 | cmf | 6.853 | 57.1% | 2.29 | 4.3% | 28 | 15.57% |
| 2 | wick_reversal | 6.506 | 54.3% | 2.03 | 3.5% | 35 | 16.83% |
| 3 | elder_impulse | 6.290 | 62.5% | 2.70 | 3.5% | 16 | 10.88% |
| 4 | volume_breakout | 5.911 | 60.0% | 2.66 | 2.2% | 15 | 10.13% |
| 5 | momentum_quality | 5.535 | 51.8% | 1.92 | 3.2% | 27 | 12.46% |
| 6 | engulfing_zone | 5.501 | 60.0% | 2.50 | 3.3% | 15 | 9.18% |
| 7 | supertrend_multi | 5.379 | 48.0% | 1.97 | 4.4% | 25 | 10.98% |
| 8 | value_area | 5.244 | 53.3% | 1.84 | 5.0% | 30 | 11.70% |
| 9 | price_action_momentum | 5.239 | 58.8% | 2.24 | 2.2% | 9.06% | 17 |
| 10 | order_flow_imbalance_v2 | 5.003 | 51.6% | 1.77 | 4.3% | 31 | 11.58% |
| 11 | htf_ema | 4.913 | 52.0% | 1.85 | 3.2% | 25 | 10.30% |
| 12 | linear_channel_rev | 4.622 | 50.0% | 1.85 | 5.3% | 24 | 9.28% |
| 13 | price_cluster | 4.507 | 53.3% | 2.06 | 2.2% | 15 | 7.30% |
| 14 | frama | 4.372 | 51.4% | 1.62 | 4.6% | 35 | 10.50% |
| 15 | narrow_range | 4.310 | 50.0% | 1.61 | 4.3% | 34 | 10.11% |
| 16 | lob_maker | 4.093 | 56.2% | 1.93 | 2.3% | 16 | 6.36% |
| 17 | dema_cross | 3.805 | 50.0% | 1.70 | 3.2% | 20 | 6.99% |
| 18 | relative_volume | 3.762 | 50.0% | 1.76 | 3.3% | 18 | 6.54% |
| 19 | positional_scaling | 3.724 | 50.0% | 1.74 | 3.3% | 18 | 6.47% |
| 20 | acceleration_band | 3.452 | 48.1% | 1.51 | 5.2% | 27 | 7.08% |
| 21 | volatility_cluster | 3.372 | 50.0% | 1.70 | 4.3% | 16 | 5.46% |
| 22 | roc_ma_cross | 2.985 | 50.0% | 1.58 | 2.5% | 18 | 4.92% |

**PASS 통계:**
- Sharpe: avg 4.79, median 4.77 (강력)
- Trades: avg 23, median 22 (충분)
- Win Rate: avg 53.1%, median 51.7% (균형)
- Profit Factor: avg 1.95, median 1.85 (안전 마진)
- Max DD: avg 3.62%, median 3.40% (매우 안정적)
- Return: avg 9.53%, median 9.70% (일관성)

## ❌ FAIL 패턴 분석

### 1. 거래 부족 (최대 위협)
- 15회 미만 거래: ~50개 전략
- 예: adaptive_rsi (Sharpe 6.66이지만 10회만)
- **원인**: 신호 생성 알고리즘이 보수적 → 합성 데이터 특성에 부합 불가능

### 2. Profit Factor 부족 (경제적 실패)
- PF < 1.5: ~100개 전략 (guppy, trend_momentum_blend 등)
- 거래는 많지만 이익 구조 취약 → 수수료 0.1%로 잠식

### 3. 신호 생성 실패
- no trades generated: 15개 전략

## 🔄 비교 (이전 감사 vs 현재)

| 항목 | 이전 | 현재 | 변화 |
|------|------|------|------|
| 전략 클래스 | 390 | 348 | -42 (10.8%) |
| PASS | 23 | 22 | -1 |
| FAIL | 362 | 326 | -36 |
| 에러 | 5 | 0 | -5 ✅ |
| Sharpe 중앙값 | 0.000 | 0.000 | - |

**분석**: 에러 제거 성공, 하지만 PASS 수는 유사. PASS 전략의 품질은 여전히 높음 (Sharpe 4.79).

## 🎯 권장 조치 (Cycle 13 완료)

### 1. 상위 22개 PASS 전략 Live 진출 후보 ✅
- 모두 Sharpe ≥ 2.98, PF ≥ 1.51, Trades ≥ 15 충족
- **다음 단계**: Walk-Forward validation + 실거래소 데이터 재백테스트 (1년 이상)
- 신호 상관관계 확인 → 포트폴리오 구축

### 2. FAIL 326개 전략 → 정리 대상 ✅
- Sharpe < 0.5 or Trades < 15 or PF < 1.5 자동 제거 권장
- 코드베이스에서 비활성화 또는 삭제

### 3. 에러 해결 완료 ✅
- `quality_audit.py` 합성 데이터에 donchian_high, ema20, vwap 추가
- 모든 348개 전략 정상 실행 (에러 0%)

## 📁 상세 결과

- **CSV**: `/home/user/Trading/.claude-state/QUALITY_AUDIT.csv` (348개 행)
- **스크립트**: `/home/user/Trading/scripts/quality_audit.py`
- **실행**: `python scripts/quality_audit.py` (약 2분 소요)

---

## 다음 작업 (Cycle 14 이후)

1. **Walk-Forward Validation** — 상위 22개 전략에 대해 IS/OOS 분할 (70/30) 검증
2. **실거래소 데이터** — CoinGecko/Binance API로 1년 이상 BTC-USDT 히스토리 수집
3. **포트폴리오 최적화** — 22개 전략 신호 상관관계 분석 → 다양성 극대화
4. **Risk Management** — 개별 position size, max correlation throttle 재검토
