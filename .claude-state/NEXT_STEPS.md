# Next Steps

_Last updated: 2026-04-20 (Cycle 165 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 166
- 166 mod 5 = 1 → **A(품질) + C(데이터) + F(리서치)** 패턴

### ✅ Cycle 165 완료 사항

#### D(ML): XGBoost 모델 옵션 추가 ✅ COMPLETE
- model_type="xgboost": max_depth=3, lr=0.03, early_stopping=50
- xgboost 미설치 시 RF fallback, multi-class 자동 감지
- 테스트 7개 추가 → 53 passed, 3 skipped

#### E(실행): PSI → AccuracyDriftMonitor 통합 ✅ COMPLETE
- set_feature_reference + check_feature_drift + should_retrain 자동 PSI 반영
- 기존 동작 100% 하위호환 (PSI 미설정 시)
- 테스트 6개 추가 → 53 passed

#### F(리서치): 모니터링 + Paper→Live 전환 ✅ COMPLETE
- 알림 3계층 (Critical/Silent/Suppress) + 5분 throttle
- Paper→Live gate: Sharpe≥1.0, PF≥1.5, MDD≤20%
- 3단계 자본 스케일업, Hard rollback (MDD 15%)

### ⚠️ 핵심 문제: 전략 엣지 부재 → 해법 확인됨

22개 전략 모두 실데이터 6개월 WF에서 0 PASS. **유효한 경로:**

#### 경로 1: ML 2-class (UP/DOWN) — **PASS 확인 (42일 WF)**
- BTC 1000캔들: test acc 63.5%, val 67.3% → **PASS**

**다음 구현 과제 (우선순위):**
1. ~~FR delta + OI~~ ✅ | 2. ~~SHAP~~ ✅ | 3. ~~calibration~~ ✅ | 4. ~~ExtraTrees~~ ✅
5. ~~XGBoost 모델~~ ✅ | 6. **XGBoost 다시간 앙상블** — stacking, 30/60/90일
7. ~~MDD CB~~ ✅ | 8. ~~max_loss_pct~~ ✅ | 9. ~~PSI~~ ✅ | 10. ~~수수료~~ ✅
11. ~~PSI-AccDrift 통합~~ ✅ | 12. **live_paper_trader 7일 운영**
13. **Telegram 알림** — Critical/Silent 3계층
14. **Health check 루프** — 5분 liveness + 데이터 지연 감지
