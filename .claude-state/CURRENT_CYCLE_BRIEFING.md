# Current Cycle Briefing

_Last updated: 2026-06-27 (Cycle 361 완료)_

## 현재 상태 요약

- **완료 사이클**: 361
- **카테고리**: B(리스크) + D(ML) + F(리서치)
- **1h PASS 연속 FAIL**: 44연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV 사용)

## Cycle 361 핵심 성과

### ✅ 완료
1. **B(리스크): DrawdownMonitor/CircuitBreaker/VaR-CVaR 검토**
   - DrawdownMonitor 직렬화/복원 완전 구현 확인 (Cycle357 수정 이후 정상)
   - CircuitBreaker(5회) vs DrawdownMonitor(3회) 연속 손실 기준 불일치: 의도적 설계 확인
   - VaR/CVaR: KellySizer.estimate_var_cvar(), CF-VaR, PortfolioOptimizer._compute_var_cvar() 정상
   - 실질적 코드 버그 없음 → 추가 수정 불필요

2. **D(ML): RF 피처 중요도 분석 (feature_importance_BTC_USDT.json)**
   - MDI vs PFI 불일치 발견:
     - `macd_hist`: MDI 0.084 (높음) BUT PFI -0.060 (가장 해로운 피처)
     - `bb_position`: PFI -0.038, `volatility_20`: PFI -0.034, `donchian_pct`: PFI -0.030
   - 핵심 피처(양 방법 양수): `atr_pct`(0.030), `price_vs_ema50`(0.018), `volume_ratio_20`(0.018)
   - n_test_samples=50으로 소표본 → 재학습 시 더 큰 테스트 세트 필요

3. **F(리서치): roc_ma_cross EMA200 조건 정리**
   - `"ema50" in df.columns` 중복 체크 제거 → `if len(df) >= 200:`으로 명확화
   - `rsi_val` dead code 제거 (Cycle329에서 RSI 필터 제거 후 변수 잔존)
   - bare `except: pass` → `except Exception: pass`

### 🔍 핵심 발견
- **price_cluster Sharpe 0.87로 상승** (0.72→0.87): SharpeStd=1.10 (안정성 최우수)
  - 파라미터 변화 없음 → 자연 변동 또는 특정 윈도우 시장 상황 호조
  - PF=1.20 (1.5 목표까지 +0.30) → WFO 심층 탐색 필요
- **RF PFI 음수 피처**: macd_hist(-0.060), bb_position(-0.038) → 제거 시 모델 일반화 향상 가능
- **roc_ma_cross**: EMA200 조건 정리로 코드 명확화, rank2(2/8 consistency) 유지

## 다음 우선순위 (Cycle 362 — B+D+F)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | F(리서치) | price_cluster WFO 심층 탐색 (rank1, Sharpe 0.87, vol_atr_trend_min 최적화) |
| 2 | D(ML) | RF PFI 음수 피처 제거 실험 (macd_hist, bb_position 제거 후 재학습) |
| 3 | B(리스크) | Kelly Sizer max_fraction 적정성 검토, CircuitBreaker rapid_decline 파라미터 확인 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `src/strategy/roc_ma_cross.py` | EMA200 조건 정리(ema50 체크 제거), rsi_val dead code 제거, bare except → Exception | 361 F |
| `src/backtest/walk_forward.py` | roc_ma_cross 주석 업데이트 (rank1 상태, Cycle361 F 수정 기록) | 361 F |
| `scripts/paper_simulation.py` | dema_cross rsi_dir_filter=True 추가 확정 (PF 1.26→1.45) | 360 A |
| `scripts/paper_simulation.py` | close_window=40 실험 → 악화 확인 → default(50) 복원 | 360 C |
| `src/backtest/walk_forward.py` | close_window=40 Cycle360 재확인 악화 주석 추가 | 360 C |
| `src/strategy/dema_cross.py` | `rsi_dir_filter=False` 파라미터 추가 | 359 D |
| `src/backtest/walk_forward.py` | dema_cross DEFAULT_GRIDS에 rsi_dir_filter=[False,True] 추가 | 359 D |
| `src/strategy/dema_cross.py` | 거리 필터 0.001→0.002 (SharpeStd 2.69→2.32) | 358 F |

## 환경 상태

- 테스트: 8434 passed, 23 skipped (Cycle 361 전체 실행 ✅)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
