# Next Steps

_Last updated: 2026-04-21 (Cycle 172 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 173
- 173 mod 5 = 3 → **E(실행) + A(품질) + F(리서치)** 패턴

### ✅ Cycle 172 완료 사항

#### B(리스크): Kelly Stress + VaR Backtest ✅ COMPLETE
- Kelly 극단 시나리오 11개 (win_rate 0/1, ATR 10x, 연속손실 10/20회, 레짐급전환)
- VaR backtest 5개 (초과율 3~8%, CF≥Normal 확인)

#### D(ML): RegimeAwareFeatureBuilder ✅ COMPLETE
- detect_regime(): ATR z-score + Donchian + EMA20/50
- REGIME_FEATURE_CONFIG: bull 10, bear 9, ranging 8, crisis 5 피처
- WalkForwardTrainer regime_aware=True 지원
- 25개 테스트 PASS, 기존 89개 ML 테스트 깨짐 없음

#### F(리서치): Online Learning + Adaptive Kelly ✅ COMPLETE
- River ADWIN 증분학습, Bayesian Kelly, 소자본 10~25% Kelly 권장

### ⚠️ 핵심 문제: 전략 엣지 부재 → ML 경로

**다음 구현 과제 (우선순위):**
1. ~~FR delta + OI~~ ✅ | 2. ~~SHAP~~ ✅ | 3. ~~calibration~~ ✅ | 4. ~~ExtraTrees~~ ✅
5. ~~XGBoost 모델~~ ✅ | 6. ~~XGBoost 다시간 앙상블~~ ✅
7. ~~MDD CB~~ ✅ | 8. ~~max_loss_pct~~ ✅ | 9. ~~PSI~~ ✅ | 10. ~~수수료~~ ✅
11. ~~PSI-AccDrift 통합~~ ✅ | 12. **live_paper_trader 7일 운영** ← 다음 E 사이클 (Cycle 173)
13. ~~Telegram 알림~~ ✅ (스켈레톤) | 14. ~~Health check~~ ✅
15. ~~Kelly 레짐 스무딩~~ ✅ | 16. ~~CF VaR~~ ✅
17. ~~DrawdownMonitor 레짐 cooldown~~ ✅ | 18. ~~CB 일일 제한~~ ✅
19. ~~DataFeed 레짐 TTL~~ ✅ | 20. ~~갭 감지~~ ✅
21. ~~VPIN/OrderFlow 엣지케이스~~ ✅ | 22. ~~WebSocket 재연결 안정성~~ ✅
23. ~~레짐별 동적 피처 파이프라인~~ ✅ | 24. **Telegram 실제 API 연동**
25. **Bayesian Kelly 구현** — Beta 분포 기반 불확실성 반영 포지션 사이징
26. **River ADWIN 통합** — 피처 드리프트 실시간 감지 + 모델 업데이트

### Cycle 173 권장 작업 (173 mod 5 = 3 → E+A+F)
- **E(실행)**: live_paper_trader 7일 운영 스크립트 준비, 레짐별 성과 추적 로깅
- **A(��질)**: RegimeAwareFeatureBuilder 통합 테스트, E2E 파이프라인 검증
- **F(리서치)**: Bayesian Kelly 구현 사례, live trading 모니터링 best practices
