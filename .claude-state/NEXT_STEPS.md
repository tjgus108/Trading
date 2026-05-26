# Next Steps

_Last updated: 2026-05-26 (Cycle 213 C+B+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 213 완료
- 213 mod 5 = 3 → **C(데이터) + B(리스크) + F(리서치)** ✅
- 다음 Cycle 214: **214 mod 5 = 4 → D(ML) + E(실행) + F(리서치)**

### 🔥 Cycle 213 주요 성과
- **volume_breakout ATR 버그 수정**: 절대값 필터(0% 유효) → 비율 기반(97% 유효) → 0 trades 해결
- **WebSocket feed 중복 방지**: 재연결 시 동일 ts 캔들 skip 로직 추가
- **DrawdownMonitor rolling_mdd_short_pct**: 20봉 단기 MDD 추가 (조기 경보 가능)
- **시뮬 결과**: 0/22 WF + 0/5 Bundle (합성 GBM 한계, volume_breakout 복구 확인)

### 🎯 Cycle 214 권장 작업 (214 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): Walk-Forward 파이프라인 개선
- WalkForwardOptimizer에 `min_oos_trades` 파라미터 추가 (현재 하드코딩 30)
- ML 앙상블 가중치: price_action_momentum, supertrend_multi 상위 일관성 반영
- `src/backtest/walk_forward.py`: OOS 기간별 개별 sharpe 표준편차 계산 (불안정 전략 조기 식별)

#### E(실행): Paper Trading 모드 검증
- `scripts/paper_simulation.py`에 실제 포지션 추적 로그 추가
- TWAP 실행기 (`src/execution/`) 단위 테스트 확인
- Telegram 알림: config/telegram.yaml 존재 여부 확인

#### F(리서치): 전략 성과 분석
- price_cluster AvgTrades=6 → BOUNCE_THRESHOLD 추가 완화 (2% → 4%) 검토
- 합성 GBM에서 price_action_momentum 일관 1위 원인 분석: 많은 거래 수 + 단순 모멘텀 구조
- narrow_range 4h봉 신호 빈도 구조적 문제 → 신호 조건 완화 또는 timeframe 분리 검토

### ⚠️ 핵심 인사이트 (Cycle 213 시뮬)
- volume_breakout 0 trades 원인 확정: ATR 절대값 필터가 BTC(50000+) 가격에서 항상 False
  - `atr14 ≈ 500-2000` >> `_ATR_HIGH = 10.0` → 필터 통과 0%
  - 수정: `atr_pct = atr14 / close`, 범위 [0.1%, 10%]으로 변경 → 97% 유효
- price_action_momentum + momentum_quality + supertrend_multi: 3심볼 모두 상위권 일관
- price_cluster 2% 수정 후에도 6 trades로 낮음 → 추가 완화 필요

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- 합성 데이터(GBM) 결과는 방향성 참고만 가능 (PASS/FAIL 판정 불가)
- 거래소 SSL 타임아웃: 5000ms

### 📋 시뮬레이션 파라미터 현황 (Cycle 213 기준)

| 설정 | 값 | 변경 사유 |
|------|----|---------| 
| TRAIN_HOURS | 5040h (210일) | Cycle 211에서 확대 |
| TEST_HOURS | 1440h (60일) | Cycle 211에서 확대 |
| STEP_HOURS | 720h (30일) | 유지 |
| WF Windows | 4개 | Cycle 211에서 확대 |
| SSL Timeout | 5000ms | 빠른 fallback |
| price_cluster BOUNCE_THRESHOLD | 2% | Cycle 212에서 수정 |
| volume_breakout ATR 필터 | 비율 기반 0.1%~10% | **Cycle 213에서 절대값→비율 수정** |

**상태**: Cycle 213 완료 → Cycle 214 D(ML) + E(실행) + F(리서치)
**최우선 과제**: price_cluster BOUNCE_THRESHOLD 추가 완화 + ML 앙상블 가중치 최적화
