# Next Steps

_Last updated: 2026-05-29 (Cycle 233 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 233

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 233 | E+A+SIM+F | PaperTrader get_execution_summary, HealthChecker get_uptime_pct, 테스트 30개 추가, Flash Crash/Kelly-VIX 리서치 |

### 🎯 Cycle 234 작업 방향 (234 mod 5 = 4 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): 피처 상관성 분석 + 데이터 파이프라인
- OFI vs bid_ask_depth_imbalance vs vpin_50 Pearson/Spearman 상관계수 계산
  - 상관 > 0.85인 피처 쌍 제거 여부 결정
- WebSocket stale_timeout 기본값 검증 (None → 300.0 복원 여부)
- exchange_netflow / sopr 온체인 피처 파이프라인 검증

#### B(리스크): Kelly-VIX Hybrid 통합
- KellySizer에 volatility scaling 레이어 추가: `fraction × (target_vol / realized_vol_20d)`
  - 리서치 근거: arXiv:2508.16598 Kelly-VIX Hybrid 논문
- DrawdownMonitor + KellySizer 통합: HIGH_VOL 시 dual dampening
- IS/OOS Sharpe 비율로 Kelly fraction 오버피팅 보정 검토

#### SIM: walk_forward fold 레짐 구성 분석
- 각 fold의 레짐 구성(TREND/RANGE/CRISIS 비율) 기록
- 레짐별 분리 OOS 성과 리포팅
- momentum_quality, price_action_momentum 재시뮬레이션

#### F(리서치): 파라미터 섭동 + 피처 중복 제거
- BacktestEngine 파라미터 섭동 테스트(±15%) 설계
  - Sharpe 하락 > 40% 시 overfitting FAIL 판정
- 레짐별 SHAP 피처 중요도 분리 추적 방안 조사
- VPIN circuit breaker 임계값 리서치

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭
- 상위 3: momentum_quality(Sharpe 6.71 BTC), price_action_momentum(Sharpe 5.16 SOL), supertrend_multi(Sharpe 4.84 ETH)
- 테스트: 8,150+ passed (Cycle 233 +30개)
- 신규 인프라: get_execution_summary(), get_uptime_pct(), Sharpe IC 엣지 커버리지
