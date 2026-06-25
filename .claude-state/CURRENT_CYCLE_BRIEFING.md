# Current Cycle Briefing

_Last updated: 2026-06-25 (Cycle 354 완료)_

## 현재 상태 요약

- **완료 사이클**: 354
- **카테고리**: D(ML) + E(실행) + F(리서치)
- **1h PASS 연속 FAIL**: 34연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지

## Cycle 354 핵심 성과

### 실험 결과 (모두 롤백)

1. **D(ML) — price_cluster vol_regime_filter=True 실험**
   - 이론: sideways 전용 전략이므로 추세장(ATR/ATR_MA > 1.5) 신호 억제 → Sharpe 개선
   - 결과: Sharpe=0.87, trades=41 **동일** (효과 없음)
   - 원인: BTC 1h 데이터에서 ATR(14)/ATR_MA(20) > 1.5 구간 거의 없음 → 필터 비발동
   - 롤백 완료 (PAPER_SIM_STRATEGY_PARAMS에 price_cluster 없음)

2. **E(실행) — dema_cross narrowing 조건 추가**
   - 이론: DEMA gap 30%+ 수렴 시 예비 신호 → trade 빈도 증가 (BTC 5→15+ 목표)
   - 결과: **BTC 65 trades, Sharpe=-3.50, return=-14.68%** (심각 악화)
   - 원인: **로직 역방향 오류**
     - fast>slow AND narrowing → BUY 신호 (구현) → 하향크로스 임박 → SELL이 맞음
     - fast<slow AND narrowing → SELL 신호 (구현) → 상향크로스 임박 → BUY가 맞음
   - 롤백 완료 (dema_cross.py 원래 상태 복원)

3. **F(리서치) — price_cluster BTC vs ETH/SOL 구조 분석**
   - BTC real (+4.99%): 실제 시장의 가격 메모리(지지/저항 레벨)를 클러스터가 포착
   - ETH synthetic (-0.31%) / SOL synthetic (-8.27%): GARCH 과정은 변동성 클러스터링만, 가격 수준 의존성 없음
   - 결론: **price_cluster는 real market data 전용** — synthetic 결과로 최적화 금지

### 핵심 발견 (교훈)

- **narrowing 방향 오류 확인**: fast>slow AND narrowing은 하향크로스 임박 (SELL 방향)
  - 올바른 narrowing: "역추세 예비 신호" 또는 "확산 기반 추세 강화 신호"로 재설계 필요
- **vol_regime_filter 한계**: BTC 1h는 ATR 변동폭이 작아 상대 ATR 비율이 임계값 초과 안 함
  - 다음 시도: n_bins=4 또는 bounce_pct=0.008 조정 (Cycle 355 A에서)
- **34연속 1h FAIL**: 단기 조정으로는 PASS 어렵 — 근본 구조 변경 필요

## 다음 우선순위 (Cycle 355 — A+C+F)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | A(품질) | price_cluster n_bins=4 또는 bounce_pct 조정 실험 |
| 2 | C(데이터) | roc_ma_cross 파라미터 분석 (Consistency 2/8 → 4/8 목표) |
| 3 | F(리서치) | dema_cross narrowing 올바른 방향 재설계 |

## 코드 변경 현황 (현재 활성)

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `scripts/paper_simulation.py` | `STRATEGIES_TIMEFRAME_EXCLUDE["1h"]`에 `"wick_reversal"` 추가 | 353 C |
| `scripts/paper_simulation.py` | `"supertrend_multi": {"atr_threshold": 0.5}` 추가 | 352 B |
| `src/risk/drawdown_monitor.py` | `set_atr_state()` atr_pct 절댓값 임계값 확장 | 352 D |
| `src/backtest/engine.py` | `min_trades_override` 파라미터 추가 | 351 B |
| `scripts/paper_simulation.py` | min_trades_override=8 (4h) 전달 | 351 B |

## 환경 상태

- 테스트: 8434 passed, 23 skipped
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf, order_flow_imbalance_v2, supertrend_multi, vwap_cross, value_area
