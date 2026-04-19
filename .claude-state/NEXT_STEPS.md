# Next Steps

_Last updated: 2026-04-19 (Cycle 156 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 157
- 157 mod 5 = 2 → **B(리스크) + D(ML) + F(리서치)** 패턴

### ✅ Cycle 156 완료 사항

#### D(ML 긴급수정): RF 과적합 수정 ✅ COMPLETE
- `min_samples_leaf` + `min_samples_split` 추가, val_acc 누출 수정
- train_acc 0.99→0.80, test_acc 0.44→0.62
- `scripts/retrain_all.sh` 생성 (3심볼 일괄 재학습)

#### A(품질): 테스트 점검 ✅ COMPLETE
- 6,865개 테스트 중 2개 기존 실패 (모델 파일 이슈)
- exchange 모듈 테스트 부재 확인

#### C(데이터): 인프라 점검 ✅ COMPLETE
- 모든 모듈 정상, 개선 필요사항 없음

#### F(리서치): ML 과적합 방지 ✅ COMPLETE
- 피처 축소(SHAP), ExtraTrees, btc_return 피처 추가 권장

### ⚠️ 핵심 문제: 전략 엣지 부재 → 해법 확인됨

22개 전략 모두 실데이터 6개월 WF에서 0 PASS. **유효한 경로:**

#### 경로 1: ML 2-class (UP/DOWN) — **PASS 확인 (42일 WF)**
- BTC 1000캔들: test acc 63.5%, val 67.3% → **PASS**

#### 경로 2: 레짐 필터링
- RANGING (28%): 거래 금지 ✅

**다음 구현 과제 (우선순위):**
1. **SHAP 피처 선택** — 15→6~8개로 축소, 노이즈 피처 제거
2. **ExtraTrees 시도** — RF 대비 분산 감소 효과 검증
3. **Funding Rate + OI 피처 추가** — Bybit API, 3~5%p 정확도 향상 기대
4. **SOL/ETH btc_return 피처 강화** — rolling beta regression
5. **MDD Circuit Breaker 강화** — 20%→10%, 포지션 사이즈 단계적 축소
6. **exchange 모듈 테스트 추가** — connector.py, paper_connector.py
7. **live_paper_trader 실제 운영** — 7일 테스트
