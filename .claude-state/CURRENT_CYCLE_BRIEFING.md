# Current Cycle Briefing

_Last updated: 2026-07-03 (Cycle 387 완료)_

## 현재 상태

- **완료된 사이클**: 387
- **다음 사이클**: 388 (388 mod 5 = 3 → A+B+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross 유지 — Sh=1.81, PF=2.02, Consist=4/8)
- **Bundle OOS**: N/A (합성 데이터 — 거래소 연결 불가)

## Cycle 387 주요 결과

### C(데이터): price_cluster bounce_pct=0.006 실험
- 전체 BTC 1h 데이터 비교 (bounce_pct=0.006/0.007/0.008/0.010):
  - bounce_pct=0.006: Sh=0.77, PF=1.17, Tr=311, MDD=28.7% [FAIL]
  - bounce_pct=0.008: Sh=0.53, PF=1.11, Tr=342, MDD=25.7% [FAIL]
  - bounce_pct=0.010: Sh=0.28, PF=1.06, Tr=368, MDD=30.5% [FAIL]
- **핵심 결론**: bounce_pct 하향 방향 맞음(Sh↑) 그러나 PF<1.5, MDD>20% 동시 해결 불가. bounce_pct 탐색 종료.

### E(실행): connector.py is_halted 테스트 추가
- `tests/test_connector.py`: 4개 테스트 추가 (26→30개)
  - is_halted False(4회 실패), True(5회 실패), create_order halted 거부, success 시 _consecutive_failures=0 리셋
- 전체 30 테스트 PASS

### F(리서치): roc_ma_cross SL/TP 실험
- BacktestEngine atr_multiplier_sl/tp 6가지 조합 실험:
  - baseline sl=1.5 tp=3.5: Sh=-0.17, PF=0.99, Tr=309, MDD=23.1% [FAIL] sl_hits=182
  - sl=1.2 tp=3.5: Sh=0.28 (최고), MDD=22.2% [FAIL]
  - sl=2.0 tp=4.0: MDD=19.8% (유일 <20%) 그러나 Sh=-0.27 [FAIL]
- **핵심 결론**: SL/TP 조정으로 roc_ma_cross PASS 불가. 전체 데이터셋 Sh<0은 regime-dependent 한계. SL/TP 방향 종료.

## 시뮬레이션 결과

| 시뮬 | 결과 |
|------|------|
| paper_sim (1h BTC baseline) | **1/19 PASS** (roc_ma_cross Sh=1.81, PF=2.02, Trades=14, 4/8) — 재실행 타임아웃, 이전 결과 유지 |
| bundle_oos (4h BTC) | N/A — 거래소 API 연결 불가 (합성 데이터 결과 무의미) |

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `tests/test_connector.py` | is_halted + consecutive_failures 리셋 4개 테스트 추가 (E) |

## Cycle 388 예고 (388 mod 5 = 3 → A(품질) + B(리스크) + F(리서치))

- **A(품질)**: BacktestEngine 또는 paper_trader 미커버 기능 테스트 추가
  - min_hold_bars, consec_loss_scale_threshold 등 Cycle298/331 기능 검토
- **B(리스크)**: KellySizer 또는 CircuitBreaker 단위 테스트 추가
  - MIN_TRADES_FOR_KELLY=15, Bayesian shrinkage 경계값
- **F(리서치)**: price_cluster vol_regime_filter=True 실험
  - bounce_pct=0.006/0.008 × vol_regime_filter=False/True 비교
  - 고변동성 레짐 차단 → PF↑, MDD↓ 기대
