# Current Cycle Briefing

_Last updated: 2026-07-08 (Cycle 406 완료)_

## 현재 상태

- **완료된 사이클**: 406
- **다음 사이클**: 407 (407 mod 5 = 2 → B+D+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **narrow_range**: Sh=-0.51, PF=0.97, Tr=46, 0/8 → 구조적 한계 확정 (1h BTC 노이즈), 탐색 보류
- **lob_maker**: Sh=-0.04, Trades=75, MDD=17%, 0/8 → 구조적 한계 확정 (LOB 데이터 없음), 탐색 보류
- **Bundle OOS**: 5/5 PASS (2026-07-08, 실 BTC CSV 4h 재샘플링) — SSL fallback으로 갱신 불가, 보존
- **전체 테스트 수**: 8634 총계 (8611 passed + 23 skipped) — Cycle406 +6 추가

## Cycle 406 주요 결과

### B(리스크): DrawdownMonitor CRISIS/복합 케이스 테스트 (3개 추가)

- `tests/test_drawdown_monitor.py`:
  - `test_crisis_regime_tightens_daily_limit`: CRISIS 레짐 → _high_vol_daily_limit(2%) 적용 확인
  - `test_high_vol_regime_and_transition_cushion_compound`: HIGH_VOL + transition_cushion 동시 활성 복합 케이스
  - `test_regime_reset_reverts_daily_limit`: HIGH_VOL → TREND_UP 전환 시 일일 한도 원복 확인

### D(ML): select_features_pfi() 경계 케이스 (3개 추가)

- `tests/test_ml_pipeline_edge_cases.py` (TestSelectFeaturesPfi):
  - `test_select_features_pfi_top_k_zero_enforces_minimum`: top_k=0 → 최소 2개 반환
  - `test_select_features_pfi_exactly_100_samples_normal_path`: n=100 경계 → n_repeats=5 정상 경로
  - `test_select_features_pfi_top_k_equals_feature_count`: top_k=n_features=5 → 전체 5개 반환

### F(리서치): narrow_range 1h BTC 구조적 한계 분석 완료

- **BTC 1h**: Sh=-0.51, PF=0.97(<1.0!), Trades=46, MDD=10.1%, 0/8 Consistency
- 근본 원인: 1h BTC 고빈도 노이즈 → NR breakout 지속성 부재, PF<1.0 = 파라미터 조정으로 해결 불가
- EMA slope filter: trades 46→20-25로 감소 → Trades<15 위험, PF 개선폭 불확실
- 결론: NR전략은 4h/daily 타임프레임 적합 → 1h 탐색 완전 보류
- `src/backtest/walk_forward.py`: DEFAULT_GRIDS["narrow_range"] 구조적 한계 주석 추가

## 다음 사이클 (407): B+D+F

- **B(리스크)**: CircuitBreaker 복합 테스트 (max_daily_drawdown + atr_surge 복합, rapid_decline + consecutive_losses)
- **D(ML)**: optimize_frama() / optimize_narrow_range() 엣지케이스 (test_phase_d.py)
- **F(리서치)**: acceleration_band 또는 dema_cross 4h 타임프레임 재분석
