# Next Steps

_Last updated: 2026-06-01 (Cycle 258 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 251, 252, 253, 254, 255, 256, 257, 258

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 251 | B+D+F | wick_reversal ATR 필터, Deflated Sharpe Ratio 유틸리티 |
| 252 | E+A+F | validate_ohlcv() 헬퍼, DSR→BundleOOS 통합 |
| 253 | C+B+F | load_csv_ohlcv/resample_ohlcv, 전환쿠션, RollingOOS max_oos_sharpe_std 파라미터화 |
| 254 | D+E+F | nr_range_ratio/nr_atr_ratio 피처, --csv-dir 옵션, **MC 버그 수정** |
| 255 | A+C+F | GARCH CSV 생성, 0-trade score 버그 수정, SOL 6/22 PASS 확인 |
| 256 | B+D+F | atr_multiplier_tp 3.0→3.5, mom_quality_score/trend_strength 피처 추가, **SOL 8/22 PASS** |
| 257 | B+D+F | HIGH conf 1.5→1.2, REGIME bull/ranging 피처 추가, OOS std 저거래 제외, **ETH 5/22 PASS** |
| 258 | C+B+F | ETH/SOL GARCH CSV 생성, HIGH conf 1.2→1.35, Bundle OOS std 로직 확인 |

### 🎯 Cycle 259 작업 방향 (259 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): GARCH CSV 품질 개선 — 평균회귀 컴포넌트 추가
- Cycle 258 문제: ETH(1200→63000), SOL(15→1765) 극단 드리프트
  - 원인: GARCH drift 누적 (bull_drift=0.00055/0.00080 × 12000봉 = 누적 효과)
  - 결과: ETH 0/22, SOL 0/22 (Cycle 257: ETH 5/22, SOL 4/22에서 하락)
- 수정 방향: `scripts/generate_garch_csv.py` 개선
  - **Ornstein-Uhlenbeck 평균회귀**: `ret = θ*(μ - log(price)) * dt + sigma * dW`
  - 또는 더 간단히: 가격이 시작가의 N배를 초과하면 drift를 0 또는 반전
  - 목표: ETH 가격 범위 1000~5000 (실제 2023 범위), SOL 10~250
- ETH/SOL GARCH CSV 재생성 후 재시뮬 → 이전 결과(ETH 5/22, SOL 4/22) 회복 목표

#### E(실행): roc_ma_cross SOL 분석
- Cycle 258: roc_ma_cross SOL Sharpe 1.35, PF 1.43, 1/8 PASS (borderline)
  - 문제: PF 1.43 < 1.5 기준 미달 (차이 작음)
  - Trades 34 (충분), MDD 6.9% (양호)
- roc_ma_cross 파라미터 확인: `src/strategy/roc_ma_cross.py`
  - TP/SL 비율 조정으로 PF 개선 가능성 검토
  - 단, CLAUDE.md 규정: 합성 데이터 PASS만으로 파라미터 수정 금지

#### F(리서치): 평균회귀 합성 데이터 효과 측정
- 개선된 GARCH CSV(OU 포함)로 재시뮬 후 ETH/SOL PASS 수 비교
  - 목표: Cycle 257 수준(ETH 5/22, SOL 4/22) 이상 회복

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단 (합성 데이터만 사용 가능)
- BTC GARCH CSV (12,000 rows): PASS 0/22 — trend 지속성 부족 (BTC 합성 데이터 개선 필요)
- ETH/SOL: 새 GARCH CSV 8 windows — 극단 드리프트 문제로 결과 신뢰도 낮음

### 핵심 메트릭 (Cycle 258)
- 테스트: 8369 passed, 23 skipped (변경 없음)
- Paper Sim BTC: 0/22 (top: supertrend_multi +5.87%, price_cluster +2.50%)
- Paper Sim ETH: **0/22** ↓ (Cycle 257: 5/22 — GARCH 드리프트 원인)
  - TOP: dema_cross(Sharpe 1.87 but 14 trades), acceleration_band(1.85 but 12 trades)
- Paper Sim SOL: **0/22** ↓ (Cycle 257: 4/22 — GARCH 드리프트 원인)
  - TOP: roc_ma_cross(Sharpe 1.35, PF 1.43, 1/8), acceleration_band(1.85, PF 2.43, 8 trades)
- Bundle OOS BTC 4h: 0/5 PASS (narrow_range Score 87.1, OOS Sharpe 0.240↑)

### 주요 코드 변경 이력 (Cycle 258)
1. `scripts/generate_garch_csv.py` — 신규 생성 (ETH/SOL GARCH 합성 CSV 생성기)
2. `src/backtest/engine.py:204` — HIGH conf_mult 1.2→1.35
3. `src/risk/manager.py:405` — CONFIDENCE_MULTIPLIER HIGH 1.2→1.35
4. `tests/test_risk_manager.py:871,901` — HIGH multiplier 테스트 업데이트 (1.2→1.35)
