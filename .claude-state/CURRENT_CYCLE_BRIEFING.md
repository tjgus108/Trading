# Current Cycle Briefing

_Cycle 301 완료 — 2026-06-12_

## 완료된 작업

### B(리스크): bounce_pct 0.02→0.025
- `scripts/paper_simulation.py`: price_cluster bounce_pct 0.025 적용
- 목표(trades 증가)는 달성 실패 (trades=12 유지)
- 부수 효과: Sharpe 3.41→3.76 (+10%), PF 2.05→2.28 (+11%) 개선 → 유지 결정

### D(ML): 두 가지 실험 → 두 가지 역효과
- `vol_atr_trend_min=1.3`: SharpeStd 2.41→2.52 악화 → 1.5로 복원
- `quality_score_buy_threshold=0.85`: PF 1.48→1.33 역효과 → 0.80 복원

### F(리서치): ATR 기반 동적 bounce_pct 기능 추가
- `src/strategy/price_cluster.py`: `atr_bounce_factor` 파라미터 추가
  - 기본값=0.0 (비활성, 하위 호환 유지)
  - atr_bounce_factor>0: effective_bounce_pct = ATR/close × factor
  - 고변동성 → threshold 자동 확대, 저변동성 → 축소
- narrow_range fold3 분석: BTC 급등(30k→52k) 구간에서 NR 패턴 오작동 확인
  - 해결책 제안: 상대적 ATR 필터 추가 (다음 A 사이클)

## 시뮬레이션 요약

| 구분 | 결과 |
|------|------|
| Paper Sim PASS | 0/22 (price_cluster 2/8 일관성) |
| Bundle OOS PASS | 2/5 (cmf, supertrend_multi) ← 동일 유지 |
| 테스트 스위트 | 8392 passed, 23 skipped |

## 다음 사이클 (302): B(리스크) + D(ML) + F(리서치)
- B: price_cluster n_bins=5→7 실험 (trades 증가의 근본 접근)
- D: ATR 동적 bounce_pct 실험 (atr_bounce_factor=1.5~2.0)
- F: narrow_range 상대적 ATR 필터 구현 (fold3 극단 손실 해결)
