# Cycle 173 Research: Bayesian Kelly 구현 사례 + Live Trading 모니터링

Date: 2026-04-21

---

## 1. Bayesian Kelly Criterion — Beta 분포 구현

### 핵심 메커니즘

Beta 분포 켤레 사전 분포(conjugate prior)를 이용한 베이지안 업데이트:

- 초기 파라미터: α (win count), β (loss count)
- 상승일: α ← α + 1
- 하락일: β ← β + 1
- 승률 추정: p = α / (α + β) — Beta 분포의 평균값

Kelly 포지션 크기 공식:
```
f* = (p × b - q × L) / (b × L)
```
- p = 추정 승률, q = 1-p
- b = 기대 이익률, L = 기대 손실률
- 실전에서는 Fractional Kelly 적용: f_actual = clip(f*, -1, 1) × kelly_fraction (0.25~0.50)

### 사전 분포 선택 (Prior Selection)

| 유형 | 초기값 | 특성 | 적합 케이스 |
|------|--------|------|-------------|
| Uninformative (균등) | α=1, β=1 | 최대 불확실성, 데이터 주도 | 신규 전략, 검증 데이터 없음 |
| Weakly Informative | α=2, β=3 | 약한 사전 편향 | 유사 전략 과거 성과 참고 가능 |
| Informative (베어리시) | α=1, β=4 | 20% 승률 가정 | 크립토 하락장 bias 반영 |

**결론**: Weakly Informative prior (α=2, β=3) 권장 — 완전 균등 prior는 초기 과도한 포지션 위험, 강한 편향 prior는 초기 데이터 부족 시 수렴 느림.

### 업데이트 빈도 (Update Frequency)

- **매 거래 업데이트**: 소자본 고빈도에 적합, 파라미터 진동 위험 있음
- **일별 배치**: 안정적, 스윙/데이 트레이딩 적합 (Medium 사례)
- **소자본 권고**: 일별 업데이트 + 최소 30거래 이후 Kelly 신뢰 구간 활용

### 소자본 실전 적용 핵심

1. **Prior 선택이 결과를 지배**: 잘못된 prior → Sharpe -1.91 vs 올바른 prior → Sharpe +1.07 (사례)
2. **Fractional Kelly 필수**: 이론값의 25-50%만 사용 (Kelly는 최적이지만 추정 오차에 민감)
3. **수렴 지점**: α+β >= 50 이후부터 posterior가 prior 영향 벗어남 → 최소 50거래 필요
4. **Alpha 붕괴 감지**: 20거래 rolling win rate가 prior 평균의 50% 이하면 전략 재검토

### 관련 논문

Browne & Whitt (1996) "Portfolio Choice and the Bayesian Kelly Criterion" — Columbia Business School. Natural conjugate prior 분석으로 Beta 분포가 수학적으로 최적의 conjugate prior임을 증명. Limiting diffusion이 rescaled Brownian motion으로 수렴.

---

## 2. Live Trading 모니터링 — 실패 패턴 및 Best Practices

### 흔한 실패 패턴

#### Alert Fatigue (알림 피로)
- **증상**: 너무 많은 알림 → 중요 신호 무시 → 중요한 MDD 초과를 놓침
- **수치**: 세션당 3-5개 이상 알림 조건은 집중력 저하 초래
- **해결**: 3단계 알림 계층화
  1. Critical: MDD 임계값 초과, 거래 실행 오류
  2. Warning: Rolling Sharpe 급락, fill rate 이상
  3. Info: 일별 PnL 요약 (알림 아닌 리포트로)

#### 과도한 수동 개입 (Over-Intervention)
- **증상**: 2% drawdown에 봇 수동 종료 → 평균 68% 자본 손실 (케이스 스터디)
- **원인**: 감정적 판단이 알고리즘보다 느리고 편향됨
- **해결**: 개입 규칙을 코드로 명문화 (MDD > X% 이면 자동 halt, 그 이하는 개입 금지)

#### 잘못된 메트릭 추적
- **증상**: 단순 PnL만 추적 → Sharpe/MDD 악화를 놓침
- **증상**: 절대 PnL 추적 → 포지션 크기 변화에 따른 왜곡

### 핵심 모니터링 메트릭

