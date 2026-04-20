# Next Steps

_Last updated: 2026-04-20 (Cycle 169 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 170
- 170 mod 5 = 0 (=5) → **D(ML) + E(실행) + F(리서치)** 패턴

### ✅ Cycle 169 완료 사항

#### C(데이터): 레짐 캐시 TTL + 갭 감지 ✅ COMPLETE
- `_effective_ttl()`: high_volatility 0.33x, crisis 0.2x, low_volatility 1.5x
- `_detect_anomalies()`: median 3배 초과 갭 자동 감지
- 테스트 10개 추가 → 118 passed

#### B(리스크): DrawdownMonitor 레짐 cooldown + CB 일일 제한 ✅ COMPLETE
- HIGH_VOL 2.0x, TREND_UP 0.5x cooldown 배수
- `max_daily_trades` 초과 시 거래 차단
- 테스트 15개 추가 → 173 passed

#### F(리서치): 소자본 + 레짐별 리스크 ✅ COMPLETE
- 소자본 수수료 잠식 분석, Stress-Gated Mutation 패턴

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
21. **레짐별 동적 피처 파이프라인** — 피처 중요도 역전 대응
22. **Telegram 실제 API 연동** — 스켈레톤 → 실제 전송
