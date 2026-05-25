# Next Steps

_Last updated: 2026-05-25 (Cycle 211 A+C+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 211 완료
- 211 mod 5 = 1 → **A(품질) + C(데이터) + F(리서치)** ✅
- 다음 Cycle 212: **212 mod 5 = 2 → B(리스크) + D(ML) + F(리서치)**

### 🔥 Cycle 211 주요 성과
- **OOS trades 신뢰도 경고**: WalkForwardOptimizer에 low_trades_folds 추가 (< 30 trades = WARNING)
- **WalkForwardResult.low_trades_folds**: 투명성 개선, summary()에 표시
- **Walk-Forward 윈도우 확대**: 3→4 윈도우 (TRAIN=210일, TEST=60일, STEP=30일)
- **타임아웃 단축**: 거래소 SSL 5초 (20초→5초), 빠른 합성 fallback
- **중간 결과 저장**: 심볼별 완료 즉시 REPORT 저장 (타임아웃 내성)

### 🎯 Cycle 212 권장 작업 (212 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): Risk 모듈 검증 강화
- DrawdownMonitor의 graceful degradation 검증 (기존 streak recovery 확인)
- KellySizer의 극단값 처리 (fraction > 1.0 clamping 확인)
- CircuitBreaker 임계값 현실화: 현재 임계값이 합성 데이터 기준인지 검토
- **VaR/CVaR** 계산에서 낮은 trades 샘플 편향 경고 추가 고려

#### D(ML): OOS trades 30+ 필터 적용 검토
- WalkForwardOptimizer: low_trades_folds > n_windows/2 이면 UNSTABLE 판정 추가
- 단순 전략(donchian_breakout, ema_cross) OOS trades 검증: fold당 30 확보 가능?
- ML 피처 중요도 분석: 현재 시그널에서 가장 유효한 피처 TOP 5 확인

#### F(리서치): 합성 vs 실데이터 성능 차이 분석
- cmf, price_action_momentum이 합성 GBM에서도 일관된 이유 분석
- volume_breakout, price_cluster의 0 trades 원인 코드 검토
- 실데이터 없이 전략 품질 측정 가능한 대안 지표 리서치

### ⚠️ 핵심 인사이트 (Cycle 211 시뮬)
- cmf, price_action_momentum: 3 심볼 모두 TOP 3 (합성 데이터에서도 일관성 있음)
- volume_breakout, price_cluster → 0 거래 (신호 조건 과도 엄격 → Cycle 212 검토)
- 4 윈도우 테스트: 각 윈도우에서 Sharpe≥1.0 + PF≥1.5 + Trades≥15 + MDD≤20% 동시 충족 어려움
- 실데이터 없이는 0/22 PASS가 의미 없음 (GBM 한계 재확인)

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- 합성 데이터(GBM) 결과는 방향성 참고만 가능 (PASS/FAIL 판정 불가)
- 거래소 SSL 타임아웃: 5000ms (이전 20000ms에서 단축)

### 📋 시뮬레이션 파라미터 현황 (Cycle 211 기준)

| 설정 | 값 | 변경 사유 |
|------|----|---------| 
| TRAIN_HOURS | 5040h (210일) | 이전 2880h(120일) → IS 충분 확보 |
| TEST_HOURS | 1440h (60일) | 이전 720h(30일) → fold당 trades ↑ |
| STEP_HOURS | 720h (30일) | 유지 (겹침 허용) |
| WF Windows | 4개 | 이전 3개 → 통계 신뢰도 향상 |
| SSL Timeout | 5000ms | 이전 20000ms → 빠른 fallback |

**상태**: Cycle 211 완료 → Cycle 212 B(리스크) + D(ML) + F(리서치)
**최우선 과제**: volume_breakout/price_cluster 0 trades 버그 조사 + OOS trades 필터 로직 추가
