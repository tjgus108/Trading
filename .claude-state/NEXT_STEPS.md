# Next Steps

_Last updated: 2026-06-01 (Cycle 257 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 251, 252, 253, 254, 255, 256, 257

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 251 | B+D+F | wick_reversal ATR 필터, Deflated Sharpe Ratio 유틸리티 |
| 252 | E+A+F | validate_ohlcv() 헬퍼, DSR→BundleOOS 통합 |
| 253 | C+B+F | load_csv_ohlcv/resample_ohlcv, 전환쿠션, RollingOOS max_oos_sharpe_std 파라미터화 |
| 254 | D+E+F | nr_range_ratio/nr_atr_ratio 피처, --csv-dir 옵션, **MC 버그 수정** |
| 255 | A+C+F | GARCH CSV 생성, 0-trade score 버그 수정, SOL 6/22 PASS 확인 |
| 256 | B+D+F | atr_multiplier_tp 3.0→3.5, mom_quality_score/trend_strength 피처 추가, **SOL 8/22 PASS** |
| 257 | B+D+F | HIGH conf 1.5→1.2, REGIME bull/ranging 피처 추가, OOS std 저거래 제외, **ETH 5/22 PASS** |

### 🎯 Cycle 258 작업 방향 (258 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### B(리스크): HIGH Confidence 혼합 효과 재검토
- Cycle 257 결과: HIGH conf 1.5→1.2 → ETH +2, SOL -4 PASS (mixed)
  - acceleration_band SOL MDD 23%→8.3% ✓ (목표 달성!)
  - price_action_momentum SOL 4/4→1/4 ✗ (borderline 전략 수익 감소)
- 고려: **전략별 confidence 동적 조정**보다 종목별 차이 분석 우선
  - SOL은 trend-persistent → HIGH conf 유지 유리
  - ETH는 더 volatile → HIGH conf 축소 유리
- 제안: HIGH conf 1.2→1.35 (중간값) 또는 전략별 파라미터로 분리

#### C(데이터): ETH/SOL CSV 데이터 생성 (합성 개선)
- 현재 ETH/SOL은 Block Bootstrap 합성 데이터 (seed 고정)
- BTC 1h CSV (data/historical/binance/BTCUSDT/1h.csv) 형식으로 ETH/SOL CSV 생성 필요
  - scripts/generate_garch_csv.py가 있다면 ETH/SOL 생성 호출
  - 없으면 BTC GARCH 패턴에서 SOL-like (higher vol), ETH-like 데이터 생성
- ETH/SOL CSV 있으면: 8 windows (vs 현재 4 windows) → 더 신뢰할 수 있는 결과

#### F(리서치): OOS Sharpe std 저거래 제외 효과 측정
- Cycle 257에서 walk_forward.py std 계산 개선 (저거래 fold 제외) 
- Bundle OOS에도 동일 로직 적용 필요 여부 확인
  - scripts/run_bundle_oos.py의 OOS std 계산 방식 확인
  - 저거래 fold 제외 후 narrow_range의 std 5.203 → 얼마나 감소하는지 측정

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단 (합성 데이터만 사용 가능)
- BTC GARCH CSV (12,000 rows): PASS 0/22 — trend 지속성 부족 (BTC 합성 데이터 개선 필요)
- ETH/SOL: Block Bootstrap 합성 4 windows (BTC CSV는 8 windows) — 불균형

### 핵심 메트릭 (Cycle 257)
- 테스트: 8369 passed, 23 skipped (변경 없음)
- Paper Sim BTC: 0/22 (top: supertrend_multi sharpe 0.50, price_cluster sharpe 0.41)
- Paper Sim ETH: **5/22 PASS** ↑ (Cycle 256 3/22)
  - TOP: momentum_quality(4/4, 5.56), supertrend_multi(3/4, 4.78), price_action_momentum(2/4, 3.80)
- Paper Sim SOL: **4/22 PASS** ↓ (Cycle 256 8/22)
  - TOP: momentum_quality(4/4, 4.89), acceleration_band(2/4, MDD 8.3%!)
  - acceleration_band MDD: 23.0%→8.3% ← HIGH conf 1.5→1.2 주효
- Bundle OOS BTC 4h: 0/5 PASS (narrow_range #1 Score 87.1)

### 주요 코드 변경 이력 (Cycle 257)
1. `src/backtest/engine.py:203` — HIGH conf_mult 1.5→1.2
2. `src/risk/manager.py:404` — CONFIDENCE_MULTIPLIER HIGH 1.5→1.2
3. `src/ml/features.py:405,417` — REGIME_FEATURE_CONFIG bull+mom_quality_score, ranging+trend_strength
4. `src/backtest/walk_forward.py:83,317,362` — WindowResult.oos_trades, OOS std 저거래 제외
5. `tests/test_risk_manager.py:871,900` — test_confidence_high_is_1_2x_medium 업데이트
