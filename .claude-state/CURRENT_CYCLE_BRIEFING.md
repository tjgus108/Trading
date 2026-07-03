# Current Cycle Briefing

_Last updated: 2026-07-03 (Cycle 386 완료)_

## 현재 상태

- **완료된 사이클**: 386
- **다음 사이클**: 387 (387 mod 5 = 2 → C+E+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross 유지 — Sh=1.81, PF=2.02, Consist=4/8)
- **Bundle OOS**: N/A (합성 데이터 — 거래소 연결 불가)

## Cycle 386 주요 결과

### B(리스크): DrawdownMonitor 단위 테스트 추가
- `tests/test_drawdown_monitor.py`: 16개 테스트 추가 (94→110개)
  - `TestAtrVolFilter` (8개): set_atr_state 완전 커버리지
    - normal/elevated ATR, 경계값(>=threshold), zero atr_ma 방어, atr_pct 절댓값 경로, get_size_multiplier 연동, DrawdownStatus 필드
  - `TestSharpDecayFilter` (8개): set_sharpe_decay 완전 커버리지
    - normal/decay, historical_sharpe=0/음수 방어, 경계값(< not <=), size_multiplier 연동, 직렬화

### D(ML): price_cluster n_bins=4 WFO 비교 분석
- WFO(n_windows=8, is_ratio=0.778) 실행 결과: bounce_pct={0.008,0.01} × n_bins={4,5,6}
  - **8/8 FAIL** — OOS trades=4-11 (Trades<15 구조적 제약)
  - IS 선택 빈도: n_bins=4(3/8), n_bins=5(3/8), n_bins=6(2/8) — 통계적 유의차 없음
  - WFO compact window(333봉 OOS ≈ 14일)로는 n_bins 구별 불가
  - **핵심 결론**: n_bins 방향 탐색 종료. bounce_pct 하향이 trade frequency 개선 유일 경로

### F(리서치): roc_ma_cross WFO IS-선택 패턴 분석
- WFO IS 선택 분포: volume_filter=False 5/8, vol_ratio_min=1.2 3/8
- vol_ratio_min=1.2 선택 시 IS Sharpe 더 높음(3.11, 1.55 vs 0.00)
- **핵심 결론**: vol_ratio_min=1.2 파라미터 edge 실제 존재 재확인. WFO compact 분석 결과로 변경 불가
- 다음 F 방향: SL/TP 실험 (BacktestEngine atr_multiplier_sl/tp — Trades 무영향)

## 시뮬레이션 결과

| 시뮬 | 결과 |
|------|------|
| paper_sim (1h BTC baseline) | **1/19 PASS** (roc_ma_cross Sh=1.81, PF=2.02, Trades=14, 4/8) |
| bundle_oos (4h BTC) | N/A — 거래소 API 연결 불가 (합성 데이터 결과 무의미) |

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `tests/test_drawdown_monitor.py` | set_atr_state + set_sharpe_decay 16개 테스트 추가 (B) |

## Cycle 387 예고 (387 mod 5 = 2 → C(데이터) + E(실행) + F(리서치))

- **C(데이터)**: price_cluster trade frequency 개선 탐색
  - bounce_pct=0.006 실험 (0.008보다 낮음 → trades↑ 기대)
  - 주의: bounce_pct 하향은 신호 품질 저하 가능 (noise↑)
- **E(실행)**: 실행 관련 코드 품질 점검 (슬리피지, 타임아웃 등)
- **F(리서치)**: roc_ma_cross SL/TP 실험
  - BacktestEngine atr_multiplier_sl=1.2 전역 실험 또는 전략별 TP 실험
  - Trades에 영향 없음 → Sharpe/PF 개선 가능성 (MDD 감소 경로)
  - 주의: Cycle375에서 dema_cross SL=1.2 역효과 확인 (전역 변경 한계)
