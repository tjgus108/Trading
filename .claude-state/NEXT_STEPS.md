# Next Steps

_Last updated: 2026-05-20 (Cycle 182 B+D+F+SIM 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 182 완료
- 182 mod 5 = 2 → **B(리스크) + D(ML) + F(리서치)** 패턴 ✅

### ⚠️ 핵심 문제: 전략 전부 OOS FAIL

**Cycle 182 시뮬레이션 결과:**
- paper_simulation (1h, 3심볼): BTC 0/22, ETH 0/22, SOL 0/22 PASS
- bundle_oos (4h, 5전략): 5/5 FAIL — OOS Sharpe 붕괴, WFE << 0.50
- 결론: **IS(In-Sample) 과적합 심각. 현재 전략들은 라이브 배포 불가.**

**원인 분석:**
1. IS Sharpe vs OOS Sharpe 극단적 차이 → 파라미터 과적합
2. Walk-Forward 윈도우 2개(179일 데이터)로 통계적 검증력 부족
3. 일부 전략 거래 수 0건 (volume_breakout, price_cluster, dema_cross)
4. 2025-2026 시장 구조 변화 (ETF 효과, 변동성 패턴 변화)에 미적응

### 🎯 Cycle 183 권장 작업 (183 mod 5 = 3 → C+B+F)

#### C(데이터): 데이터 수집 기간 확대 + 피처 재검토
- paper_simulation.py의 데이터 기간을 6개월→12개월로 확대 (Walk-Forward 윈도우 증가)
- 전략들의 신호 발생 빈도 분석 — 거래 0건 전략 원인 파악
- Bybit 4h봉 데이터 수집 안정성 확인

#### B(리스크): 과적합 대응 전략 수립
- IS/OOS 성과 비교 상세 분석 → 과적합 패턴 식별
- WFE 기준 완화 vs 전략 파라미터 범위 축소 vs 정규화 도입 검토
- 전략 파라미터 수 대비 데이터 포인트 비율 확인

#### F(리서치): 과적합 해결 기법 리서치
- Combinatorial Purged Cross-Validation (CPCV) 적용 방안
- 파라미터 안정성 테스트 (sensitivity analysis)
- "Deflated Sharpe Ratio" 적용으로 다중 테스트 보정
- 크립토 특화 과적합 방지 논문/사례

### ✅ Cycle 182 완료 사항

#### B(리스크): Risk Management 검증 ✅ COMPLETE
- CircuitBreaker 플래시크래시 리셋 버그 수정
- KellySizer, DrawdownMonitor, PerformanceMonitor 검증 완료
- PortfolioOptimizer VaR/CVaR 정상

#### D(ML): ML & Signals 검증 ✅ COMPLETE
- RegimeDetector, RegimeStrategyRouter, DriftDetector 전부 프로덕션 양호
- 2봉 연속 확인, ADWIN 이중 게이트, PSI 계산 정확

#### F(리서치): 2025-2026 봇 실패/성공 사례 ✅ COMPLETE
- 73% 봇 6개월 내 손실, 실행 품질 > 신호 품질
- Production 실패 패턴 15가지 정리
- ETF 효과로 BTC 변동성 구조 변화 확인

#### SIM: 시뮬레이션 ✅ COMPLETE (전부 FAIL)
- paper_simulation: 3심볼 × 22전략 = 0 PASS
- bundle_oos: 5전략 전부 FAIL

---

### 📋 Paper Trading 자동화 판정 기준 (Cycle 179 F 리서치 결과)

| 지표 | Go 조건 | No-Go 트리거 |
|------|---------|-------------|
| Profit Factor | ≥ 1.4 | < 1.0 즉시 중단 |
| MDD | ≤ 15% | > 20% 즉시 중단 |
| Sharpe (rolling 4주) | ≥ 0.8 | < 0.3 |
| WFE (OOS/IS 수익 비율) | ≥ 0.50 | < 0.30 |
| 주간 승률 | ≥ 45% | < 30% |

---

### 📊 Strategy Performance Reference (Real Data — ⚠️ IS only, OOS 미검증)

| Strategy | Sharpe | Win% | PF | Trades | MDD | Regime |
|----------|--------|------|-------|--------|-----|--------|
| cmf | 6.85 | 57% | 2.29 | 28 | 4.3% | TREND |
| wick_reversal | 6.51 | 54% | 2.03 | 35 | 3.5% | RANGE |
| volume_breakout | 5.91 | 60% | 2.66 | 15 | 2.2% | TREND |
| elder_impulse | 6.29 | 63% | 2.70 | 16 | 3.5% | TREND |
| value_area | 5.24 | 53% | 1.84 | 30 | 5.0% | RANGE |

**⚠️ 위 수치는 IS(In-Sample) 성과. OOS 검증 시 전략 전부 FAIL.**

---

### 🔧 /schedule 원격 에이전트 설정됨
- 5시간마다 자동 실행 (UTC 0/5/10/15/20시)
- 루틴 ID: trig_0145pyi9PxaqL9fbfd25nzEL
- 관리: https://claude.ai/code/routines/trig_0145pyi9PxaqL9fbfd25nzEL

---

**상태**: Cycle 182 완료 → Cycle 183 C(데이터 확대) + B(과적합 대응) + F(과적합 리서치)
**최우선 과제**: OOS 전략 전부 FAIL → 과적합 해결이 다음 세션 최우선
