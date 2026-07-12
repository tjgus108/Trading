# Current Cycle Briefing

_Last updated: 2026-07-12 (Cycle 419 완료)_

## 현재 상태

- **완료된 사이클**: 419
- **다음 사이클**: 420 (420 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **roc_ma_cross**: 4/8 Consistency = 구조적 최적점 확정 (Cycle416 F) — 추가 탐색 완전 종료
- **price_cluster**: Sh=1.06, PF=1.32, Tr=35, 2/8 → 2/8 ceiling 구조적 한계 확정 (Cycle415 F)
- **dema_cross**: Sh=0.85, PF=1.38, Tr=26, 2/8 → 2/8 ceiling 구조적 원인 확정 (Cycle418 F) — 추가 탐색 완전 종료
- **frama**: Sh=0.44, PF=1.11, Tr=65, 0/8 → 추가 탐색 완전 종료 (Cycle417 F) — PF 구조적 ceiling
- **narrow_range**: Sh=-0.51, PF=0.97(<1.0), Tr=46, 0/8 → 구조적 실패 확정
- **positional_scaling**: Sh=-0.38, PF=1.09, Tr=34, 1/8 → 구조적 실패 확정 (pullback==rally)
- **momentum_quality**: Sh=-1.19, PF=0.96(<1.0), Tr=71, 1/8 → 구조적 실패 확정
- **volume_breakout**: Sh=-0.74, PF=0.96(<1.0), Tr=72, 0/8 → 구조적 실패 확정
- **relative_volume**: Sh=-0.99, PF=0.92(<1.0), Tr=64, 0/8 → 구조적 실패 확정
- **price_action_momentum**: Sh=-1.08, PF=0.97(<1.0), Tr=73, 1/8 → 구조적 실패 확정
- **htf_ema**: Sh=-0.72, PF=0.91(<1.0), Tr=43, 0/8 → 구조적 실패 확정
- **acceleration_band**: Sh=-0.94, PF=0.98(<1.0), Tr=44, 1/8 → 구조적 실패 확정
- **lob_maker**: Sh=-0.04, Trades=75, MDD=17%, 0/8 → 구조적 한계 확정 (LOB 데이터 없음)
- **Bundle OOS**: 5/5 PASS (2026-07-08 기준, supertrend_multi avg trades=7.6 저거래 확인됨)
- **전체 테스트 수**: 8722 총계 (8699 passed + 23 skipped) — Cycle419 +6 추가

## Cycle 419 주요 결과

### D(ML): optimize_supertrend_multi + avg_oos_trades 테스트 3개
1. `test_optimize_supertrend_multi_returns_wf_result`: 기본 호출 → WalkForwardResult 반환, strategy_name='supertrend_multi'
2. `test_optimize_supertrend_multi_avg_oos_trades_none_or_float`: avg_oos_trades 필드(Cycle417 D 추가) None or float 검증
3. `test_optimize_supertrend_multi_single_window_no_crash`: n_windows=1에서도 크래시 없이 반환

### E(실행): PaperConnector 엣지케이스 3개
4. `test_buy_exceeds_balance_raises_value_error`: 잔고(100 USDT) 초과 매수(10@1000=10000 USDT) → ValueError
5. `test_sell_without_position_raises_value_error`: 포지션 없이 SELL 시도 → ValueError (no position)
6. `test_create_order_without_price_raises_value_error`: price=None → PaperConnector에서 직접 ValueError

### F(리서치): roc_ma_cross 4/8 vs price_cluster/dema_cross 2/8 비교 분析
- **핵심 발견**: vol_ratio≥1.2 = 묵시적 레짐 필터 (Implicit Regime Gate)
  - roc_ma_cross 4/8 PASS: BTC 급등기(2023 Q4: 27k→44k, 2024 Q1: 44k→73k) vol_ratio≥1.2 충족 → Trades≥15
  - RANGING 구간: vol_ratio=0.89-0.97 → 신호 차단 → Trades=10-12 → FAIL
- **price_cluster/dema_cross 2/8 FAIL 구조**:
  - 레짐 필터 없음 → TREND_UP 시 noise trades → PF<1.5 구조적
  - dema_cross rsi_dir_filter는 볼륨 무관 약한 필터 → RANGING false cross 완전 제거 불가
- **결론**: volume filter가 없는 전략의 구조적 ceiling = RANGING 47.3%에서 signal noise 제거 불가
- walk_forward.py roc_ma_cross 섹션 Cycle419 F 비교 分析 주석 추가 완료

## 다음 사이클 420 방향 (A+C+F)

- **A(품질)**: BacktestEngine 또는 apply_wfe 미커버 케이스
- **C(데이터)**: DataFeed 지표 경계값 추가 (ema50, volume_sma20, return_1 등)
- **F(리서치)**: supertrend_multi avg_oos_trades=7.6 저거래 원인 分析 (Bundle OOS fold 2,3 trades=3)
  - trend_confirm_bars=2-3이 4h에서 과다 차단하는지 검토
