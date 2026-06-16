# Next Steps

_Last updated: 2026-06-16 (Cycle 316 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 316

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 314 | D+E+F | vol_spike_mult=0.5 실험→역효과(복원), --strategies 필터 추가(E실행), cmf 4h BTC PASS 확인(첫번째!) |
| 315 | A+C+F | atr_threshold=1.05 실험→역효과(avg=-2.118, std=3.889, 복원), cmf 4h BTC-특이성 확인(ETH/SOL FAIL) |
| 316 | B+D+F | narrow_range→price_cluster 교체(FAIL:저거래), cmf_confirm=False 확정(avg=3.892↑,std=1.239↓), 4h slippage 보정(engine.py) |

### 🎯 Cycle 317 작업 방향 (317 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): price_cluster 4h close_window 단축 실험

- **Cycle 316 B 결론**: price_cluster FAIL — 근본 원인은 close_window=60이 4h에서 신호 생성 억제
  - close_window=60: 신호율 3.9% (230봉 중 9개)
  - close_window=30: 신호율 10.0% (260봉 중 26개) — 2.5배 증가
  - vol_atr_trend_min 변경은 효과 없음 (1.2/1.5 동일한 신호율)
- **B 작업**: `close_window=60` → `close_window=30` 단독 실험
  1. `run_bundle_oos.py` BUNDLE_STRATEGY_INIT_PARAMS["price_cluster"]["close_window"] = 30
  2. Bundle OOS 4h 실행: `python3 scripts/run_bundle_oos.py --symbol BTC/USDT --timeframe 4h --csv-dir data/historical`
  3. 결과 분석: 각 fold 거래 수 변화, OOS Sharpe 변화
  - **목표**: fold 저거래 비율 80% → 40% 미만으로 감소
  - **만약 여전히 저거래 FAIL**: `min_oos_trades=7` override 추가 고려 (단독 실험 원칙 유지)

#### D(ML): elder_impulse fold1 IS 과최적화 분석

- **Cycle 316 D 결론**: supertrend_multi cmf_confirm=False로 완성 (avg=3.892, std=1.239)
  - 다음 supertrend 이슈: fold4 레짐 전환 제외 (IS=2.323, WFE=-0.662) — 포스트-ATH 구간
  - fold4 근본 원인: ATH 이후 BTC 급격한 조정 → 모든 BUY 전략에 불리
- **D 작업**: elder_impulse IS 과최적화 분석
  - elder_impulse fold1 (IS=5.372, OOS=0.568, WFE=0.106): IS 과최적화 의심
  - fold2 (IS=5.883, OOS=-5.389, WFE=-0.916): 심각한 OOS 역전
  - 실험: `sharpe_decay_max` 완화 (현재 기본값 → 0.5 이하 fold 제거)
  - OR: elder_impulse 번들에서 제거 후 다른 전략 대체 (rank 최하위 7.4 p0)
  - **권고**: elder_impulse는 IS 과최적화가 심각 — 번들 교체 검토 (5번째 전략 후보 탐색)

#### F(리서치): 4h Adaptive Slippage 보정 효과 검증

- **Cycle 316 F 결론**: engine.py `_get_slippage()` 타임프레임 스케일 보정 완료
  - 4h BTC: HIGH 98.8% → 9.3%, NORMAL 0% → 90.7% (avg slippage 0.149% → 0.059%)
- **F 작업**:
  1. Paper sim 4h cmf 단독 재실행으로 슬리피지 보정 효과 확인
     - `python3 scripts/paper_simulation.py --timeframe 4h --csv-dir data/historical --strategies cmf`
     - 이전 (Cycle 315): HIGH slippage 99.4%, avg Sharpe=0.74
     - 예상: HIGH 감소, Sharpe 개선 여부 확인
  2. Bundle OOS 결과에서 실질 slippage 배분 로깅 확인
  3. 실전 투입 시 슬리피지 가정 문서화 (4h BTC: 0.05% avg = 현실적)

### ⚠️ 주의 사항 (Cycle 317)
- **cmf_confirm**: `False` (변경 금지) — Cycle 316 D 확정
- **close_window 실험**: 60→30 단독 변경, 다른 price_cluster 파라미터는 유지
  - 현재: `{"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}`
  - 실험: `close_window=30` (나머지 동일)
- **단독 실험 원칙**: close_window=30 + min_oos_trades 동시 변경 금지
- **4h slippage 보정**: engine.py `_get_slippage()` sqrt(tf) 스케일 (변경 금지)

### 핵심 메트릭 (Cycle 316)
- 테스트: **8413 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, TRAIN=210일, --csv-dir data/historical): **0/22 PASS** (Cycle 315 동일)
  - rank1: price_cluster (score=75.7, Sharpe=0.59, trades=46)
  - rank2: supertrend_multi (score=68.3, Sharpe=0.32, trades=48)
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **2/5 PASS** (유지)
  - cmf: 5/5 PASS (avg=2.508, std=1.888)
  - supertrend_multi (cmf_confirm=False): 4/4 valid PASS (avg=**3.892**, std=**1.239**) ← 개선!
  - price_cluster: FAIL (저거래 80% folds)
- **실전 투입 우선순위**: supertrend_multi 4h rank1 (avg=3.892), cmf 4h rank2 (avg=2.508)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 1h: 22 전략 × 8 windows (210일 train) → 약 7분 소요 (BTC 단독)

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 316 완료 후)
- `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}`
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← cmf_confirm 확정
- `narrow_range`: 번들에서 제거됨 (Cycle 316)

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 316 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}`
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}`
- `order_flow_imbalance_v2: {"trend_span": 20}`
- `cmf: {"buy_thresh": 0.10}`