| 메트릭 | 수집 주기 | Critical 임계값 | Warning 임계값 |
|--------|-----------|-----------------|----------------|
| Rolling PnL (7d) | 1h | -5% | -2% |
| Rolling Sharpe (30d) | 1d | < 0.5 | < 1.0 |
| Max Drawdown | 1h | > 15% | > 10% |
| Fill Rate | 매 주문 | < 85% | < 93% |
| Signal Latency | 매 신호 | > 5s | > 2s |
| Win Rate (20 rolling) | 매 거래 | < prior의 50% | < prior의 70% |

### 경보 임계값 설정: 동적 vs 정적

**정적 임계값**: 단순, 낮은 유지 비용
- 적합: MDD (절대 자본 보호), fill rate (인프라 이슈)
- 예: MDD > 15% → 즉시 halt

**동적 임계값**: 시장 상황 반영
- 적합: Rolling Sharpe, PnL 경보
- 예: ATR 기반 stop-loss, 변동성 조정 포지션 크기
- 권고: Bollinger-like 방법 — 20일 평균 ± 2σ 로 동적 경보

**권고**: MDD/Fill Rate은 정적, Sharpe/PnL은 동적 임계값 사용

### Dashboard 설계 패턴

**Freqtrade + Grafana + Prometheus** 오픈소스 스택이 검증된 패턴:
- GitHub: `thraizz/freqtrade-dashboard`
- 데이터베이스: InfluxDB/TimescaleDB (OHLCV), Prometheus (인프라 메트릭)
- RED 방법론 적용: Rate(거래 빈도), Errors(오류율), Duration(레이턴시)

**레이아웃 권고**:
```
Row 1 (Critical): Current Equity | Rolling MDD | Fill Rate | Latency
Row 2 (Performance): Rolling Sharpe (30d) | Win Rate (20-trade) | PF
Row 3 (Detail): Trade History | Per-Strategy PnL | Position Heatmap
```

---

## 3. 핵심 인사이트 요약

- **Prior 선택이 Bayesian Kelly의 핵심 리스크**: Uninformative prior (α=β=1)는 안전해 보이지만 초기 데이터 부족 시 과도한 포지션 유발. Weakly informative (α=2, β=3) 권장.

- **Fractional Kelly 25-50%가 실전 표준**: 이론 Kelly는 추정 오차에 지수적으로 민감. 소자본에서는 25-33%가 파산 위험을 실질적으로 0에 가깝게 낮춤.

- **알림 계층화 없이는 Alert Fatigue 불가피**: Critical/Warning/Info 3단계 구분하고, 세션당 Critical 알림은 3-5개 이내로 제한. 나머지는 일별 리포트로 대체.

- **수동 개입 규칙을 코드로 명문화**: "MDD > 15% 자동 halt" 같은 기계적 규칙 외의 개입은 평균적으로 성과를 악화시킴 (케이스 스터디: 68% 자본 손실 패턴).

- **최소 50거래 이전에는 Bayesian Kelly 신뢰 불가**: α+β < 50 구간에서는 prior 영향이 dominant. 이 기간엔 고정 소액 포지션으로 데이터 수집에 집중.

---

## 참고 자료

- [Bayesian Kelly: A Self-Learning Algorithm for Power Trading (Medium)](https://medium.com/@jlevi.nyc/bayesian-kelly-a-self-learning-algorithm-for-power-trading-2e4d7bf8dad6)
- [Portfolio Choice and the Bayesian Kelly Criterion — Browne, Columbia (PDF)](https://business.columbia.edu/sites/default/files-efs/pubfiles/6343/bayes_kelly.pdf)
- [33 Critical Lessons from Failure: Building a Profitable Trading Bot](https://gov.capital/33-critical-lessons-from-failure-building-a-profitable-trading-bot-that-actually-works/)
- [Crypto Trading Bot Pitfalls to Avoid 2025](https://en.cryptonomist.ch/2025/08/22/crypto-trading-bot-pitfalls/)
- [Algorithmic Trading Monitoring and Management — ION Group](https://iongroup.com/blog/markets/algorithmic-trading-monitoring-and-management/)
- [Freqtrade Grafana Dashboard (GitHub)](https://github.com/thraizz/freqtrade-dashboard)
- [AI Trading Bot Risk Management Guide 2025 — 3Commas](https://3commas.io/blog/ai-trading-bot-risk-management-guide-2025)
- [Performance Metrics for Algorithmic Trading — uTrade Algos](https://www.utradealgos.com/blog/5-key-metrics-to-evaluate-the-performance-of-your-trading-algorithms)
