# Next Steps

_Last updated: 2026-04-21 (Cycle 171 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 172
- 172 mod 5 = 2 → **B(리스크) + D(ML) + F(리서치)** 패턴

### ✅ Cycle 171 완료 사항

#### A(품질): 테스트 커버리지 +68개 ✅ COMPLETE
- paper_trader edge case 21개 + ML pipeline 25개 + VPIN 14 + WebSocket 9
- paper_trader input validation 추가 (ZeroDivision 방지)

#### C(데이터): VPIN + WebSocket 강화 ✅ COMPLETE
- VPIN: 음수볼륨, NaN, zero-volume, mega spike 처리
- WebSocket: exponential backoff + jitter + ConnectionMetrics

#### F(리서치): Live Trading 전환 교훈 ✅ COMPLETE
- 73% 실패율, 과최적화 1위 원인, 소자본 월 1~5% 현실

### ⚠️ 핵심 문제: 전략 엣지 부재 → ML 경로

**다음 구현 과제 (우선순위):**
1. ~~FR delta + OI~~ ✅ | 2. ~~SHAP~~ ✅ | 3. ~~calibration~~ ✅ | 4. ~~ExtraTrees~~ ✅
5. ~~XGBoost 모델~~ ✅ | 6. ~~XGBoost 다시간 앙상블~~ ✅
7. ~~MDD CB~~ ✅ | 8. ~~max_loss_pct~~ ✅ | 9. ~~PSI~~ ✅ | 10. ~~수수료~~ ✅
11. ~~PSI-AccDrift 통합~~ ✅ | 12. **live_paper_trader 7일 운영** ← 다음 E 사이클
13. ~~Telegram 알림~~ ✅ (스켈레톤) | 14. ~~Health check~~ ✅
15. ~~Kelly 레짐 스무딩~~ ✅ | 16. ~~CF VaR~~ ✅
17. ~~DrawdownMonitor 레짐 cooldown~~ ✅ | 18. ~~CB 일일 제한~~ ✅
19. ~~DataFeed 레짐 TTL~~ ✅ | 20. ~~갭 감지~~ ✅
21. ~~VPIN/OrderFlow 엣지케이스~~ ✅ | 22. ~~WebSocket 재연결 안정성~~ ✅
23. **레짐별 동적 피처 파이프라인** — 피처 중요도 역전 대응 ← 다음 D 사이클
24. **Telegram 실제 API 연동** — 스켈레톤 → 실제 전송

### Cycle 172 권장 작업
- **B(리스크)**: Kelly sizer stress test (극단 시나리오), VaR backtest (실제 vs 예측)
- **D(ML)**: 레짐별 동적 피처 선택 파이프라인, LSTM 재학습 with 최신 데이터
- **F(리서치)**: Online learning / incremental RL 구현 방법론, adaptive Kelly 최신 연구
