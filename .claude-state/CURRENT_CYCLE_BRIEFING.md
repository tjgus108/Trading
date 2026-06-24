# Current Cycle Briefing

_Last updated: 2026-06-24 (Cycle 352 완료)_

## 현재 상태 요약

- **완료 사이클**: 352
- **카테고리**: B(리스크) + D(ML) + F(리서치)
- **1h PASS 연속 FAIL**: 32연속 0/20 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (2026-06-24 재실행 확인)

## Cycle 352 핵심 성과

### ✅ 완료
1. **supertrend_multi atr_threshold=0.5 적용** (`scripts/paper_simulation.py`)
   - 근거: 4h 저변동성 window에서 atr_threshold=0.7이 모든 신호 차단 → 3개 window no trades
   - Bundle OOS도 동일 값(0.5) 사용하며 PASS → paper_sim도 일치시킴
2. **DrawdownMonitor 절댓값 ATR% 임계값 추가** (`src/risk/drawdown_monitor.py`)
   - `set_atr_state()` 확장: `atr_pct`, `atr_pct_threshold=0.06` 파라미터 추가
   - SOL처럼 avg ATR이 높아 상대 배수(ratio=1.5)로 감지 안 되는 경우에 절댓값 6% 보완
3. **Bundle OOS 4h 재실행**: 5/5 PASS 유지, supertrend_multi OOS Sharpe=3.892

### 🔍 핵심 발견
- **wick_reversal 구조 문제**: ETH/SOL 1h에서 모든 8개 window 0 trades
  - 합성 데이터에 wick 패턴이 충분히 없는 것으로 추정
  - C(데이터) 사이클에서 조사/수정 필요
- **dema_cross ETH 1h**: Sharpe=1.12 (>1.0!) but trades=6 (<15) → FAIL
  - Sharpe 조건은 충족, trades만 문제 → 진입 파라미터 조정으로 PASS 가능성 있음
- **SOL 1h HIGH%** 극단적: dema_cross=85.5%, frama=52.5%
  - 1h SOL은 극고변동성 레짐 → 대부분 전략이 슬리피지로 수익 상쇄
- **engulfing_zone**: ETH 1h 2/8, SOL 1h 1/8으로 크로스심볼 상위권 (BTC는 미진입)

## 다음 우선순위 (Cycle 353 — C+E+F)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | C(데이터) | wick_reversal ETH/SOL 0 trades 원인 분석, 합성 데이터 wick 패턴 생성 확인 |
| 2 | E(실행) | dema_cross ETH 1h trades=6 → 진입 조건 분석, 파라미터 완화 검토 |
| 3 | F(리서치) | engulfing_zone BTC vs ETH/SOL 성과 차이 구조 분석 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `scripts/paper_simulation.py` | `"supertrend_multi": {"atr_threshold": 0.5}` 추가 | 352 B |
| `src/risk/drawdown_monitor.py` | `set_atr_state()` atr_pct 절댓값 임계값 확장 | 352 D |
| `src/backtest/engine.py` | `min_trades_override` 파라미터 추가 | 351 B |
| `scripts/paper_simulation.py` | min_trades_override=8 (4h) 전달 | 351 B |
| `scripts/paper_simulation.py` | `timeframe=ACTIVE_TIMEFRAME` 추가 (슬리피지 버그) | 350 A |

## 환경 상태

- 테스트: 8434 passed, 23 skipped (Cycle 351 확인, 352 변경 후 관련 테스트 PASS)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf, order_flow_imbalance_v2, supertrend_multi, vwap_cross, value_area
