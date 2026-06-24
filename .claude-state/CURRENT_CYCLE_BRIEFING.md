# Current Cycle Briefing

_Last updated: 2026-06-24 (Cycle 353 완료)_

## 현재 상태 요약

- **완료 사이클**: 353
- **카테고리**: C(데이터) + E(실행) + F(리서치)
- **1h PASS 연속 FAIL**: 33연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (재실행 없음, Cycle 352 결과 보존)

## Cycle 353 핵심 성과

### ✅ 완료
1. **wick_reversal 1h 제외** (`scripts/paper_simulation.py`)
   - `STRATEGIES_TIMEFRAME_EXCLUDE["1h"]`에 `"wick_reversal"` 추가
   - 근거: ETH/SOL 1h 모든 8개 window 0 trades, BTC 1h Sharpe=-2.64 (return=-9.31%)
   - 효과: BTC avg return -3.18%→-2.73% 개선 (wick_reversal 드래그 제거)
2. **dema_cross fast=8/slow=20 실험 및 분석**
   - 실험 결과: ETH Sharpe 1.12→0.00 (악화), BTC/SOL 소폭 개선
   - 판단: ETH Sharpe 저하 + 여전히 15 trades 미달 → 파라미터 조정으로 해결 불가
   - 롤백 완료 (기본값 fast=10/slow=25 유지)
3. **engulfing_zone 크로스심볼 성과 차이 분석**
   - BTC real: 0/8, return=-6.31% (구조적 실패)
   - ETH synthetic: 2/8, return=+3.50% (SharpeStd 높음)
   - SOL synthetic: 1/8, return=+4.81% (PF 1.33 < 1.5)
   - 결론: ETH/SOL 성과는 합성 데이터 아티팩트 가능성 (GARCH mean-reversion 특성)

### 🔍 핵심 발견
- **wick_reversal 완전 실패 확인**: 1h에서 구조적으로 작동 불가 (제외 처리)
- **dema_cross 파라미터 한계**: 빠른 주기로도 15 trades 달성 불가 (BTC 5, ETH 8, SOL 13)
  - 대안 접근 필요: 크로스 이외의 신호 조건 추가 (거리/경사도 기반)
- **engulfing_zone BTC 실패 원인**: 효율적 시장(real)에서 패턴 즉각 흡수
  - ETH/SOL 성과는 합성 데이터 GARCH mean-reversion 아티팩트로 추정
- **price_cluster BTC 3사이클 연속 rank=1**: Sharpe=0.87, PF=1.20 → PASS에 가장 근접
  - 다음 사이클 D(ML)에서 집중 개선 시도 대상

## 다음 우선순위 (Cycle 354 — D+E+F)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | D(ML) | price_cluster BTC 1h Sharpe 0.87→1.0, PF 1.20→1.5 개선 시도 |
| 2 | E(실행) | dema_cross 대안: 크로스 거리/경사도 기반 신호로 trade 빈도 증가 |
| 3 | F(리서치) | price_cluster BTC vs ETH/SOL 성과 차이 구조 분석 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `scripts/paper_simulation.py` | `STRATEGIES_TIMEFRAME_EXCLUDE["1h"]`에 `"wick_reversal"` 추가 | 353 C |
| `scripts/paper_simulation.py` | `"supertrend_multi": {"atr_threshold": 0.5}` 추가 | 352 B |
| `src/risk/drawdown_monitor.py` | `set_atr_state()` atr_pct 절댓값 임계값 확장 | 352 D |
| `src/backtest/engine.py` | `min_trades_override` 파라미터 추가 | 351 B |
| `scripts/paper_simulation.py` | min_trades_override=8 (4h) 전달 | 351 B |

## 환경 상태

- 테스트: 8434 passed, 23 skipped (Cycle 353 실행 확인)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf, order_flow_imbalance_v2, supertrend_multi, vwap_cross, value_area
