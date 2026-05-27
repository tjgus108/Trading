# Next Steps

_Last updated: 2026-05-28 (Cycle 229 완료: C 개선)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### ✓ Cycle 229 완료 (2026-05-28)
- **C(데이터)**: 
  - DataFeed.get_order_book_depth() 추가 (호가창 깊이 조회, TWAP 슬라이스 연동용)
  - BinanceWebSocketFeed 타임프레임 기반 동적 타임아웃 계산 
  - ConnectionHealthMonitor.validate_timeout_setting() 검증 메서드
  - 신규 테스트 10/10 PASS + 기존 테스트 39/39 PASS

### 🎯 Cycle 230 작업 방향 (230 mod 5 = 0 → A(품질) + D(ML) + SIM + F(리서치))

#### A(품질): 데이터 품질 메트릭 수집 강화
- Anomaly 감지율 추적 (duplicate_close, stale_feed, timestamp_gap 등)
- Cache hit/miss 비율 실시간 모니터링
- Order book depth 사용률 추적 (TWAP 슬라이스 조정용)

#### D(ML): Regime-aware VWAP 특성 추가
- order_book_depth → ask/bid depth imbalance 피처
- 호가창 스프레드 변동성 = 시장 유동성 지표
- 레짐별 호가창 깊이 프로파일 분석

#### SIM: MC permutation test 대안 평가
- Regime-aware Monte Carlo: 블록 단위 셔플 (기존 완전 셔플 대체)
- Block size selection: 블록 길이 = 레짐 전환 기간
- SPA test 검토 (Superior Predictive Ability, Hansen 2005)

#### F(리서치): TWAP 슬라이스 최적화
- 호가창 깊이 비율 → 슬라이스 크기 매핑 (동적 TWAP)
- 고변동성 시장에서 호가창 깊이 급락 시 슬라이스 축소
- Paper→Live 체크리스트 (호가창 데이터 신뢰도, 스프레드 임계값)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만 — "실전 PASS" 단정 금지
- Order book depth 실제 거래소 데이터는 아직 미수집 (스텁 상태)

### 핵심 메트릭
- 상위 3 전략: supertrend_multi(Sharpe 7.39), momentum_quality(6.25), price_action_momentum(6.58)
- 모두 Sharpe≥1.0, PF≥1.5, MDD≤20% 충족 → mc_p_value만 탈락
- 테스트: 7,849 passed (229 추가)
