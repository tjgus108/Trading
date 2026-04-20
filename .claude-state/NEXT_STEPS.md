# Next Steps

_Last updated: 2026-04-20 (Cycle 164 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 165
- 165 mod 5 = 0 → **D(ML) + E(실행) + F(리서치)** 패턴

### ✅ Cycle 164 완료 사항

#### C(데이터): 수수료 현실화 + adaptive 슬리피지 ✅ COMPLETE
- 수수료 0.1% → Bybit taker 0.055% (7개 파일), maker 0.020% 상수 정의
- adaptive_slippage: ATR/close 기반 레짐별 가변 (low 0.02%, normal 0.05%, high 0.15%)
- 테스트 9개 추가 → 48 PASS

#### B(리스크): PSI 드리프트 모니터 ✅ COMPLETE
- compute_psi() + PSIDriftMonitor 구현 (drift_detector.py)
- 4단계: stable/warning/drift/severe, PSI > 0.2 = 재학습 트리거
- 테스트 19개 추가 → 47 PASS

#### F(리서치): XGBoost 앙상블 + 다시간 윈도우 ✅ COMPLETE
- RF base + XGBoost meta stacking 권장
- 30/60/90일 윈도우에 다른 알고리즘 할당 (상관도 낮추기)
- max_depth ≤ 3, early_stopping=50, lr 0.01~0.05

### ⚠️ 핵심 문제: 전략 엣지 부재 → 해법 확인됨

22개 전략 모두 실데이터 6개월 WF에서 0 PASS. **유효한 경로:**

#### 경로 1: ML 2-class (UP/DOWN) — **PASS 확인 (42일 WF)**
- BTC 1000캔들: test acc 63.5%, val 67.3% → **PASS**

**다음 구현 과제 (우선순위):**
1. ~~**FR delta + OI 파생 피처 추가**~~ ✅ DONE
2. ~~**SHAP 피처 선택**~~ ✅ DONE
3. ~~**calibration hold-out 분리**~~ ✅ DONE
4. ~~**ExtraTrees 시도**~~ ✅ DONE
5. **XGBoost 다시간 앙상블** — RF+XGB stacking, 30/60/90일, softmax 동적 가중치
6. ~~**MDD Circuit Breaker 강화**~~ ✅ DONE
7. ~~**max_loss_pct 구현**~~ ✅ DONE
8. ~~**PSI 드리프트 모니터**~~ ✅ DONE
9. ~~**수수료 현실화**~~ ✅ DONE
10. **PSI → AccuracyDriftMonitor 통합** — input+output 양방향 감지
11. **live_paper_trader 실제 운영** — 7일 테스트
