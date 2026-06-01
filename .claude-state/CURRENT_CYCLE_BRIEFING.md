# Current Cycle Briefing

_Cycle 257 — 2026-06-01_
_카테고리: B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크): HIGH Confidence 포지션 사이징 축소
- `src/backtest/engine.py`: HIGH confidence multiplier 1.5 → 1.2
- `src/risk/manager.py`: CONFIDENCE_MULTIPLIER HIGH 1.5 → 1.2 (동기화)
- 목적: acceleration_band SOL MDD 23%>20% 해결
- 효과: acceleration_band MDD 23%→8.3% (목표 달성), 단 SOL 총 PASS 8→4 (mixed)

### D(ML): REGIME_FEATURE_CONFIG 업데이트
- `src/ml/features.py`:
  - `"bull"` 레짐: `mom_quality_score` 추가 (SOL price_action_momentum 핵심 피처)
  - `"ranging"` 레짐: `trend_strength` 추가 (momentum_quality 전략 지원)
  - 피처 수: bull 10→11, ranging 8→9

### F(리서치): OOS Sharpe std 저거래 fold 제외
- `src/backtest/walk_forward.py`:
  - `WindowResult.oos_trades` 필드 추가
  - OOS std 계산: 저거래 fold (< 30 trades) 제외
  - 근거: 저거래 OOS fold의 Sharpe는 통계적으로 신뢰 불가 (trades=7에서 Sharpe=7.674 같은 이상치)

## 시뮬레이션 결과 (Cycle 257)
- Paper Sim BTC 1h (CSV): 0/22 PASS
  - Top: supertrend_multi(0.50), price_cluster(0.41)
- Paper Sim ETH (합성): **5/22 PASS** ↑ (Cycle 256 3/22)
  - momentum_quality(4/4, 5.56), supertrend_multi(3/4, 4.78), price_action_momentum(2/4, 3.80)
- Paper Sim SOL (합성): **4/22 PASS** ↓ (Cycle 256 8/22)
  - momentum_quality(4/4, 4.89), acceleration_band(2/4, MDD 8.3%)
- Bundle OOS BTC 4h: 0/5 PASS (narrow_range #1 Score 87.1, OOS Sharpe std 5.203)

## 다음 Cycle 258 (258 mod 5 = 3 → C+B+F)
- C: ETH/SOL CSV 데이터 생성 (합성 데이터 품질 개선 — 4 windows→8 windows)
- B: HIGH conf 1.2→1.35 재검토 (SOL PASS 8→4 원인 분석)
- F: Bundle OOS std 저거래 제외 효과 측정, run_bundle_oos.py에도 동일 로직 적용 검토
