======================================================================
🔄 CYCLE 234 — 2026-05-28
======================================================================

## 이번 사이클 배정 카테고리

### [D] ML & Signals
- **Focus**: 중복 피처 제거 + regime 조건부 fold 가중치
- **완료**:
  - `src/ml/features.py`: bid_ask_depth_imbalance 완전 제거 (OFI Pearson=1.0 중복)
  - `src/backtest/walk_forward.py`: use_regime_weights 파라미터 추가
    - HIGH_VOL fold 다운웨이팅: weight = 1/(1 + vol/mean_vol)
    - weighted_oos_sharpe에 반영 (PASS/FAIL 기준 avg_oos_sharpe는 변경 없음)
- **테스트**: 4개 신규

### [E] Execution
- **Focus**: TWAP 거래량 가중 슬라이스
- **완료**:
  - `src/exchange/twap.py`: volume_weights 파라미터 추가
    - 비례 슬라이스: slice_qty[i] = total_qty * weights[i] / sum(weights)
    - 잘못된 길이/None → 균등 슬라이스 fallback
  - `tests/test_twap.py`: TestVolumeWeightedSlices 10개 추가
- **테스트**: 10개 신규

## SIM 결과 요약

### Paper (Walk-Forward 1h봉)
- **0/22 PASS** (합성 GBM 데이터 한계)
- 상위: momentum_quality (Sharpe 5.08), price_action_momentum (Sharpe 3.74), narrow_range (Sharpe 3.35, PF 1.49)
- 공통 실패 원인: Consistency 0/4, mc_p_value > 0.05

### OOS Bundle (4h봉)
- **0/5 PASS**, OOS Sharpe std 3.4~6.4
- narrow_range: 3/9 fold PASS (최다)
- wick_reversal: 2/9 fold PASS
- IS Sharpe 100% 음수: cmf, wick_reversal (GBM 블록 크기 문제)

## 테스트 현황
- **8,127 passed** (+14 from Cycle 233)
- 회귀: 없음

## 다음 사이클: 235 (235 mod 5 = 0 → A(품질) + C(데이터) + F)
- A: narrow_range PF 1.49→1.5 분석, mc_p_value 로직 점검
- C: BlockBootstrap block_size 36→72 검토 (IS Sharpe 음수 개선)
- F: GBM 합성 vs 실거래소 데이터 乖離 분석
======================================================================
