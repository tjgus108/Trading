# Current Cycle Briefing

_Last updated: 2026-07-04 (Cycle 393 완료)_

## 현재 상태

- **완료된 사이클**: 393
- **다음 사이클**: 394 (394 mod 5 = 4 → D+E+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross 유지 — Sh=1.81, PF=2.02, Consist=4/8)
- **Bundle OOS**: 5/5 PASS (cmf, order_flow_imbalance_v2, supertrend_multi, vwap_cross, value_area)
- **전체 테스트 수**: 8514개 (+5)

## Cycle 393 주요 결과

### B(리스크): DrawdownMonitor should_kill_strategy 레짐 + trailing_stop_signal 회복 테스트 3개

- `tests/test_drawdown_monitor.py`: test_regime_ranging_tightens_kill_threshold 추가
  - RANGING(cap=1.2): 0.13>0.10×1.2=0.12 → Kill 발동 (기본 cap없음에서는 0.13<0.15 미발동)
- `tests/test_drawdown_monitor.py`: test_regime_high_vol_kills_at_backtest_mdd 추가
  - HIGH_VOL(cap=1.0): 0.11>0.10×1.0=0.10 → Kill, 0.09<0.10 → 미발동
- `tests/test_drawdown_monitor.py`: test_trailing_stop_signal_recovery_resets 추가
  - 하락 후 51개 상승봉 완전 회복 → signal False 검증

### C(데이터): feed.py _add_indicators() NaN 경계값 테스트 2개

- `tests/test_feed_boundary.py`: TestAddIndicatorsNanBoundary 클래스 추가
  - test_zero_volume_no_inf_in_vwap: volume=0 → vwap/vwap20에 inf 없음 검증
  - test_constant_close_rsi_no_crash: close 불변 → rsi14 inf 없음, 크래시 없음

### F(리서치): confirmation_bars=2 실험 → DEAD PARAM, 탐색 완전 종료

- **실험 결과**: Sh=-0.36(↓↓-1.31!), PF=1.00, Tr=29, Consistency=0/8 — 완전 붕괴
- bars=0(0.95) → bars=1(0.50) → bars=2(-0.36): 단조 악화 패턴 확인
- **confirmation_bars 탐색 완전 종료**: WFO grid [0]으로 축소, 추가 실험 금지
  - close_window=50 확정 불변, 추가 실험 금지
- close_window=50 복원 (변경 금지)
- `walk_forward.py` DEFAULT_GRIDS: dead param 주석 + 탐색 완전 종료 명시

### F(리서치): price_cluster 남은 개선 방향 재평가

- 모든 주요 파라미터 방향 소진:
  - bounce_pct(완료), vol_atr_trend_min(완료), close_window(완료), n_bins(완료)
  - dead: rsi_oversold_filter, min_cluster_strength_ratio, high_conf_only, confirmation_bars=1
- 마지막 미검증: `atr_bounce_factor` 또는 `confirmation_bars=2`
- 현재 최적 유지: `{"vol_regime_filter": True, "bounce_pct": 0.006, "vol_atr_trend_min": 1.2}` → Sh=0.95, PF=1.33

## 다음 사이클 (393) 핵심 과제

1. **C(데이터)**: `src/data/feed.py` compute_indicators() NaN 경계값 또는 DataFeed 캐시 엣지케이스 테스트
2. **B(리스크)**: `should_kill_strategy()` 레짐별 multiplier 또는 `trailing_stop_signal()` 가속도 경계값 테스트
3. **F(리서치)**: price_cluster 마지막 방향 — `atr_bounce_factor` 또는 `confirmation_bars=2` 탐색 결정

## ⚠️ 중요 메모

- **price_cluster 파라미터**: `{"vol_regime_filter": True, "bounce_pct": 0.006, "vol_atr_trend_min": 1.2}` (변경 금지)
- **close_window 탐색 완전 종료** (Cycle392 D 확정): 추가 close_window 실험 금지
- **vol_atr_trend_min 탐색 완전 종료** (Cycle391 D 확정): 추가 vol_atr_trend_min 실험 금지
- **bounce_pct 탐색 완전 종료** (Cycle390 C 확정): 추가 bounce_pct 실험 금지
- **roc_ma_cross**: PASS 상태 유지 (Sh=1.81, Consist=4/8) — 파라미터 변경 금지
