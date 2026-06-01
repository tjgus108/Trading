# Next Steps

_Last updated: 2026-06-01 (Cycle 256 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 251, 252, 253, 254, 255, 256

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 251 | B+D+F | wick_reversal ATR 필터, Deflated Sharpe Ratio 유틸리티 |
| 252 | E+A+F | validate_ohlcv() 헬퍼, DSR→BundleOOS 통합 |
| 253 | C+B+F | load_csv_ohlcv/resample_ohlcv, 전환쿠션, RollingOOS max_oos_sharpe_std 파라미터화 |
| 254 | D+E+F | nr_range_ratio/nr_atr_ratio 피처, --csv-dir 옵션, **MC 버그 수정** |
| 255 | A+C+F | GARCH CSV 생성, 0-trade score 버그 수정, SOL 6/22 PASS 확인 |
| 256 | B+D+F | atr_multiplier_tp 3.0→3.5, mom_quality_score/trend_strength 피처 추가, **SOL 8/22 PASS** |

### 🎯 Cycle 257 작업 방향 (257 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): MDD 초과 전략 개선
- momentum_quality SOL: MDD 11.4% OK지만 ETH 일부 윈도우 MDD 22% 초과
- acceleration_band SOL: MDD 23.0% > 20% → FAIL 주요 원인
- DrawdownMonitor 임계값 재검토 또는 아 포지션 사이징에서 MDD 사전 조절
- 제안: BacktestEngine의 `risk_per_trade` (현 0.01 × conf_mult) 조정 실험
  - HIGH confidence: 1.5% → 1.2% (MDD 감소 목표)

#### D(ML): REGIME_FEATURE_CONFIG 업데이트
- `mom_quality_score`, `trend_strength`를 bull/ranging 레짐에 추가
  - REGIME_FEATURE_CONFIG["bull"]에 추가 시 `test_regime_feature_selector.py` 테스트 업데이트 필요
  - 신중히 진행 (test count hardcoded 확인 후 업데이트)
- BTC vs SOL 성과 차이 분석:
  - price_action_momentum SOL 4/4 PASS (sharpe 5.48) vs BTC 0/8 PASS (sharpe -3.37)
  - 가설: GARCH BTC CSV에 trend 지속성 부족 → BTC용 block bootstrap 데이터 생성 검토

#### F(리서치): Bundle OOS Sharpe std 안정화
- 현재 OOS Sharpe std: 3.9~8.5 (기준 1.5 대비 매우 큰)
- 원인: 4h 봉 데이터 부족 + 파라미터 과적합
- 제안: walk_forward.py의 `OOS_STD_MAX` 기준 완화 (0.8 → 1.5) 또는
  - nr_lookback 그리드를 [5, 6, 7] → [6] 고정 (과적합 방지)
  - cmf period를 [15, 20, 25] → [20] 고정 시도

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단 (합성 데이터만 사용 가능)
- BTC GARCH CSV (12,000 rows): PASS 0/22 — trend 지속성 부족 (BTC 합성 데이터 개선 필요)
- 합성 데이터 한계: OOS Sharpe std 3.9~8.5 (기준 1.5 대비 과대) — 실 데이터 PASS 필수

### 핵심 메트릭 (Cycle 256)
- 테스트: 8369 passed, 23 skipped (신규 2건: test_returns_18_base_features, test_momentum_quality_features_in_feature_names)
- 신규 피처: mom_quality_score (ROC5 z-score), trend_strength (consistency+acceleration)
- 신규 엔진 파라미터: atr_multiplier_tp 3.5 (기본값)
- Paper Sim: BTC 0/22, ETH 3/22 (price_action_momentum, acceleration_band, momentum_quality), **SOL 8/22 PASS**
  - SOL TOP: price_action_momentum(5.48, 4/4), momentum_quality(5.07, 3/4), frama(4.47, 3/4), htf_ema(3.95, 3/4)
- Bundle OOS: 0/5 PASS — narrow_range #1 (Score 87.1, OOS Sharpe std 5.154)
- 주요 개선: SOL 6/22 → 8/22 (atr_multiplier_tp 3.0→3.5 효과 확인됨)
