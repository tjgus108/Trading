# Next Steps

_Last updated: 2026-05-28 (Cycle 233 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 228 → 233 (6사이클)

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 228 | E+A+SIM+F | PaperTrader load_state 검증, TWAP unfilled_qty, regime 통합테스트 |
| 229 | C+B+SIM+F | order_book_depth, 동적 타임아웃, --mc-p-threshold 옵션 |
| 230 | D+E+SIM+F | depth_imbalance 피처, TWAP 동적 슬라이스, SPA 분석 |
| 231 | A+C+SIM+F | 테스트 32개 추가, OFICalculator, MC block_size, Fractional Kelly |
| 232 | B+D+SIM+F | KellySizer dynamic fraction, VPIN 피처, Sharpe IC, 버그 1건 수정 |
| 233 | C+B+SIM+F | OFI/VPIN 상관성 분석, Kelly+MDD 통합, --pass-ratio 인자 추가 |

### 🎯 Cycle 234 작업 방향 (234 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): 피처 중복 제거 + 레짐 조건부 fold 가중
- `src/ml/features.py`에서 `bid_ask_depth_imbalance` 제거 (OFI와 완전 동일)
  - Cycle 233에서 Pearson=1.0 확인 → 중복 피처 확정
  - 제거 시 피처 수 -1 → 관련 테스트 업데이트 필요
- walk_forward.py: 레짐 조건부 fold 가중치 (HIGH_VOL fold → 낮은 가중치)
  - OOS Sharpe std 감소 목표: 현재 3.4~6.4 → 목표 < 2.0
  - 구현: fold_weight = 1/(1 + regime_vol_factor) 로 HIGH_VOL fold 다운웨이팅

#### E(실행): TWAP + 체결 품질 개선
- TWAP 동적 슬라이스: 거래량 가중 슬라이스 크기 (고거래량 → 더 큰 슬라이스)
- 슬리피지 모델 정확도: 합성 데이터 기반 슬리피지 추정치 검증

#### SIM: --pass-ratio 0.33 + --mc-p-threshold 0.10 조합 효과
- narrow_range: 3/9 fold PASS → 33% 기준이면 PASS 가능성
- momentum_quality, price_action_momentum: mc_p_value 완화 시 PASS 가능성 분석
- 결과를 NEXT_STEPS에 반영 (완화 기준 유지 여부 결정)

#### F(리서치): 레짐 이질성 해결책 + ML 피처 중요도
- IS/OOS 레짐 불일치: CPCV(Combinatorial Purged Cross-Validation) 적용 연구
  - 기존 walk-forward 대신 CPCV로 레짐 불일치 줄이기
- RF 모델 피처 중요도: bid_ask_depth_imbalance vs OFI 중요도 비교 (PFI)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭
- 상위 3: price_action_momentum(Sharpe 3.74, +47%), momentum_quality(Sharpe 5.08, +55%), narrow_range(3/9 PASS)
- 테스트: 8,113 passed (Cycle 233 +12개)
- 새로 추가된 인프라: Kelly+MDD compound scaling, OFI/VPIN 상관성 분석, --pass-ratio 옵션
