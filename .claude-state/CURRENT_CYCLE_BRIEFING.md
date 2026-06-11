# Current Cycle Briefing

_Cycle 299 완료 — 2026-06-11_
_카테고리: D(ML) + E(실행) + F(리서치)_

## 이번 사이클 요약

### 완료한 작업

1. **D(ML)**: price_cluster vol_regime_filter 파라미터 추가
   - `_atr_ratio()` 메서드: ATR(14)/close 비율로 변동성 레짐 판별
   - vol_regime_filter=True + thresh=0.025 실험 → 역효과 (trades 12→5, 0/8)
   - 절대값 thresh 방식의 한계 확인: BTC 4h에서 ATR/close 0.025는 너무 제한적
   - 코드 기능 유지, 향후 상대적 ATR(ATR/ATR_MA 비율) 방식 검토 필요

2. **E(실행)**: paper_simulation adaptive_slippage=True 활성화
   - ATR 기반 레짐별 가변 슬리피지: low=0.02%, normal=0.05%, high=0.15%
   - 기존 flat 0.05% → 더 현실적인 시장 충격 모델
   - price_cluster sideways 구간 유리(0.02%), cmf 트렌드 구간 보수적(0.15%)

3. **F(리서치)**: order_flow_imbalance_v2 delta_window 파라미터화
   - delta_window=7 실험 → 역효과 (sharpe -2.10, 2/8) → 기본값(10) 복원
   - 코드 기능 유지, delta_window 파라미터 탐색 완료

### 시뮬레이션 결과 (adaptive_slippage=True)

- Paper Sim BTC 4h: **0/22 PASS**
  - rank1: price_cluster (score=71.5, Sharpe=3.41, PF=2.05, trades=12, 2/8 PASS)
  - rank8: order_flow_imbalance_v2 (trend_span=20, 3/8 PASS 복원)
- Bundle OOS: **2/5 PASS** (cmf, supertrend_multi - Cycle 298과 동일)
- 테스트: **8392 passed, 23 skipped** (전체 스위트)

### 다음 사이클 (300)

- **A(품질) + C(데이터) + F(리서치)**
- 300 mod 5 = 0 → A + C + F
- price_cluster vol_regime_filter 상대적 ATR 방식으로 개선 (A 품질)
- order_flow_imbalance_v2 BUY_THRESH 0.25→0.30 강화 실험 (F 리서치)
- ETH real CSV 수집 가능성 재확인 (C 데이터)
