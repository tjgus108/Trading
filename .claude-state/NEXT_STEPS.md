# Next Steps

_Last updated: 2026-04-21 (Cycle 174 완료)_

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

### ⚠️ 핵심 문제: 전략 엣지 부재 → ML + 레짐 스위칭

**다음 구현 과제 (우선순위):**
1. ~~BayesianKelly~~ ✅ | ~~DataFeed E2E~~ ✅ | ~~Telegram 실연동~~ ✅
2. **River ADWIN 통합** — 이중 게이트(피처+모델출력), delta=0.05 ← 다음 D 사이클
3. **Regime Switcher** — 레짐별 전략 로테이션 활성화 (4~5x 거래 증가)
4. **Live 7일 운영** — live_paper_trader + regime rotation ← 다음 E 사이클
5. **Bayesian Kelly → live 통합** — warmup 후 자동 활성화

### Cycle 175 권장 작업 (175 mod 5 = 0 → D+E+F)
- **D(ML)**: River ADWIN 드리프트 감지 구현 (delta=0.05, 이중 게이트)
- **E(실행)**: live_paper_trader 7일 운영 개시, BayesianKelly 통합
- **F(리서치)**: 레짐 기반 전략 로테이션 성공 사례, walk-forward + regime 논문
