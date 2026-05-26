# Next Steps

_Last updated: 2026-05-26 (Cycle 212 B+D+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 212 완료
- 212 mod 5 = 2 → **B(리스크) + D(ML) + F(리서치)** ✅
- 다음 Cycle 213: **213 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치)**

### 🔥 Cycle 212 주요 성과
- **WalkForwardOptimizer UNSTABLE 강화**: low_trades_folds > n_windows/2 이면 UNSTABLE 판정
- **KellySizer VaR/CVaR**: estimate_var_cvar() 소표본 경고 메서드 추가 (n < 30 → WARNING)
- **price_cluster 0 trades 수정**: BOUNCE_THRESHOLD 0.5% → 2% (4배 완화)
- **시뮬 결과**: 0/22 WF + 0/5 Bundle (합성 GBM 한계 재확인)

### 🎯 Cycle 213 권장 작업 (213 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): DataFeed 안정성 검증
- WebSocket feed mock 테스트: 재연결 시 중복 데이터 처리 확인
- DataFeed 캐시 전략: 심볼별 최근 N봉 캐싱 효율성 점검
- **volume_breakout 0 trades 추가 분석**: GBM에서 ema20 > ema50 uptrend 조건 출현 빈도 계산
  - 조건 완화 검토: uptrend 조건 제거 또는 단기 EMA 기준으로 변경

#### B(리스크): CircuitBreaker 임계값 검토
- `CircuitBreaker.atr_surge_multiplier`: 현재 2.0 → 합성 데이터에서 실제 트리거 빈도 확인
- `DrawdownMonitor.rolling_mdd()`: 단기(50봉) vs 장기 MDD 차이 시각화 추가
- VaR/CVaR: estimate_var_cvar() 연동 테스트 (KellySizer 통합 검증)

#### F(리서치): 실데이터 없이 전략 품질 측정 대안 지표 탐구
- volume_breakout uptrend 조건의 GBM 출현율 분석 (Python 스크립트)
- price_cluster threshold=2% 수정 효과 → Cycle 213 시뮬에서 검증
- Top 전략(price_action_momentum, cmf) 합성 GBM 일관성 원인 분석
  - 단순한 신호 구조 + 충분한 거래 수 → GBM에서도 noise로 수익?

### ⚠️ 핵심 인사이트 (Cycle 212 시뮬)
- price_action_momentum, cmf: TOP 일관성 (GBM에서도 Sharpe 6~7)
  - 많은 거래 수(115-169)로 Sharpe 분모 안정화 효과
- volume_breakout 0 trades: ema20>ema50 uptrend가 GBM 랜덤워크에서 거의 없음
  - 해결책: uptrend 조건을 단기 추세(예: price > ema20 기준)로 단순화
- price_cluster: 2% threshold 수정 후 다음 시뮬 검증 예정
- Bundle OOS 4h: narrow_range 저거래 fold 44% > 40% → 4h봉 신호 빈도 구조적 문제

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- 합성 데이터(GBM) 결과는 방향성 참고만 가능 (PASS/FAIL 판정 불가)
- 거래소 SSL 타임아웃: 5000ms

### 📋 시뮬레이션 파라미터 현황 (Cycle 212 기준)

| 설정 | 값 | 변경 사유 |
|------|----|---------| 
| TRAIN_HOURS | 5040h (210일) | Cycle 211에서 확대 (IS 충분 확보) |
| TEST_HOURS | 1440h (60일) | Cycle 211에서 확대 (fold당 trades ↑) |
| STEP_HOURS | 720h (30일) | 유지 (겹침 허용) |
| WF Windows | 4개 | Cycle 211에서 확대 (통계 신뢰도 향상) |
| SSL Timeout | 5000ms | 빠른 fallback |
| price_cluster BOUNCE_THRESHOLD | 2% | Cycle 212에서 0.5%→2% 완화 |

**상태**: Cycle 212 완료 → Cycle 213 C(데이터) + B(리스크) + F(리서치)
**최우선 과제**: volume_breakout uptrend 조건 완화 + price_cluster 2% 효과 검증
