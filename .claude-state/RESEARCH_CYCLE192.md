# Cycle 192 Research — 실행 품질(Execution Quality)

_작성일: 2026-05-22_

---

## 1. TWAP vs VWAP 실행 알고리즘 (2024–2026 최신)

### 핵심 차이
- **TWAP**: 시간 균등 분할. 유동성 낮은 페어, 스텔스 실행, 변동성 높은 장에 유리.
- **VWAP**: 거래량 비례 분할. 유동성 안정적인 주요 페어(BTC/ETH)에서 더 유리한 체결가.

### 2024 실전 사례
- 크립토 VC사 Instadapp(INST) 2주 TWAP 실행: VWAP 대비 **7.5% 체결가 개선**, 가스비는 주문액의 0.30% 수준. (출처: [TradingView/CoinTelegraph](https://www.tradingview.com/news/cointelegraph:4e659b29e094b:0-twap-vs-vwap-in-crypto-trading-what-s-the-difference/))
- Dogwifhat $9M 시장가 → $5.7M 슬리피지: TWAP 미사용의 대표적 실패 (Cycle 191에서도 언급).

### 딥러닝 VWAP (arxiv 2502.13722, 2025.02)
- Temporal Linear Network가 거래량 곡선을 직접 최적화 (중간 예측 단계 생략).
- Bitcoin: naive TWAP 대비 절대손실 **25% 개선**, 이차손실 **43% 개선**.
- Ethereum: 손실 0.1778 → 0.1386 (22% 개선).
- ADA/XRP 등 변동성 높은 자산에서도 일관된 아웃퍼폼.
- **핵심 인사이트**: 최적 실행 전략이 반드시 거래량 곡선을 따를 필요 없음 — 가격-거래량 상관관계 존재 시 비균등 배분이 유리.

### Almgren-Chriss 모델 크립토 적용
- 고전 AC 프레임워크를 크립토에 적용: 체결비용 = 스프레드 + 임시충격(Temporary Impact) + 시간리스크.
- Talos가 BTC/ETH 포함 상위 60개 현물/영구선물 계약 대상 실증 모델 구축 (2024.06–2025.07, 5만+ 모 주문, 5천만+ 자 주문).
- Anboto Labs: IS(Implementation Shortfall) 알고리즘에 AC 프레임워크 탑재, 실시간 시장 데이터로 파라미터 업데이트.
- **우리 프로젝트 시사점**: 대형 시장가 주문 시 order splitting 필수. `src/exchange/` 실행 레이어에서 최소 TWAP 분할 구현 검토.

---

## 2. 변동성 기반 포지션 사이징

### EWMA vs GARCH vs 실현변동성

| 모델 | 특징 | 추천 용도 |
|------|------|-----------|
| Simple HV | 단순 평균 | 기준선, 느린 반응 |
| EWMA (λ=0.94) | JP Morgan RiskMetrics 표준. 평균회귀 없음 | 일간~주간 포지션 VaR 입력 |
| GARCH(1,1) | 장기 평균으로 회귀. 이론적으로 우월 | 중기 변동성 예측, 크립토 α=9~37% |
| Realized Vol (ATR) | 실시간 반응, 직관적 | 손절/포지션 크기 실시간 조정 |

### Vol Targeting 효과
- **전략**: 포트폴리오 변동성을 목표치(예: 연 15%)로 고정, 변동성 상승 시 포지션 축소.
- 크립토 레짐 전환이 잦아 단순 고정비율보다 vol scaling이 MDD 제어에 효과적.
- 기관 실전: **Quarter Kelly(풀 켈리의 25%)** 적용. 풀 켈리 대비 변동성 절반, 수익 감소 미미.
- **하이브리드**: Kelly + VIX(또는 실현변동성) 레짐 스케일링 조합이 낮은 변동성 구간에서 MDD 제어 최우수 (arxiv 2508.16598).

### 우리 프로젝트 현황
- 현재 `src/risk/` — 기존 고정 포지션 사이즈 위주. 변동성 연동 스케일링 미구현 여부 확인 필요.
- EWMA(λ=0.94) 또는 20일 ATR 기반 포지션 사이저 추가가 실전 MDD 개선에 직접적 효과 예상.

---

## 3. 트레이딩봇 실패 사례 (실행 관점)

### 레이턴시로 인한 손실
- New York VPS vs London VPS 비교 사례: NYC 평균 75ms 레이턴시 → 지속적 손실. London < 1ms → 수익. (출처: [ForexVPS](https://www.forexvps.net/resources/the-hidden-cost-of-latency-in-trading/))
- HFT 스캘핑 봇: 레이턴시 제어 실패로 전략 자체가 무의미해진 사례 반복 보고.
- **우리 프로젝트**: 스윙/포지션 전략 위주이므로 ms 단위 레이턴시보다 주문 로직 정확성이 더 중요. 단, 시장가 주문 과다 사용 시 슬리피지 누적에 주의.

### 슬리피지 과소평가
- 평균 슬리피지: 정상 시장 0.1–0.6%, 변동성 급등 시 1.5% 초과.
- 소형 코인 시장가 주문: 5–10% 슬리피지 일상적.
- **실전 비용 기준 (2025)**: BTC/USDT 시장가 $10K → 0.1% 미만 / 상위 10개 코인 → 0.05–0.1% / 100위권 밖 → 0.5–2%.
- 백테스트에서 슬리피지를 0으로 가정하면 **실전에서 소매 투자자 기준 0.4% 추가 비용** 발생 (기관 대비).

### 성공 인프라 사례
- 크로스체인 아비트라지 봇: 240,000건/9체인, $868M 볼륨 (Cycle 191). 인프라(낮은 레이턴시) + 자동화가 핵심.
- 기관 실행 차별화: TWAP/VWAP + 아이스버그 주문으로 시장 충격 최소화 → 소매 대비 0.4% 실행 우위.

---

## 4. Paper Trading vs Live Trading 갭

### 주요 차이점

| 항목 | Paper | Live |
|------|-------|------|
| 슬리피지 | 0 또는 미미 | 실제 발생 (0.1–2%) |
| 체결 보장 | 100% | 지정가 미체결 위험 |
| 레이턴시 | 없음 | API 왕복 + 거래소 처리 |
| 심리 | 없음 | 손실 회피 행동 유발 |
| 수수료 | 종종 누락 | 실제 차감 |
| 유동성 | 무한 가정 | 주문창 두께 제한 |

### Paper에서 성공 → Live에서 실패 원인
1. **슬리피지 미반영**: 체결가 가정이 mid-price 기준. 실전은 ask/bid 스프레드 + 충격.
2. **생존 편향(Survivorship Bias)**: 백테스트 기간에 상장폐지/급락한 코인 제외.
3. **과최적화**: 파라미터가 특정 기간 노이즈에 맞춰짐. 일반화 불가.
4. **Look-Ahead Bias**: `shift()`/`rolling()` 오용 — 우리 프로젝트에서 이미 인지된 문제.
5. **레짐 전환**: Paper 기간 상승장 → Live 하락/횡보장으로 전략 무력화.

### Paper→Live 전환 체크리스트 (2025 기준)
- [ ] 30일 이상 안정적 Paper 결과 (Sharpe ≥ 1.0, MDD ≤ 20%)
- [ ] 5% 급락 이벤트 포함 기간에서 Paper 검증
- [ ] 슬리피지 0.1% (BTC) ~ 0.5% (소형코인) 반영한 재백테스트
- [ ] 수수료 0.1% (taker 기준) 포함 손익 재계산
- [ ] API 에러/재시도 로직, 주문 상태 확인 로직 구현 완료
- [ ] 익스포저 한도, 손절 자동화 검증
- [ ] 포지션 사이즈: Paper의 10–25%로 시작, 30–90일 후 스케일업 판단
- [ ] 실전과 Paper의 trade-by-trade P&L 비교 대시보드 구축

### 우리 프로젝트 현황
- `src/backtest/engine.py`: Sharpe ≥ 1.0, MDD ≤ 20%, PF ≥ 1.5, Trades ≥ 15 기준 이미 적용.
- `.claude-state/LIVE_PAPER_REPORT.md` + `live_paper_trader.log` 존재: Paper 트레이딩 인프라 구축됨.
- **갭**: 슬리피지 모델이 백테스트 엔진에 어느 수준으로 반영되어 있는지 추가 점검 필요.

---

## 5. 핵심 시사점 요약

1. **TWAP 분할 실행**: 소형 코인 또는 포지션 크기 > 1일 평균 거래량 0.5% 초과 시 필수. 현재 미구현이면 `src/exchange/` 개선 대상.
2. **슬리피지 현실화**: 백테스트 엔진에 자산별 슬리피지 티어 적용 (BTC: 0.05%, 중형: 0.2%, 소형: 1.0%).
3. **Vol Scaling**: EWMA λ=0.94 기반 포지션 사이저. 고변동성 레짐에서 자동 축소. `src/risk/` 개선 우선순위.
4. **Paper→Live 갭 모니터링**: Live P&L과 Paper 예측값의 괴리를 정기적으로 추적. 10% 이상 지속 괴리 시 슬리피지/레이턴시 원인 분석.
5. **73% 6개월 내 실패** 통계의 공통 원인: 슬리피지 미반영 + 과최적화 + 레짐 전환 대응 부재 — 세 가지 모두 우리 프로젝트의 기존 기준(OOS 검증, 레짐 필터, Trades ≥ 15)이 대응하는 항목.

---

## 참고 자료

- [TWAP vs VWAP in Crypto Trading (CoinTelegraph)](https://www.tradingview.com/news/cointelegraph:4e659b29e094b:0-twap-vs-vwap-in-crypto-trading-what-s-the-difference/)
- [Deep Learning for VWAP Execution in Crypto (arxiv 2502.13722)](https://arxiv.org/html/2502.13722v1)
- [Talos TCA: Execution Insights & Slippage](https://www.talos.com/insights/execution-insights-through-transaction-cost-analysis-tca-benchmarks-and-slippage)
- [Talos Empirical Market Impact Model (June 2024–July 2025)](https://www.talos.com/insights/an-empirical-model-of-market-impact-in-cryptocurrency-trading)
- [Automation Risks: Slippage, Latency, Overfitting (BloFin)](https://blofin.com/en/academy/education/automation-risk-in-crypto-bot)
- [ForexVPS Latency Case Study](https://www.forexvps.net/resources/the-hidden-cost-of-latency-in-trading/)
- [Paper Trading vs Live Trading (Alpaca)](https://alpaca.markets/learn/paper-trading-vs-live-trading-a-data-backed-guide-on-when-to-start-trading-real-money)
- [Bitsgap 12-Point Pre-Launch Checklist](https://bitsgap.com/blog/before-you-launch-a-crypto-trading-bot-12-point-pre-launch-checklist)
- [QuantPedia: Introduction to Volatility Targeting](https://quantpedia.com/an-introduction-to-volatility-targeting/)
- [Kelly Criterion for Crypto (Altrady)](https://www.altrady.com/blog/risk-management/kelly-criterion-crypto-position-sizing)
- [Kelly + VIX Hybrid Sizing (arxiv 2508.16598)](https://arxiv.org/html/2508.16598v1)
- [Optimal Execution in Cryptocurrency Markets (Claremont)](https://scholarship.claremont.edu/cgi/viewcontent.cgi?article=3566&context=cmc_theses)
