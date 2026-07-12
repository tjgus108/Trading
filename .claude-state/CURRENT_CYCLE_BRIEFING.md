# Current Cycle Briefing

_Last updated: 2026-07-12 (Cycle 418 완료)_

## 현재 상태

- **완료된 사이클**: 418
- **다음 사이클**: 419 (419 mod 5 = 4 → D(ML) + E(실행) + F(리서치))
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **roc_ma_cross**: 4/8 Consistency = 구조적 최적점 확정 (Cycle416 F) — 추가 탐색 완전 종료
- **price_cluster**: Sh=1.06, PF=1.32, Tr=35, 2/8 → 2/8 ceiling 구조적 한계 확정 (Cycle415 F)
- **dema_cross**: Sh=0.85, PF=1.38, Tr=26, 2/8 → **2/8 ceiling 구조적 원인 확정 (Cycle418 F)** — 추가 탐색 완전 종료
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
- **Bundle OOS**: 5/5 PASS (2026-07-08 실거래소 데이터 기준, SSL 차단으로 신규 실행 불가)
- **전체 테스트 수**: 8716 총계 (8693 passed + 23 skipped) — Cycle418 +6 추가

## Cycle 418 주요 결과

### C(데이터): DataFeed 경계값 테스트 3개
1. `test_ema20_slope_near_zero_for_constant_prices`: 상수 가격 50봉 → ema20_slope ≈ 0
2. `test_vwap20_equals_close_for_constant_ohlcv`: 상수 가격·거래량 → vwap20 = close
3. `test_macd_hist_near_zero_for_constant_prices`: 상수 가격 → macd_hist ≈ 0 (|hist| < 1.0)

### B(리스크): DrawdownMonitor BLOCK 복합 케이스 3개
4. `test_block_entry_and_sharpe_decay_block_dominates`: BLOCK_ENTRY(0.0) + sharpe_decay(0.5) → get_size_multiplier=0.0
5. `test_streak_and_atr_elevated_no_mdd_no_sharpe`: streak(0.5) + ATR elevated(0.5) → get_size_multiplier=0.5
6. `test_block_entry_and_atr_elevated_block_dominates`: BLOCK_ENTRY(0.0) + ATR elevated(0.5) → get_size_multiplier=0.0

### F(리서치): dema_cross 2/8 Consistency ceiling 원인 완전 확정
- **핵심 원인**: RANGING(47.3%) → DEMA(8,20) 크로스가 방향성 없는 노이즈 신호 생성
- **PASS 2윈도우** = BTC TREND_UP 구간(2023 Q4/2024 Q1) — 볼륨 스파이크+추세 일치
- **FAIL 6윈도우** = RANGING/BEAR 구간 → false cross 빈발, PF 구조적 < 1.5
- **PF gap=0.12** (1.38→1.50): 20+ 사이클 탐색으로 달성 불가 확인됨
- **결론**: dema_cross/frama/price_cluster 모두 RANGING 47.3% BTC 1h 구조적 한계 동일. 추가 탐색 완전 종료.

## 다음 사이클 419 방향 (D+E+F)

- **D(ML)**: ML 신호 생성기 미커버 케이스 또는 feature importance/regime-aware 관련 테스트
- **E(실행)**: 주문 실행 관련 미커버 케이스 (슬리피지 계산, 체결 재시도 등)
- **F(리서치)**: roc_ma_cross 4/8 Consistency 상세 분석 또는 신규 전략 후보 탐색
  - roc_ma_cross는 유일한 PASS 전략 (Sh=1.81, PF=2.02) — 파라미터 안정성 검토
