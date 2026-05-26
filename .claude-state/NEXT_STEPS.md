# Next Steps

_Last updated: 2026-05-26 (Cycle 213 C+B+SIM+F & E+A+SIM+F 병합 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 213 완료
- 213 mod 5 = 3 → **C+B+SIM+F** ✅ & **E+A+SIM+F** ✅ (병렬 세션)
- 다음 Cycle 214: **214 mod 5 = 4 → D(ML) + E(실행) + F(리서치)**

### 🔥 Cycle 213 주요 성과 (두 세션 합산)
- **volume_breakout ATR 버그 수정**: 절대값 필터(0% 유효) → 비율 기반(97% 유효) → 0 trades 해결
- **volume_breakout v3**: EMA 추세 필터 → confidence 이동 (5→4 조건)
- **price_cluster v3**: threshold 계산 수정 (cluster_width 비율 → 가격 기준 1%)
- **WebSocket feed 중복 방지**: 재연결 시 동일 ts 캔들 skip 로직 추가
- **DrawdownMonitor rolling_mdd_short_pct**: 20봉 단기 MDD 추가 (조기 경보 가능)
- **PerformanceTracker 주간/월간**: get_weekly_summary(), get_monthly_summary() 추가
- **PaperTrader 상태 저장/복원**: save_state()/load_state() + graceful shutdown 시 자동 저장
- **SIM Rank Score**: 6지표 가중합산 composite metric + percentile + sharpe_std
- **리서치**: Block Bootstrap/CPCV 합성데이터 극복방안 도출

### 🎯 Cycle 214 권장 작업 (214 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): Walk-Forward 파이프라인 개선
- WalkForwardOptimizer에 `min_oos_trades` 파라미터 추가 (현재 하드코딩 30)
- ML 앙상블 가중치: price_action_momentum, supertrend_multi 상위 일관성 반영
- `src/backtest/walk_forward.py`: OOS 기간별 개별 sharpe 표준편차 계산 (불안정 전략 조기 식별)

#### E(실행): Paper Trading 모드 검증
- `scripts/paper_simulation.py`에 실제 포지션 추적 로그 추가
- TWAP 실행기 (`src/execution/`) 단위 테스트 확인
- Telegram 알림: config/telegram.yaml 존재 여부 확인

#### F(리서치): Block Bootstrap + 전략 성과 분석
- **최우선**: GBM 대신 Block Bootstrap 구현 (리서치 결과 기반)
- CPCV(Combinatorially Purged Cross-Validation) 도입 가능성 조사
- price_cluster AvgTrades=6 → BOUNCE_THRESHOLD 추가 완화 (2% → 4%) 검토
- narrow_range 4h봉 신호 빈도 구조적 문제 → 신호 조건 완화 또는 timeframe 분리 검토

### ⚠️ 핵심 인사이트 (Cycle 213 양쪽 세션 합산)
- volume_breakout 0 trades 원인 확정: ATR 절대값 필터가 BTC(50000+) 가격에서 항상 False
  - 수정: `atr_pct = atr14 / close`, 범위 [0.1%, 10%]으로 변경 → 97% 유효
  - 추가로 EMA 추세 필터를 신호 조건에서 제외 → confidence로 이동 (5→4 조건)
- price_cluster: BTC에서 threshold 0.9 USD → 300 USD로 현실화 (가격 기준 1%)
- 리서치: Freqtrade/Hummingbot 성공 핵심은 "검증 품질" (전략 수 아님)
- 합성데이터: Block Bootstrap이 GBM 대비 자기상관+ARCH 효과 보존
- SIM: Rank Score로 0/22 PASS 상황에서도 전략 간 상대 우위 정량화 가능

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
| price_cluster _BOUNCE_PCT | 가격 기준 1% | Cycle 213에서 수정 (cluster_width 비율→가격 기준) |
| volume_breakout ATR 필터 | 비율 기반 0.1%~10% | **Cycle 213에서 절대값→비율 수정** |

**상태**: Cycle 213 완료 → Cycle 214 D(ML) + E(실행) + F(리서치)
**최우선 과제**: Block Bootstrap 합성데이터 생성기 구현 + ML 앙상블 가중치 최적화
