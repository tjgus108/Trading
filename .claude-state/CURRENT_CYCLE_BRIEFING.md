# Current Cycle Briefing

_Last updated: 2026-07-10 (Cycle 410 완료)_

## 현재 상태

- **완료된 사이클**: 410
- **다음 사이클**: 411 (411 mod 5 = 1 → B+D+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **relative_volume**: Sh=-0.99, PF=0.92(<1.0), Tr=64, 0/8 → 구조적 실패 확정 (RANGING 볼륨 노이즈, 탐색 금지)
- **price_action_momentum**: Sh=-1.08, PF=0.97(<1.0), Tr=73, 1/8 → 구조적 실패 확정 (모멘텀 vs RANGING 부조화, 탐색 금지)
- **htf_ema**: Sh=-0.72, PF=0.91(<1.0), Tr=43, 0/8 → 구조적 실패 확정 (iloc[::4] HTF proxy 불정확, 탐색 금지)
- **acceleration_band**: Sh=-0.94, PF=0.98(<1.0), Tr=44, 1/8 → 구조적 실패 확정 (음의 엣지, 탐색 금지)
- **narrow_range**: Sh=-0.51, PF=0.97, Tr=46, 0/8 → 구조적 한계 확정, 탐색 보류
- **lob_maker**: Sh=-0.04, Trades=75, MDD=17%, 0/8 → 구조적 한계 확정 (LOB 데이터 없음), 탐색 보류
- **Bundle OOS**: 5/5 PASS (2026-07-08, 실 BTC CSV 4h 재샘플링) — SSL fallback으로 갱신 불가, 보존
- **전체 테스트 수**: 8661 총계 (8638 passed + 23 skipped) — Cycle410 +6 추가

## Cycle 410 주요 결과

### A(품질): apply_wfe 미커버 브랜치 테스트 (3개 추가)
1. `test_apply_wfe_mild_negative_is_positive_oos_gives_one`: IS=-0.5 (소폭 음수), OOS=1.0 → wfe=1.0
2. `test_apply_wfe_both_nonpositive_gives_zero`: IS=-2.0, OOS=-0.5 → wfe=0.0
3. `test_apply_wfe_zero_is_positive_oos_gives_one`: IS=0.0, OOS=1.2 → wfe=1.0

### C(데이터): DataFeed 지표 경계값 테스트 (3개 추가)
1. ema20_slope 상승 추세 양수 검증
2. donchian_high shift(1) 현재 봉 제외 검증
3. vwap20 균일 가격/거래량 NaN/Inf 없음 + typical price 수렴 검증

### F(리서치): relative_volume BTC 1h 구조적 한계 확정
- Sh=-0.99, PF=0.92(<1.0), Trades=64, 0/8 — 음의 엣지 확정
- 근본 원인: rvol>1.2가 RANGING 47.3%에서 단기 노이즈로 빈번히 충족 + RSI<68 과다 허용
- walk_forward.py DEFAULT_GRIDS["relative_volume"]={} 추가

## 다음 사이클: 411 (B+D+F)

- B(리스크): DrawdownMonitor 또는 CircuitBreaker 미커버 케이스 추가
- D(ML): select_features_pfi 또는 ML 파이프라인 미커버 케이스 추가
- F(리서치): volume_breakout (rank 6, BTC 1h Sh=-0.74, Trades=72, MDD>20%) 구조 분석
