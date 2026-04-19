# Next Steps

_Last updated: 2026-04-19 (Cycle 154 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 155
- 155 mod 5 = 0 → **D(ML) + E(실행) + F(리서치)** 패턴

### ✅ Cycle 154 완료 사항

#### C(데이터): DataFeed Circuit Breaker ✅ COMPLETE
- `src/data/feed.py`에 CircuitState + CircuitBreaker 추가
- 3-state 자동복구 (CLOSED→OPEN→HALF_OPEN)
- 13개 테스트 추가 (93/93 PASS)

#### B(리스크): CircuitBreaker 경계값 테스트 ✅ COMPLETE
- `tests/test_risk.py`에 22개 경계값 테스트 추가
- 54/54 PASS

#### F(리서치): 성공/실패 사례 + ML 개선 ✅ COMPLETE
- 장기 생존 봇: 리스크 관리 > 알파, MDD 10% 기준 권장
- ML: Funding Rate + OI 피처 → 3~5%p 향상, RF+XGBoost 앙상블 권장

### ⚠️ 핵심 문제: 전략 엣지 부재 → 해법 확인됨

22개 전략 모두 실데이터 6개월 WF에서 0 PASS. **유효한 경로:**

#### 경로 1: ML 2-class (UP/DOWN) — **PASS 확인 (42일 WF)**
- BTC 1000캔들: test acc 63.5%, val 67.3% → **PASS**

#### 경로 2: 레짐 필터링
- RANGING (28%): 거래 금지 ✅

**다음 구현 과제 (우선순위):**
1. **Funding Rate + OI 피처 추가** — Bybit API, 3~5%p 정확도 향상 기대
2. **RF + XGBoost 앙상블** — 소프트 보팅, Drift 대응 보완
3. **MDD Circuit Breaker 강화** — 20%→10%, 포지션 사이즈 단계적 축소
4. **Triple Barrier 실데이터 검증** — `--bybit --triple-barrier --binary`
5. **live_paper_trader 실제 운영** — 7일 테스트
