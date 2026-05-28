# Next Steps

_Last updated: 2026-05-28 (Cycle 232 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 228 → 232 (5사이클)

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 228 | E+A+SIM+F | PaperTrader load_state 검증, TWAP unfilled_qty, regime 통합테스트 |
| 229 | C+B+SIM+F | order_book_depth, 동적 타임아웃, --mc-p-threshold 옵션 |
| 230 | D+E+SIM+F | depth_imbalance 피처, TWAP 동적 슬라이스, SPA 분석 |
| 231 | A+C+SIM+F | 테스트 32개 추가, OFICalculator, MC block_size, Fractional Kelly |
| 232 | B+D+SIM+F | KellySizer dynamic fraction, VPIN 피처, Sharpe IC, 버그 1건 수정 |

### 🎯 Cycle 233 작업 방향 (233 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): WebSocket 피드 안정성 + 온체인 피처
- stale_timeout=None 기본값 변경 후 기존 REST fallback 경로 검증
- OFI + VPIN 상관성 분석: OFICalculator vs bid_ask_depth_imbalance vs vpin_50
  - 세 피처의 Pearson/Spearman 상관계수 계산 (중복 제거 여부 판단)
- exchange_netflow / sopr 온체인 피처 파이프라인 검증

#### B(리스크): DrawdownMonitor + 레짐 통합
- DrawdownMonitor.get_mdd_size_multiplier() + KellySizer.update_fraction_for_regime() 통합
  - 레짐 HIGH_VOL 시: Kelly fraction 10% + MDD multiplier 동시 적용
  - RiskManager에서 두 모듈 연결하는 코드 추가
- VaR/CVaR 일일 리포트 자동화: DrawdownStatus에 cf_var 필드 추가 검토

#### SIM: Sharpe IC 효과 측정
- walk_forward.py Sharpe IC 변경 후 OOS Sharpe std 변화 측정
- narrow_range, value_area 재시뮬레이션 (3/9 fold PASS → 개선 여부)
- paper_simulation.py에서 consistency 기준 완화 테스트 (50% → 33%)

#### F(리서치): 레짐 이질성 + 피처 중복 제거
- OOS Sharpe std 원인: IS/OOS 레짐 불일치 → 레짐 조건부 fold 가중 선택
- 피처 중복: OFI ≈ bid_ask_depth_imbalance ≈ VPIN의 상관성 분석
  - Cycle 233에서 PFI 비교로 중복 피처 제거 여부 결정

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭
- 상위 3: price_action_momentum(Sharpe 3.81, +49%), momentum_quality(Sharpe 3.91), supertrend_multi
- 테스트: 8,101 passed (Cycle 232 +146개)
- 새로 추가된 인프라: KellySizer dynamic fraction, VPIN 피처, Sharpe IC 파라미터 선택
