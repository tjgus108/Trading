# Next Steps

_Last updated: 2026-05-28 (Cycle 228 완료: E+A+SIM+F)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### ✓ Cycle 228 완료 (2026-05-28)
- **E(실행)**: PaperTrader load_state 스키마검증 + TWAP unfilled_qty 누적 재시도 (146 tests passed)
- **A(품질)**: MLSignalGenerator regime_aware 추론 통합 테스트 3개 추가 (74 tests passed)
- **SIM**: 0/22 PASS 유지 (합성 데이터 mc_p_value 편향)
- **F(리서치)**: TWAP MEV 봇 위험, Paper→Live 슬리피지 사례, MC test 편향 대안 조사

### 🎯 Cycle 229 작업 방향 (229 mod 5 = 4 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): 호가창 깊이 연동 검토
- 리서치 결과: TWAP 슬라이스 크기를 호가창 깊이에 동적 연동 필요
- DataFeed에서 order book depth 정보 접근 가능 여부 확인
- WebSocket ConnectionHealthMonitor 안정성 점검

#### B(리스크): MC permutation test 대안 검토
- Regime-aware Monte Carlo (레짐 블록 단위 셔플) 검토
- SPA(Superior Predictive Ability) test 구현 가능성 평가
- mc_p_threshold 0.05 → 0.10 완화 옵션 추가 (실전 데이터 검증 후 적용)

#### F(리서치): 레짐 기반 MC test + 실전 전환 체크리스트
- Regime-aware MC permutation 구현 사례 리서치
- Paper→Live 전환 체크리스트 정립 (호가창 깊이 비율 등)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만 — "실전 PASS" 단정 금지

### 핵심 메트릭
- 상위 3 전략: supertrend_multi(Sharpe 7.39), momentum_quality(6.25), price_action_momentum(6.58)
- 모두 Sharpe≥1.0, PF≥1.5, MDD≤20% 충족 → mc_p_value만 탈락
- 테스트: 7,800+ passed
