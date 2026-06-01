# Current Cycle Briefing

_Cycle 256 — 2026-06-01_
_카테고리: B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크): BacktestEngine atr_multiplier_tp 기본값 조정
- `src/backtest/engine.py`: atr_multiplier_tp 3.0 → 3.5 (R:R 2.33:1)
- Kelly sizer f* 공식 검증: 구현 정확 (f* = p - q/b)
- 효과: SOL 6/22 → 8/22 PASS, price_action_momentum sharpe 4.18→5.48

### D(ML): FeatureBuilder 모멘텀 품질 피처 추가
- `src/ml/features.py`:
  - `mom_quality_score`: ROC5 z-score (price_action_momentum 핵심 신호 피처화)
  - `trend_strength`: (consistency×2-1) + (mom5>mom10) (momentum_quality 핵심 피처화)
  - feature_names: 16 → 18
- 테스트 4개 파일 업데이트 (feature count)
- 전체 테스트: 8369 passed (신규 2건 추가)

### F(리서치): atr_multiplier_tp PF 효과 분석
- R:R=2.33:1: PF=1.5 달성 최소 win_rate 39.2% (이전 42.9%), 3.7%p 완화
- BTC 0/22 PASS: GARCH CSV가 trend-insufficient → 합성 데이터로 대체 불가
- SOL 8/22 PASS 중 price_action_momentum 4/4 윈도우 완전 일관성

## 시뮬레이션 결과 (Cycle 256)
- Paper Sim BTC: 0/22 PASS (AvgPF 1.0~1.2)
- Paper Sim ETH: 3/22 PASS
- Paper Sim SOL: **8/22 PASS** (Cycle 255 6/22 → 개선)
- Bundle OOS BTC 4h: 0/5 PASS (OOS Sharpe std 3.9~8.5, 여전히 불안정)

## 다음 Cycle 257 (257 mod 5 = 2 → B+D+F)
- B: momentum_quality MDD 개선 (22%>20% 초과 → MDD 제약 강화 검토)
- B: acceleration_band SOL MDD 23% 초과 → 포지션 사이징 조정
- D: mom_quality_score, trend_strength REGIME_FEATURE_CONFIG["bull"] 추가 (테스트 영향 확인 필요)
- D: BTC 0/22 원인 분석 — price_action_momentum이 SOL에선 4/4 PASS인데 BTC에선 PF 1.00 → 심볼 특성 차이 분석
- F: Bundle OOS Sharpe std 개선을 위한 파라미터 안정화 방안 (narrowing grid search)
