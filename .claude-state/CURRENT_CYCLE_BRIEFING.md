# Current Cycle Briefing

_Last updated: 2026-06-26 (Cycle 358 완료)_

## 현재 상태 요약

- **완료 사이클**: 358
- **카테고리**: C(데이터) + B(리스크) + F(리서치)
- **1h PASS 연속 FAIL**: 38연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV 사용)

## Cycle 358 핵심 성과

### ✅ 완료
1. **roc_ma_cross 파라미터 실험** (`scripts/paper_simulation.py`) → **실패, 기본값 복원**
   - roc_period=10/ma_period=5 실험: BTC Sharpe 0.34→-1.93 (역효과 확정)
   - ETH: Sharpe=-2.83 (rank 15/19)
   - 결론: 단축 ROC + 강화 스무딩 조합은 신호 품질 저하 → 기본값(12/3) 복원

2. **DrawdownMonitor ATR/Sharpe 직렬화 round-trip 테스트 6개 추가** (`tests/test_drawdown_monitor.py`)
   - Cycle 357 B에서 추가한 5개 필드 end-to-end 검증 완료
   - ATR elevated/normal, Sharpe decayed/normal, get_size_multiplier 복원 모두 PASS

3. **price_cluster vol_regime_filter 완전 제거** (`src/backtest/walk_forward.py`, `scripts/paper_simulation.py`)
   - DEFAULT_GRIDS: vol_regime_filter/vol_atr_trend_min 제거, bounce_pct/n_bins/close_window만 탐색
   - paper_sim: `{}` 기본값 복원
   - 근거: 4사이클(354-357) filter=True/False 모두 Sharpe=0.87 → 필터 무효 확정

### 🔍 핵심 발견
- **roc_ma_cross 파라미터 민감도**: roc_period 12→10 변경만으로 Sharpe 0.34→-1.93 급락
  - 기본값(roc_period=12, ma_period=3)이 현재 BTC 1h에서 최적임을 간접 확인
  - 향후 파라미터 탐색 시 DEFAULT_GRIDS WFO(Bundle OOS)를 통한 검증 권장
- **price_cluster**: vol_regime_filter 완전 제거 후 첫 Bundle OOS에서 최적 params 재평가 예정

## 다음 우선순위 (Cycle 359 — D+E+F)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | D(ML) | dema_cross RSI=65 SharpeStd 추이 확인 (2/8→유지 여부) |
| 2 | E(실행) | order_flow_imbalance_v2 1h paper_sim 순위 분석 |
| 3 | F(리서치) | roc_ma_cross 기본값(12/3) 성능 베이스라인 재확인 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `tests/test_drawdown_monitor.py` | ATR/Sharpe round-trip 테스트 6개 추가 | 358 B |
| `src/backtest/walk_forward.py` | price_cluster vol_regime_filter/vol_atr_trend_min 제거 | 358 F |
| `scripts/paper_simulation.py` | price_cluster `{}` 복원, roc_ma_cross 기본값 복원 | 358 F/C |
| `src/risk/drawdown_monitor.py` | to_dict/from_dict 5개 필드 추가 | 357 B |
| `src/strategy/dema_cross.py` | BUY RSI 70→65 강화 | 357 D |

## 환경 상태

- 테스트: 8440 passed, 23 skipped (Cycle 358 전체 실행)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
