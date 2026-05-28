# Next Steps

_Last updated: 2026-05-29 (Cycle 235 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 233, 235 (이 세션) + 234 (parallel session)

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 233 | E+A+SIM+F | PaperTrader get_execution_summary, HealthChecker get_uptime_pct, 테스트 30개 |
| 234 | D+E+SIM+F | bid_ask_depth_imbalance 제거, regime fold weighting, TWAP volume-weights |
| 235 | A+C+SIM+F | MC permutation 버그 수정(block sign), --block-size CLI, WebSocket MAX_BACKOFF |

### 🎯 Cycle 236 작업 방향 (236 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): Kelly-VIX Hybrid + 파라미터 섭동 테스트
- KellySizer에 volatility scaling 레이어 추가: `fraction × (target_vol / realized_vol_20d)`
  - 리서치 근거: arXiv:2508.16598 Kelly-VIX Hybrid
- BacktestEngine `perturbation_check()` 구현:
  - 각 파라미터 ±10%, ±20% 섭동 → Sharpe 변화 측정
  - ±10%에서 Sharpe < 1.0이면 FRAGILE 판정
  - mean Sharpe across all perturbations ≥ 80% of baseline → ROBUST
- DrawdownMonitor + KellySizer dual dampening (HIGH_VOL)

#### D(ML): 레짐별 SHAP 피처 중요도 분리
- features.py 피처 중요도를 레짐 레이블별 분리 추적
  - TREND에서 모멘텀 피처 우세 vs HIGH_VOL에서 VPIN/OFI 우세 확인
- block_size 12-24 최적화: ACF 기반 자동 블록 길이 선택 검토
- rolling 30d live Sharpe monitor: PerformanceTracker에 추가

#### SIM: MC 버그 수정 후 재시뮬레이션
- block sign randomization 적용 후 mc_p_value 변화 측정
- --block-size 12 / 24 / 36 비교 시뮬
- momentum_quality, price_action_momentum PASS 가능성 재평가

#### F(리서치): rolling Sharpe 모니터 + regime death 감지
- rolling 30d live Sharpe < 0.5 × backtest Sharpe → regime death trigger
- 실전 봇 모니터링 best practices 조사
- GAN 기반 합성 데이터 생성 가능성 조사 (GBM 대체)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭
- 상위 3: momentum_quality(Sharpe 7.67), price_action_momentum(Sharpe 6.98), supertrend_multi(Sharpe 6.57)
- 테스트: 8,180+ passed (Cycle 235 +33개)
- 핵심 수정: MC permutation block sign randomization 버그 수정 → 재시뮬로 PASS 가능성 확인 필요
