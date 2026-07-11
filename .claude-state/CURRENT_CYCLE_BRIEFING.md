# Current Cycle Briefing

_Last updated: 2026-07-11 (Cycle 416 완료)_

## 현재 상태

- **완료된 사이클**: 416
- **다음 사이클**: 417 (417 mod 5 = 2 → B+D+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **roc_ma_cross**: 4/8 Consistency = 구조적 최적점 확정 (Cycle416 F) — 추가 탐색 완전 종료
- **price_cluster**: Sh=1.06, PF=1.32, Tr=35, 2/8 → 2/8 ceiling 구조적 한계 확정 (Cycle415 F)
- **dema_cross**: Sh=0.85, PF=1.38, Tr=26, 2/8 → 탐색 완전 종료 (Cycle377 F)
- **frama**: Sh=0.44, PF=1.11, Tr=65, 0/8 → 탐색 종료 (RANGING 47.3% weak_signal 차단)
- **narrow_range**: Sh=-0.51, PF=0.97(<1.0), Tr=46, 0/8 → 구조적 실패 확정
- **positional_scaling**: Sh=-0.38, PF=1.09, Tr=34, 1/8 → 구조적 실패 확정 (pullback==rally)
- **momentum_quality**: Sh=-1.19, PF=0.96(<1.0), Tr=71, 1/8 → 구조적 실패 확정
- **volume_breakout**: Sh=-0.74, PF=0.96(<1.0), Tr=72, 0/8 → 구조적 실패 확정
- **relative_volume**: Sh=-0.99, PF=0.92(<1.0), Tr=64, 0/8 → 구조적 실패 확정
- **price_action_momentum**: Sh=-1.08, PF=0.97(<1.0), Tr=73, 1/8 → 구조적 실패 확정
- **htf_ema**: Sh=-0.72, PF=0.91(<1.0), Tr=43, 0/8 → 구조적 실패 확정
- **acceleration_band**: Sh=-0.94, PF=0.98(<1.0), Tr=44, 1/8 → 구조적 실패 확정
- **lob_maker**: Sh=-0.04, Trades=75, MDD=17%, 0/8 → 구조적 한계 확정 (LOB 데이터 없음)
- **Bundle OOS**: 5/5 PASS (2026-07-08 실거래소 데이터 기준, SSL 차단으로 신규 실행 불가)
- **전체 테스트 수**: 8707 총계 (8684 passed + 23 skipped) — Cycle416 +7 추가

## Cycle 416 주요 결과

### B(리스크): DrawdownMonitor 복합 케이스 3개 추가
1. `test_kelly_fraction_and_sharpe_decay_compound`: kelly_fraction(0.5) + sharpe_decay(0.5) 독립 동시 활성 검증
2. `test_streak_and_sharpe_decay_no_mdd_atr`: streak(0.5, 3연속 손실) + sharpe_decay(0.5) → size_mult=0.5
3. `test_sharpe_decay_recovery_while_high_vol_daily_limit_remains`: sharpe_decay 회복 후 size_mult=1.0, HIGH_VOL 일일 한도 2% 독립 유지

### D(ML): optimize_donchian + select_features_pfi 반환 검증 4개 추가
4. `test_optimize_donchian_best_params_is_dict`: best_params가 dict; 비어있지 않으면 'channel_period' 포함
5. `test_optimize_donchian_avg_oos_sharpe_is_float`: avg_oos_sharpe float 타입
6. `test_select_features_pfi_all_from_input_columns`: 반환 피처명이 X_train.columns 서브셋
7. `test_select_features_pfi_no_duplicates`: 반환 목록 중복 없음

### F(리서치): roc_ma_cross AvgTrades=14 구조적 ceiling 확정
- **PASS 4/8 윈도우**: 2023 Q4(BTC 27k→44k) + 2024 Q1(44k→73k) — 볼륨 스파이크 동반 → vol_ratio≥1.2 빈번
- **FAIL 4/8 윈도우**: 2023 H1(저거래량 회복) + 2024 Q2(조정기) — vol_ratio at signals=0.89-0.97(<1.2)
- **AvgTrades=14 ceiling**: BTC 1h 60d × vol_ratio_min=1.2 = ~10% 통과율 (구조적)
- **결론**: 4/8 Consistency가 구조적 최적점. vol_ratio/필터 조정 모두 역효과 확인. 탐색 완전 종료.
- walk_forward.py roc_ma_cross 섹션에 Cycle416 F 분석 주석 추가

## 다음 사이클 417 방향 (B+D+F)

- **B(리스크)**: CircuitBreaker 경계값 또는 DrawdownMonitor BLOCK+sharpe_decay 복합 케이스
- **D(ML)**: optimize_price_cluster 또는 optimize_frama 추가 경계값
- **F(리서치)**: frama 0/8 Consistency 원인 분석 (WFO 그리드 파라미터 선택 분석)
