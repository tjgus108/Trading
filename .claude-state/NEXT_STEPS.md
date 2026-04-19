# Next Steps

_Last updated: 2026-04-20 (Cycle 159 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 160
- 160 mod 5 = 0 → **D(ML) + E(실행) + F(리서치)** 패턴 (0→5번째)

### ✅ Cycle 159 완료 사항

#### C(데이터): FR+OI 3계층 구현 ✅ COMPLETE
- connector/feed/features에 FR delta + OI 파생 피처 통합, 24개 테스트

#### B(리스크): MDD 4단계 서킷브레이커 ✅ COMPLETE
- MddLevel enum (NORMAL/WARN/BLOCK/LIQUIDATE/HALT), 31개 테스트 추가 (총 85)

#### SIM: calibration hold-out 분리 ✅ COMPLETE
- 60/15/15/10 분할, val_acc 누출 수정, 39개 테스트 PASS

#### F(리서치): 포지션 사이징 리서치 ✅ COMPLETE
- Kelly quarter-cap, regime→sizing 연결, MDD soft/hard 이중 기준

### ✅ Cycle 158 완료 사항 (요약)

#### E(실행): Exchange 테스트 추가 ✅ COMPLETE
- connector.py 53개 + paper_connector.py 27개 = 98개 테스트 (94 pass)
- `_call_with_deadline` Python 3.9+ 전용 확인

#### A(품질): 실패 테스트 수정 + trainer 테스트 ✅ COMPLETE
- `sys.executable` 수정으로 2개 실패 해결
- `tests/test_trainer.py` 38개 추가, 147 전체 PASS

#### SIM: paper_simulation.py 리뷰 ✅ COMPLETE
- 타입힌트 버그 수정 (`Optional[pd.DataFrame]`)
- calibration hold-out 분리 권장

#### F(리서치): ML봇 실패/성공 리서치 ✅ COMPLETE
- FR delta+OI 피처 권장, XGBoost max_depth≤3 필수
- WF PASS 기준 완화 금지 확인

### ⚠️ 핵심 문제: 전략 엣지 부재 → 해법 확인됨

22개 전략 모두 실데이터 6개월 WF에서 0 PASS. **유효한 경로:**

#### 경로 1: ML 2-class (UP/DOWN) — **PASS 확인 (42일 WF)**
- BTC 1000캔들: test acc 63.5%, val 67.3% → **PASS**

#### 경로 2: 레짐 필터링
- RANGING (28%): 거래 금지 ✅

**다음 구현 과제 (우선순위):**
1. ~~**FR delta + OI 파생 피처 추가**~~ ✅ DONE — Cycle 159: connector/feed/features 3계층 구현, 24개 테스트 (18 pass, 6 skip[ccxt 미설치])
2. **SHAP 피처 선택** — 15→6~8개로 축소, 노이즈 피처 제거
3. ~~**calibration hold-out 분리**~~ ✅ DONE — 60/15/15/10 분할 구현, val_acc 누출 방지 완료
4. **ExtraTrees 시도** — RF 대비 분산 감소 효과 검증
5. **XGBoost 앙상블** — max_depth≤3, early_stopping, RF와 앙상블
6. ~~**MDD Circuit Breaker 강화**~~ ✅ DONE — 4단계 MDD (5%/10%/15%/20%) + MddLevel enum + size_multiplier 통합, 31개 테스트 추가
7. **live_paper_trader 실제 운영** — 7일 테스트
