# Current Cycle Briefing

_Last updated: 2026-07-06 (Cycle 400 완료)_

## 현재 상태

- **완료된 사이클**: 400
- **다음 사이클**: 401 (401 mod 5 = 1 → B+D+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **frama**: Sh=0.44, Trades=65, 0/8 Consistency — 구조적 한계 확인 (파라미터 해결 불가)
- **price_cluster**: Sh=1.06, Consist=2/8 → 최적화 완전 종료
- **dema_cross**: Sh=0.85, PF=1.38 → 탐색 완전 종료
- **Bundle OOS**: 5/5 PASS (2026-07-04, SSL 차단으로 신규 실데이터 불가)
- **전체 테스트 수**: 8568개 (+12)

## Cycle 400 주요 결과

### A(품질): BacktestEngine 방향 전환 + optimize_frama 엣지케이스 (6개 추가)

- `tests/test_backtest_engine.py`:
  - `AlternatingStrategy` 헬퍼 클래스 (BUY/SELL 교번)
  - `test_position_flip_buy_sell_generates_multiple_trades`: 방향 전환 시 2회+ 거래 생성
  - `test_engine_reuse_identical_results`: 엔진 재사용 시 상태 초기화 보장
  - `test_engine_two_strategies_result_names`: 전략별 이름 올바르게 기록
- `tests/test_phase_d.py`:
  - `TestOptimizeFrama.test_optimize_frama_returns_wf_result`: 기본 호출 검증
  - `TestOptimizeFrama.test_optimize_frama_single_window_no_crash`: n_windows=1 크래시 없음
  - `TestOptimizeFrama.test_optimize_frama_result_fields_present`: 핵심 필드 존재

### C(데이터): DataFeed duplicate timestamp + 동일 심볼 캐시 (6개 추가)

- `tests/test_feed_boundary.py`:
  - `TestToDataframeDuplicateTimestamps`: 중복 타임스탬프 제거 3개 (2개/3개중복/부분중복)
  - `TestSameSymbolMultipleRequests`: 동일 심볼 캐시 3개 (히트/limit다름/심볼다름)

### F(리서치): frama 설정 분석

- Cycle400 paper_sim: frama Sh=0.44, Trades=65, 0/8 Consistency — Cycle399 값과 동일
- `weak_rsi_buy_max=50, weak_rsi_sell_min=50` 현재 설정 유지 확정
- **결론**: frama 0/8 Consistency는 구조적 한계. 추가 파라미터 탐색으로 해결 불가.
- WFO 그리드 [40,50,60] 계속 유지 — 자동 탐색 중

## 다음 사이클 (401): B+D+F

- **B(리스크)**: DrawdownMonitor 또는 KellySizer 미커버 케이스
- **D(ML)**: WFO frama [40,50,60] fold별 선택 분포 분석 또는 MLSignalGenerator 기능
- **F(리서치)**: frama 0/8 Consistency 근본 원인 코드 분석 → 탐색 종료 결정
