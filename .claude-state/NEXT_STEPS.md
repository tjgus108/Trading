# Next Steps

_Last updated: 2026-05-28 (Cycle 230 완료: D+E+SIM+F)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### ✓ Cycle 230 완료 (2026-05-28)
- **D(ML)**: bid_ask_depth_imbalance 피처 + compare_feature_importance() (118 tests passed)
- **E(실행)**: TWAP order book depth 기반 동적 슬라이스 (76 tests passed)
- **SIM**: SPA test 분석 (arch 미설치, 교체 ~20-30줄), mc_p_threshold=0.10 시뮬레이션 실행
- **F(리서치)**: OFI/VPIN 예측력, CPCV vs WFO, BitMEX flash crash, Fractional Kelly 권장

### 🎯 Cycle 231 작업 방향 (231 mod 5 = 1 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 테스트 커버리지 점검
- bid_ask_depth_imbalance 피처의 통합 테스트 확인
- TWAP 동적 슬라이스의 엣지 케이스 테스트 보강
- compare_feature_importance() 메서드 테스트

#### C(데이터): OFI 기반 실행 필터 검토
- 리서치 결과: OFI 급격히 음수면 매수 실행 지연/회피
- DataFeed에서 OFI 계산 가능 여부 확인
- VPIN 극단 불균형 감지와 OFI의 통합 가능성

#### F(리서치): CPCV 구현 사례 + Fractional Kelly 검증
- CPCV(Combinatorial Purged Cross-Validation) 구현 라이브러리 조사
- 현재 KellySizer의 fraction 상한이 적절한지 검토 (10-25% 권장)
- arch 라이브러리 설치 시 SPA test 적용 방안

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭
- 상위 3: supertrend_multi(Sharpe 7.39), momentum_quality(6.25), price_action_momentum(6.58)
- mc_p_value만 탈락, 테스트: ~7,880 passed
