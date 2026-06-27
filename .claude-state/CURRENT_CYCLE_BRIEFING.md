# Current Cycle Briefing

_Last updated: 2026-06-27 (Cycle 359 완료)_

## 현재 상태 요약

- **완료 사이클**: 359
- **카테고리**: D(ML) + E(실행) + F(리서치)
- **1h PASS 연속 FAIL**: 42연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV 사용)

## Cycle 359 핵심 성과

### ✅ 완료
1. **dema_cross ATR 최소 변동성 필터 코드 추가** (`src/strategy/dema_cross.py`)
   - `atr_vol_min_pct=0.0` 파라미터 추가 (기본값 비활성)
   - paper_sim에서 0.005(0.5%) 실험 → BTC ATR ~1.49%로 임계값 미작동 (dead param)
   - 코드는 유지 (다른 심볼/타임프레임 실험용)

2. **dema_cross RSI 방향성 필터 코드 추가** (`src/strategy/dema_cross.py`)
   - `rsi_dir_filter=False` 파라미터 추가 (기본값 비활성)
   - BUY시 RSI>50, SELL시 RSI<50 요구 → 모멘텀 방향 확인 필터
   - Cycle360에서 paper_sim 실험 예정

3. **walk_forward DEFAULT_GRIDS 업데이트** (`src/backtest/walk_forward.py`)
   - `DEFAULT_GRIDS["dema_cross"]`에 `rsi_dir_filter=[False,True]` 추가

4. **PaperConnector use_tiered_slippage 노출** (`src/exchange/paper_connector.py`)
   - `use_tiered_slippage=False` 파라미터 추가 → PaperTrader로 전달
   - BTC/ETH=0.05%, SOL=0.2% 차등 슬리피지 옵션 활성화 가능

5. **price_cluster n_bins=6 실험 → 악화 확인 → 복원** (`scripts/paper_simulation.py`)
   - n_bins=6 결과: BTC Sharpe -0.84 (0.72→-0.84, 대폭 악화)
   - 결론: n_bins=5(기본값) 최적 확정. 다음 탐색: close_window 조정

### 🔍 핵심 발견
- **price_cluster n_bins**: 6은 과도한 분할, 노이즈 증가 확인 → 5가 최적
- **dema_cross ATR 필터**: BTC 1h에서 dead param (ATR 항상 임계값 초과)
- **dema_cross RSI 방향성 필터**: 코드 완성, Cycle360에서 paper_sim 실험 예정
- **PaperTrader 티어드 슬리피지**: 기능은 있었으나 PaperConnector에 미노출 → 수정

## 다음 우선순위 (Cycle 360 — A+C+F)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | A(품질) | dema_cross rsi_dir_filter=True paper_sim 실험 (Sharpe/PF 향상 확인) |
| 2 | C(데이터) | price_cluster close_window 탐색 (20 또는 40, 현재 기본값 30) |
| 3 | F(리서치) | dema_cross WFO 그리드 분석 (18 조합 탐색) |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `src/strategy/dema_cross.py` | `atr_vol_min_pct=0.0` 파라미터 추가 (BTC dead param 확인) | 359 D |
| `src/strategy/dema_cross.py` | `rsi_dir_filter=False` 파라미터 추가 (Cycle360 실험 예정) | 359 D |
| `src/backtest/walk_forward.py` | dema_cross DEFAULT_GRIDS에 rsi_dir_filter=[False,True] 추가 | 359 D |
| `src/exchange/paper_connector.py` | use_tiered_slippage=False 파라미터 노출 | 359 E |
| `scripts/paper_simulation.py` | n_bins=6 실험 → 악화 확인 → n_bins=5 복원 | 359 F |
| `src/strategy/dema_cross.py` | 거리 필터 0.001→0.002 (SharpeStd 2.69→2.32) | 358 F |
| `src/risk/drawdown_monitor.py` | cooldown_active 주석 보완 | 358 B |
| `scripts/paper_simulation.py` | price_cluster bounce_pct=0.020 실험→악화→복원 | 358 C |
| `src/backtest/walk_forward.py` | price_cluster bounce_pct=0.020 악화 기록 주석 | 358 C |
| `src/risk/drawdown_monitor.py` | to_dict()/from_dict() 5개 필드 + transition_cushion 추가 | 357 B |
| `src/strategy/dema_cross.py` | RSI 임계값 70→65 (효과없음 확인) | 357 D |
| `scripts/paper_simulation.py` | price_cluster vol_regime_filter=False | 357 F |
| `src/backtest/walk_forward.py` | price_cluster DEFAULT_GRIDS vol_regime_filter=[False,True] | 357 F |

## 환경 상태

- 테스트: 8434 passed, 23 skipped (Cycle 359 전체 실행 ✅)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
