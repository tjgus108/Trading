# Current Cycle Briefing

_Last updated: 2026-07-04 (Cycle 392 완료)_

## 현재 상태

- **완료된 사이클**: 392
- **다음 사이클**: 393 (393 mod 5 = 3 → C+B+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross 유지 — Sh=1.81, PF=2.02, Consist=4/8)
- **Bundle OOS**: 5/5 PASS (cmf, order_flow_imbalance_v2, supertrend_multi, vwap_cross, value_area)
- **전체 테스트 수**: 8509개 (+7)

## Cycle 392 주요 결과

### B(리스크): CircuitBreaker recovery_window + DrawdownMonitor HIGH_VOL/reset_weekly 테스트 3개

- `tests/test_circuit_breaker.py`: rapid_decline_oldest_price_exits_window 추가
  - window=3, cooldown_periods=0: [100,95,95] → triggered, 4번째 97 추가 → no trigger
  - peak 가격이 슬라이딩 윈도우 밖으로 나가면 decline 감지 자동 해제 검증
- `tests/test_drawdown_monitor.py`: reset_weekly_does_not_clear_warning 추가
  - WARNING → reset_weekly() → WARNING 유지 (reset_daily()만 해제)
- `tests/test_drawdown_monitor.py`: set_regime_high_vol_tightens_daily_limit 추가
  - HIGH_VOL 레짐 → 일일 DD 한도 3%→2% 강화 → 2% 손실에 WARNING 트리거

### D(ML): price_cluster close_window=60 실험 → DEAD PARAM 확정

- `paper_simulation.py` close_window 50→60 실험:
  - **결과**: Sh=0.55(↓-0.40!), PF=1.22(↓-0.11), Tr=30(↓-4), Consistency=1/8(↓1) → 대폭 악화
  - 원인: 긴 window → 오래된 가격 클러스터에 포함 → bounce 타이밍 지연 → 수익성 하락
- **close_window 탐색 완전 종료**: 40(Cycle360 대폭 악화), 50(최적), 60(역효과) 모두 검증
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
