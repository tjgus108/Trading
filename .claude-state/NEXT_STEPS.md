# Next Steps

_Last updated: 2026-04-20 (Cycle 163 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 164
- 164 mod 5 = 4 → **C(데이터) + B(리스크) + F(리서치)** 패턴

### ✅ Cycle 163 완료 사항

#### E(실행): live_paper_trader max_loss_pct 구현 ✅ COMPLETE
- `MAX_LOSS_PCT=0.50` + `_halted` 플래그 + `_check_max_loss()` 메서드
- tick() 최상단에서 halt 체크, 수동 재시작 필요
- `min_accuracy` 0.52 → 0.55 상향
- 테스트 3건 추가 → 37 PASS

#### A(품질): FeatureBuilder 테스트 커버리지 ✅ COMPLETE
- `tests/test_feature_builder.py` 29개 테스트 신규
- build(), 레이블 모드, 선택적 피처, 엣지케이스 전부 커버
- 7,057 passed, 신규 실패 없음

#### F(리서치): ML 드리프트 + 소자본 운영 ✅ COMPLETE
- PSI > 0.2 재학습 트리거 (업계 표준 확인)
- 다시간 윈도우 앙상블(30/60/90일) 권장
- 소자본: maker 주문 필수, 4h 스윙 유리, 레짐별 가변 슬리피지

### ⚠️ 핵심 문제: 전략 엣지 부재 → 해법 확인됨

22개 전략 모두 실데이터 6개월 WF에서 0 PASS. **유효한 경로:**

#### 경로 1: ML 2-class (UP/DOWN) — **PASS 확인 (42일 WF)**
- BTC 1000캔들: test acc 63.5%, val 67.3% → **PASS**

**다음 구현 과제 (우선순위):**
1. ~~**FR delta + OI 파생 피처 추가**~~ ✅ DONE
2. ~~**SHAP 피처 선택**~~ ✅ DONE
3. ~~**calibration hold-out 분리**~~ ✅ DONE
4. ~~**ExtraTrees 시도**~~ ✅ DONE
5. **XGBoost 다시간 앙상블** — 30/60/90일 윈도우, 드리프트 시 최신 가중치 상승
6. ~~**MDD Circuit Breaker 강화**~~ ✅ DONE
7. ~~**max_loss_pct 구현**~~ ✅ DONE — 50% 자동 중단
8. **PSI 드리프트 모니터** — 피처 분포 변화 감지 → 자동 재학습 트리거
9. **수수료 현실화** — Taker 0.055%, 고변동성 슬리피지 0.3%
10. **live_paper_trader 실제 운영** — 7일 테스트
