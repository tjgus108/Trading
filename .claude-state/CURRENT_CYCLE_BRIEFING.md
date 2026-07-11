# Current Cycle Briefing

_Last updated: 2026-07-11 (Cycle 414 완료)_

## 현재 상태

- **완료된 사이클**: 414
- **다음 사이클**: 415 (415 mod 5 = 0 → A+C+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **narrow_range**: Sh=-0.51, PF=0.97, Tr=46, 0/8 → **탐색 완전 종료** (DEFAULT_GRIDS={}, Cycle414 F 확정)
- **Bundle OOS**: 5/5 PASS (2026-07-08, 실 BTC CSV 4h) — SSL fallback 보존
- **전체 테스트 수**: 8668 passed + 23 skipped (Cycle414 +6 추가)

## Cycle 414 주요 결과

### D(ML): WalkForwardTrainer.select_features_pfi 경계값 테스트 (3개 추가)
1. `test_pfi_one_feature_no_crash`: 피처 1개 → k=max(2,1)=2 → ranked[:2]는 1개만 반환 (크래시 없음)
2. `test_pfi_two_features_returns_both`: 피처 2개 → k=2 → 정확히 2개 반환
3. `test_pfi_small_sample_no_crash`: n_samples=50 < 100 → n_repeats=10 경로, 크래시 없음

### E(실행): PaperConnector 경계값 테스트 (3개 추가)
4. `test_partial_sell_leaves_remaining_position`: buy 1.0 → sell 0.5 → open_positions == 0.5
5. `test_fetch_balance_used_reflects_open_position`: buy 후 fetch_balance()['used'] > 0
6. `test_fetch_balance_total_equals_free_plus_used`: total == free + used 항등식

### F(리서치): narrow_range BTC 1h 구조적 한계 최종 확정
- Sh=-0.51, PF=0.97 (<1.0 = 음의 엣지), Trades=46, MDD=10.1%, 0/8 Consistency
- **전방 수익 분석 (12,000 BTC 1h 캔들)**:
  - BUY 1h fwd_ret = +0.032% → 슬리피지 0.1% (0.05%/leg × 2) 미만 → 비용 > 엣지
  - SELL 8h fwd_ret = -0.074% → BTC 상승 바이어스로 SELL 구조적 불리
- `ema_slope` 필터 적용 시: trades=46→~20-25 → Trades<15 위험, PF 개선 불가
- NR전략은 4h/daily 타임프레임에 적합 (1h 고빈도 노이즈 환경 부적합)
- **DEFAULT_GRIDS["narrow_range"] = {} 설정** (탐색 완전 종료, 추가 실험 금지)

## 다음 사이클 415 방향 (A+C+F)

- **A(백테스트)**: BacktestEngine 미커버 경계값 3개 (A=415 mod 5=0)
- **C(데이터)**: DataFeed rsi14/donchian 경계값 3개
- **F(리서치)**: frama rank 2 전략 분석 (paper_sim에서 rank 2 전략 OOS 구조 점검)
