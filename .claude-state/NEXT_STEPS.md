# Next Steps

_Last updated: 2026-05-28 (Cycle 228-231 세션 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 228 → 231 (4사이클)

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 228 | E+A+SIM+F | PaperTrader load_state 검증, TWAP unfilled_qty, regime 통합테스트 |
| 229 | C+B+SIM+F | order_book_depth, 동적 타임아웃, --mc-p-threshold 옵션 |
| 230 | D+E+SIM+F | depth_imbalance 피처, TWAP 동적 슬라이스, SPA 분석 |
| 231 | A+C+SIM+F | 테스트 32개 추가, OFICalculator, MC block_size, Fractional Kelly |

### 🎯 Cycle 232 작업 방향 (232 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): KellySizer 동적 fraction
- Quarter-Kelly(25%) 실무 표준 (리서치 Cycle 231)
- 현재 CF 클리핑은 있으나 fraction 동적 조정 미구현
- 레짐별 Kelly fraction: 고변동성→10%, 저변동성→25%
- Risk-Constrained Kelly (drawdown 확률 제약 결합) 검토

#### D(ML): OFI + VPIN + depth_imbalance 통합
- OFICalculator(Cycle 231) + VPIN 극단감지 연동
- bid_ask_depth_imbalance 피처와 OFI의 상관성 분석
- 피처 중요도 비교: compare_feature_importance() 활용

#### SIM: block_size 효과 측정
- MC permutation block_size=5로 시뮬레이션 실행
- 기존 0/22 PASS에서 개선도 측정
- mc_p_threshold=0.10 + block_size=5 조합 테스트

#### F(리서치): CPCV + Stationary Bootstrap
- CPCV 구현 라이브러리 조사 (mlfinlab 등)
- Stationary Bootstrap + Politis-White 자동 블록 크기
- arch 라이브러리 설치 → SPA test 적용

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭
- 상위 3: supertrend_multi(Sharpe 7.39), momentum_quality(6.25), price_action_momentum(6.58)
- 테스트: ~7,900+ passed (이번 세션 +55개 이상 추가)
- 새로 추가된 인프라: OFICalculator, TTL 검증, MC block_size, TWAP 동적 슬라이스
