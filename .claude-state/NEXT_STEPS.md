# Next Steps

_Last updated: 2026-04-21 (Cycle 175 D+E완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 175
- 175 mod 5 = 0 (=5) → **D(ML) + E(실행) + F(리서치)** 패턴

### ✅ Cycle 174 완료 사항

#### B(리스크): BayesianKellyPositionSizer ✅ COMPLETE
- Beta prior (α=2, β=3), fractional 0.33, warmup 50거래
- Kelly formula + max_fraction 10% 상한
- 23개 테스트 추가, 54/54 PASS

#### C(데이터): DataFeed→RegimeFeature E2E ✅ COMPLETE
- fetch_with_regime(), build_with_cached_regime() 구현
- 16개 통합 테스트, 64/64 PASS

#### SIM: 레짐 스위칭 가능성 분석 ✅ COMPLETE
- 77% PASS 전략이 실데이터 거래수 미달 → 레짐 스위칭 4~5x 증가 가능
- Trend followers(Sharpe 5.77), Breakout(PF 2.41), Adaptive(cmf Sharpe 6.85)

#### F(리서치): ADWIN + Telegram ✅ COMPLETE
- ADWIN delta=0.05~0.1, 이중 게이트 패턴, warm start 재학습
- Telegram 즉시/큐 분리, token bucket 25msg/s

### ✅ Cycle 175 완료 사항

#### D(ML): ADWIN 드리프트 감지 ✅ COMPLETE
- ADWINDriftDetector + DualGateADWINMonitor, delta=0.05, 29 tests PASS

#### E(실행): BayesianKelly → live_paper_trader 통합 ✅ COMPLETE
- BayesianKellyPositionSizer 통합: warmup 50거래 → 자동 Bayesian Kelly 활성화
- warmup_fraction=0.005 (기존 RISK_PER_TRADE와 동일), max_fraction=0.10
- BK 사이즈 = min(bk_size, atr_size, max_size) — ATR 상한으로 안전장치
- 거래 결과(PnL) → posterior 실시간 업데이트 (alpha/beta)
- 상태 저장/복원: bayesian_kelly_state (JSON) — 세션 재시작 시 posterior 유지
- 에러 복구 개선: 연속 tick 에러 5회 → 상태 저장 + 5분 대기, 데이터 페치 실패 카운터
- BK 상태를 세션 요약 + 24시간 리포트에 표시
- 13개 통합 테스트 추가, 전체 PASS (기존 54+58 테스트 불변)

### ⚠️ 핵심 문제: 전략 엣지 부재 → ML + 레짐 스위칭

**다음 구현 과제 (우선순위):**
1. ~~BayesianKelly~~ ✅ | ~~DataFeed E2E~~ ✅ | ~~Telegram 실연동~~ ✅
2. ~~**River ADWIN 통합**~~ ✅ | ~~**BayesianKelly → live 통합**~~ ✅
3. **Regime Switcher** — 레짐별 전략 로테이션 활성화 (4~5x 거래 증가)
4. **Live 7일 운영** — live_paper_trader 실운영 개시 (BK + ADWIN 탑재 완료)

### Cycle 176 권장 작업 (176 mod 5 = 1 → A+B+C)
- **A(전략)**: 레짐 스위처 구현 (레짐별 전략 풀 로테이션)
- **B(리스크)**: BayesianKelly + DrawdownMonitor MDD step-down 연동
- **C(데이터)**: 실시간 데이터 파이프라인 안정성 개선
