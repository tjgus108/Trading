# Next Steps

_Last updated: 2026-04-21 (Cycle 173 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 174
- 174 mod 5 = 4 → **C(데이터) + B(리스크) + F(리서치)** 패턴

### ✅ Cycle 173 완료 사항

#### E(실행): live_paper_trader + Telegram ✅ COMPLETE
- 레짐별 성과 추적 (win/loss/avg_return per regime per symbol)
- 일별 P&L 로깅 + 세션 시작/종료 요약 통계
- Telegram 실연동 (환경변수 기반, 없으면 로깅만)
- 68/68 테스트 PASS

#### A(품질): E2E 통합 테스트 +20개 ✅ COMPLETE
- RegimeFeature E2E 9개 (OOS 과적합 감지, 피처 안정성)
- ML-Backtest 통합 11개 (수수료 영향, equity curve, 다시간)
- 137개 테스트 PASS, regression 없음

#### F(리서치): Bayesian Kelly + 모니터링 ✅ COMPLETE
- Prior α=2, β=3 / fractional 25~33% / 50거래 후 활성화
- Alert 3단계 (Critical/Warning/Info), 수동 개입 코드 명문화

### ⚠️ 핵심 문제: 전략 엣지 부재 → ML 경로

**다음 구현 과제 (우선순위):**
1. ~~FR delta + OI~~ ✅ | ... | 23. ~~레짐별 동적 피처~~ ✅
24. ~~Telegram 실연동~~ ✅ | 25. **Bayesian Kelly 구현** ← 다음 B 사이클
26. **River ADWIN 통합** — 피처 드리프트 실시간 감지 ← 다음 D 사이클
27. **live_paper_trader 7일 운영** — 스크립트 준비 완료, 실행 대기

### Cycle 174 권장 작업 (174 mod 5 = 4 → C+B+F)
- **C(데이터)**: DataFeed → RegimeAwareFeatureBuilder 연결 (end-to-end 파이프라인)
- **B(리스크)**: Bayesian Kelly 구현 (BayesianKellyPositionSizer, α=2/β=3, fractional 0.33)
- **F(리서치)**: River ADWIN 구현 사례, Telegram webhook vs polling, 드리프트 감지 실전
