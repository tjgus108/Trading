# Next Steps

_Last updated: 2026-05-28 (Cycle 234 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 228 → 234 (7사이클)

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 228 | E+A+SIM+F | PaperTrader load_state 검증, TWAP unfilled_qty, regime 통합테스트 |
| 229 | C+B+SIM+F | order_book_depth, 동적 타임아웃, --mc-p-threshold 옵션 |
| 230 | D+E+SIM+F | depth_imbalance 피처, TWAP 동적 슬라이스, SPA 분석 |
| 231 | A+C+SIM+F | 테스트 32개 추가, OFICalculator, MC block_size, Fractional Kelly |
| 232 | B+D+SIM+F | KellySizer dynamic fraction, VPIN 피처, Sharpe IC, 버그 1건 수정 |
| 233 | C+B+SIM+F | OFI/VPIN 상관성 분석, Kelly+MDD 통합, --pass-ratio 인자 추가 |
| 234 | D+E+SIM+F | bid_ask_depth_imbalance 제거, regime fold weighting, TWAP volume-weights |

### 🎯 Cycle 235 작업 방향 (235 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): mc_p_value 계산 개선 + narrow_range PF 미달 분석
- Cycle 234 Paper SIM: narrow_range PF 1.49 (기준 1.5에 -0.01 미달)
  - `src/strategy/narrow_range.py` 신호 임계값 확인
  - exit_pct 또는 min_range_ratio 파라미터 소폭 조정 검토
  - 단, 합성 데이터 기준이므로 실거래소 검증 후 확정
- momentum_quality: Sharpe 5.08이지만 mc_p_value > 0.05 → Consistency 0/4
  - `scripts/paper_simulation.py` mc_p_value 계산 로직 점검
  - Monte Carlo block bootstrap block_size 영향도 분석

#### C(데이터): BlockBootstrap 블록 크기 확대 + WebSocket 안정성
- IS Sharpe 100% 음수(cmf, wick_reversal): GBM block_size=36봉이 너무 짧아 추세 소실
  - `scripts/paper_simulation.py`: block_size 36 → 72봉 (72h = 3일) 검토
  - 72봉 블록으로 추세 성분 보존 → IS Sharpe 음수 비율 감소 기대
- `src/data/websocket_feed.py`: 재연결 exponential backoff 검증

#### SIM: use_regime_weights=True 효과 검증
- 이번 사이클(234) walk_forward에 use_regime_weights 추가됨
- 다음 SIM에서 OOS Sharpe std 감소 확인 (목표: 3.4~6.4 → < 2.0)
- run_bundle_oos.py에 --use-regime-weights 플래그 추가 검토

#### F(리서치): GBM 합성 데이터 vs 실거래소 乖離 + 블록 크기 영향
- GBM block_size 감도 분석: 36/72/144봉 비교 → IS Sharpe 분포 변화
- narrow_range fold 8: OOS Sharpe -14.1 극단값 → IS/OOS 레짐 불일치 원인 분석

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭
- 상위 3: momentum_quality(Sharpe 5.08, +55%), price_action_momentum(Sharpe 3.74, +47%), narrow_range(Sharpe 3.35, PF 1.49)
- 테스트: 8,127 passed (Cycle 234 +14개)
- 새로 추가된 인프라:
  - bid_ask_depth_imbalance 중복 제거 (features.py)
  - regime 조건부 fold 가중치 (walk_forward.py use_regime_weights)
  - TWAP volume-weighted slices (twap.py volume_weights)
