# Next Steps

_Last updated: 2026-04-20 (Cycle 167 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 168
- 168 mod 5 = 3 → **E(실행) + A(품질) + F(리서치)** 패턴

### ✅ Cycle 167 완료 사항

#### B(리스크): Kelly 레짐 스무딩 + CF VaR ✅ COMPLETE
- `regime_smooth_alpha` EMA 블렌딩 (opt-in, 기본 0.0)
- Cornish-Fisher expansion: 왜도/첨도 반영 꼬리위험 VaR
- 테스트 4개 추가 → 174 passed (risk)

#### D(ML): MultiWindowEnsemble ✅ COMPLETE
- 30/60/90일 윈도우 RF/ExtraTrees/XGBoost 독립 학습
- softmax 동적 가중치 (temp=1.5), rolling 20거래 갱신
- 테스트 9개 추가

#### F(리서치): 실패/성공 사례 + 앙상블 실증 ✅ COMPLETE
- 자동화 계좌 73% 6개월 내 실패 (RESEARCH_CYCLE167.md)
- Stacking > Blending > Voting 실증 확인

### ⚠️ 핵심 문제: 전략 엣지 부재 → 해법 확인됨

22개 전략 모두 실데이터 6개월 WF에서 0 PASS. **유효한 경로:**

#### 경로 1: ML 2-class (UP/DOWN) — **PASS 확인 (42일 WF)**
- BTC 1000캔들: test acc 63.5%, val 67.3% → **PASS**

**다음 구현 과제 (우선순위):**
1. ~~FR delta + OI~~ ✅ | 2. ~~SHAP~~ ✅ | 3. ~~calibration~~ ✅ | 4. ~~ExtraTrees~~ ✅
5. ~~XGBoost 모델~~ ✅ | 6. ~~XGBoost 다시간 앙상블~~ ✅
7. ~~MDD CB~~ ✅ | 8. ~~max_loss_pct~~ ✅ | 9. ~~PSI~~ ✅ | 10. ~~수수료~~ ✅
11. ~~PSI-AccDrift 통합~~ ✅ | 12. **live_paper_trader 7일 운영** ← 다음 E 사이클
13. **Telegram 알림** — Critical/Silent 3계층
14. **Health check 루프** — 5분 liveness + 데이터 지연 감지
15. ~~Kelly 레짐 스무딩~~ ✅ | 16. ~~CF VaR~~ ✅
