# Research Log

## [2026-04-11] Cycle 1 Research

### 신규 실패 사례

- **October 2025 암호화폐 청산 연쇄 붕괴** / 2025-10-10 / 원인: 50~100x 레버리지 봇들의 자동청산이 연쇄 반응 유발, 60초 안에 $3.21B 증발, 14시간 총 $19B 청산. 스프레드 1,321x 폭등, 호가창 깊이 98% 소실. 봇들이 비정상 변동성 시 멈추지 않고 계속 매도 집행 / 교훈: 일일 3% 드로다운 서킷브레이커 필수, 레버리지 포지션 규모 엄격 제한 / 출처: https://blog.amberdata.io/how-3.21b-vanished-in-60-seconds-october-2025-crypto-crash-explained-through-7-charts

- **May 2025 AI 봇 플래시 크래시 가속** / 2025-05 / 원인: 정상 시장 조건용으로 설계된 AI 봇들이 갑작스러운 변동성에 적응 못하고 2분 안에 $2B 자산 매도. 레짐 감지 로직 부재 / 교훈: 변동성 레짐 필터(VIX/ATR 기반) 없이 단일 전략 운영 금지 / 출처: https://www.crypto-reporter.com/press-releases/most-crypto-trading-bots-promised-easy-money-the-market-killed-them-here-is-what-the-survivors-built-instead-123004/

- **OKX 토큰 50% 플래시 크래시** / 2024-01-23 / 원인: 청산 연쇄로 단시간 50% 폭락, 얕은 유동성에서 대형 봇 매도가 slippage 폭발적 확대 유발 / 교훈: 저유동성 자산에서의 포지션 크기는 시장 깊이(depth) 대비 최대 0.1% 이하로 제한 / 출처: https://www.coindesk.com/business/2024/01/23/crypto-exchange-okxs-token-suffers-50-flash-crash-amid-liquidation-cascade

- **2024~2025 암호화폐 봇 73% 6개월 내 실패** / 2024~2025 / 원인: CoinGecko 연구에 따르면 13.4M 프로젝트 중 53.2% 소멸. 자동화 거래 계좌의 73%가 6개월 내 실패, 52%는 3개월 내 실패. 주요 원인: 리스크 관리 부재, 과최적화, 레짐 변화 무대응 / 교훈: 출시 전 최소 3개 시장 레짐(상승/하락/횡보)에서 walk-forward 검증 필수 / 출처: https://awards.finance-monthly.com/do-trading-bots-fail/

---

### 신규 성공 사례

- **AutoPilot Trader V3 (2024~2025)** / 조건: 1,045개 백테스트 트레이드, 다중 거래소(Binance, Bybit, 3개 DEX) 24/7 운영 / 성과: Sharpe 3.58, 연환산 42% 수익, MDD 9% / 교훈: 다중 거래소 분산 + 낮은 레버리지 + 엄격한 포지션 사이징(1% 룰)의 조합이 핵심 / 출처: https://redhub.ai/ai-trading-bots-2025/

- **SuperTrend AI 봇 (2024-01~2025-01)** / 조건: AI 기반 SuperTrend 전략, 111개 트레이드 / 성과: 순이익 95.94%, Sharpe 0.558(양의 위험조정 수익). 주의: Sharpe가 낮아 리스크 대비 수익 효율은 중간 / 교훈: 높은 절대 수익이라도 Sharpe < 1.0이면 변동성 대비 수익이 불안정함을 의미, 백테스트 지표 종합 판단 필요 / 출처: https://www.researchgate.net/publication/388448293_Algorithmic_Trading_Bot_Using_Artificial_Intelligence_Supertrend_Strategy

- **ML 기반 다중 레짐 전략 (2024~2025 기관급)** / 조건: 머신러닝 모델, 상승/하락/횡보 3개 레짐 대응 / 성과: Sharpe 2.5 이상 유지, 업계 평균(1.0~2.0)을 크게 상회 / 교훈: 레짐 전환 감지 + 전략 스위칭이 일관된 성과의 핵심 / 출처: https://redhub.ai/ai-trading-bots-2025/

---

### 최신 리스크 관리 기법 (2024~2025)

- **다층 서킷브레이커**: 일일 드로다운 3% + 주간 7% 초과 시 자동 거래 중단
- **변동성 기반 포지션 사이징**: ATR/VIX 기반으로 포지션 크기를 동적 조정, 고변동성 시 축소
- **Kelly Criterion 적용**: 포트폴리오 노출 6% 이하, 단일 트레이드 1% 이하
- **ADL(Auto-Deleveraging) 회피**: 거래소의 강제 청산 메커니즘 분석 후 청산가격 완충 설정
- **레짐 감지 필터**: 추세/횡보/고변동성 레짐 구분 후 전략 전환 또는 일시 중단

---

### 우리 봇에 적용 가능한 개선점 3개

1. **다층 서킷브레이커 구현**: `src/risk/` 에 일일 드로다운 3%, 주간 7% 초과 시 자동 중단 로직 추가. October 2025 사태처럼 봇이 폭락 중 계속 매도하는 사태 방지.

2. **변동성 레짐 필터**: ATR(14) 기준 고변동성 감지 시 포지션 크기를 50% 자동 축소하거나 BUY 신호를 억제하는 레짐 레이어를 `src/strategy/base.py` 또는 `src/risk/` 에 추가. May 2025 AI 봇 플래시 크래시 가속 방지.

3. **슬리피지/유동성 검증 강화**: 백테스트 엔진에 호가창 깊이(market depth) 기반 슬리피지 시뮬레이션 추가. OKX 사례처럼 저유동성에서의 대형 포지션은 실제 체결가가 백테스트와 크게 달라짐.

---

### 참고 자료

- https://blog.amberdata.io/how-3.21b-vanished-in-60-seconds-october-2025-crypto-crash-explained-through-7-charts
- https://www.ainvest.com/news/october-2025-crypto-crash-19b-leverage-liquidation-event-2602/
- https://aurpay.net/aurspace/crypto-crash-october-2025-bitcoin-liquidation-explained/
- https://www.soliduslabs.com/post/when-whales-whisper-inside-the-20-billion-crypto-meltdown
- https://www.crypto-reporter.com/press-releases/most-crypto-trading-bots-promised-easy-money-the-market-killed-them-here-is-what-the-survivors-built-instead-123004/
- https://www.coindesk.com/business/2024/01/23/crypto-exchange-okxs-token-suffers-50-flash-crash-amid-liquidation-cascade
- https://awards.finance-monthly.com/do-trading-bots-fail/
- https://redhub.ai/ai-trading-bots-2025/
- https://www.researchgate.net/publication/388448293_Algorithmic_Trading_Bot_Using_Artificial_Intelligence_Supertrend_Strategy
- https://3commas.io/blog/ai-trading-bot-risk-management-guide-2025
- https://www.luxalgo.com/blog/risk-management-strategies-for-algo-trading/

---

## [2026-04-11] Cycle 2 — Risk Management Deep Dive

### 드로다운 관리 기법

- 프로 퀀트 펀드 표준: soft limit = 연간 변동성의 1배(포지션 축소), hard limit = 1.5배(트레이딩 중단). 2단계 에스컬레이션 구조.
- 프랍 펌 실무(2025): 일일 3~5% / MDD 6~10%가 가장 보편적. QT Prime은 일일 4% / MDD 10%, QT Instant는 일일 3%로 더 타이트.
- Equity Protector 개념: 단일 트레이드 부동손실 1.5% 초과 시 모든 포지션 자동 청산 — 포지션 레벨 안전장치.
- Apex 방식(EOD trailing drawdown): 일별 한도 없이 누적 하이워터마크 기준 trailing MDD 통제 — 단기 변동성은 허용하되 누적 손실만 제한.
- **우리 봇 적용 가능**: `src/risk/` 에 일/주/월 3단계 DD 한도 + 자동 포지션 축소 로직 추가. Cycle 1에서 다층 서킷브레이커를 개선점으로 식별했고, 이번 리서치로 구체적 수치(일 3~5%, MDD 6~10%) 근거 확보.

### ATR 변동성 스케일링

- 기본 공식: `포지션 크기 = (계좌 자산 × 위험%) / (ATR × 멀티플라이어)`. ATR 상승 = 포지션 자동 축소.
- **함정 1 — ATR 절대값 오해**: ATR $5는 $100 주식에서 5% 변동성이지만 $500 주식에서는 1%. 반드시 `ATR / 현재가` 비율로 정규화해야 함. 크립토 자산 간 비교 시 특히 중요.
- **함정 2 — 방향성 혼동**: ATR은 방향 지표가 아님. ATR 상승 = 변동성 확대일 뿐, 매수/매도 신호 아님. 방향성 지표와 반드시 결합해야 하며, 2025년 백테스트에서 조합 전략이 단독 대비 수익성 34% 향상.
- **함정 3 — 극단 변동성 시 파라미터 고정**: ATR(14) 단기 파라미터는 극단 구간에서 과민 반응. 고변동성 레짐 진입 시 ATR(20~30)으로 전환 필요.
- **함정 4 — 손절과 사이징 불일치**: 포지션 크기와 손절 위치를 ATR로 동시 계산해야 정합성 유지. 손절만 ATR 기반이고 사이징은 고정이면 실제 리스크가 계획과 달라짐.

### Kelly Criterion 함정

- **Full Kelly 실전 위험**: 승률/손익비 추정 오차가 조금만 있어도 MDD 50% 초과 빈발. 이론 최적이지만 실전에서는 파산 경로.
- **Half Kelly 권장**: 성장률을 Full Kelly의 약 75% 수준으로 유지하면서 변동성/파산위험 대폭 감소. 추정 불확실성에 대한 버퍼 역할. 학계와 실무 모두 Half Kelly 이하를 표준으로 채택.
- **바이너리 아웃컴 가정의 한계**: Kelly 원식은 이기거나 지거나 2가지만 가정하지만, 실제 트레이딩은 부분 청산/슬리피지/연속 손실 등 연속 분포 아웃컴. 이 가정 위반 시 Kelly가 과대 베팅 유도.
- **2024~2025 실전 권장**: Risk-Constrained Kelly(이분법 알고리즘으로 최대 DD 제약 조건 추가) 또는 Bayesian 업데이팅 방식이 주목받음. 실무에서는 Quarter Kelly(×0.25) 또는 고정 분수(포트폴리오 1~2%)가 더 안전. 추정 불확실성이 클수록 분수를 줄일 것.

### 참고 자료

- [Drawdown Management — QuantifiedStrategies](https://www.quantifiedstrategies.com/drawdown/)
- [Legacy Evaluation Rules — Apex Trader Funding](https://support.apextraderfunding.com/hc/en-us/articles/31519769997083-Legacy-Evaluation-Rules)
- [QT Prime Rules 2025 — FundedTrading](https://fundedtrading.com/qt-prime-trading-challenge-rules/)
- [ATR Position Sizing — ChartingPark](https://chartingpark.com/articles/volatility-based-position-sizing-atr/)
- [Volatility-Based Position Sizing — QuantifiedStrategies](https://www.quantifiedstrategies.com/volatility-based-position-sizing/)
- [ATR Strategy Guide 2025 — QuantStrategy.io](https://quantstrategy.io/blog/using-atr-to-adjust-position-size-volatility-based-risk/)
- [Kelly Criterion in Algo-Trading — ALGOGENE](https://algogene.com/community/post/175)
- [Risk-Constrained Kelly Criterion — QuantInsti](https://blog.quantinsti.com/risk-constrained-kelly-criterion/)
- [Fractional Kelly & Uncertainty — Matthew Downey](https://matthewdowney.github.io/uncertainty-kelly-criterion-optimal-bet-size.html)


## [2026-04-11] Cycle 3 — Execution Research (SKIPPED)

F 에이전트가 WebSearch 타임아웃(30분+)으로 실행 완료하지 못함.
Cycle 4에서 Execution 주제 포함해 리서치 강화 필요:
- 거래소별 실측 슬리피지 (Binance, OKX, Bybit)
- Paper → Live 전환 함정 체크리스트
- TWAP/VWAP 최신 개선 기법 (2024-2025)


## [2026-04-11] Cycle 4 — Brief Research

### 2025 스트레스 이벤트

- October 10, 2025 (10/10): $19B 청산, 60초 내 $3.21B 소멸. 트럼프 관세 발표 + 기술적 매도가 겹친 매크로 충격이 트리거.
- November 21, 2025: $2B 24시간 청산. ETF 자금 유출이 유동성을 빼앗으며 지지선 붕괴 → 자동 청산 연쇄. October보다 규모 작지만 동일한 메카니즘.
- 2025년 연간 총 ~$150B 청산. 대부분 정상 흡수됐으나 October/November 두 구간에서 인프라 한계 노출.
- 공통 특징: 중형~소형 알트코인에서 롱 레버리지 집중 → 유동성 얕은 구간에서 청산 증폭.

### 실측 슬리피지 (Binance/OKX)

- Binance 선물: 일일 $40B+ 거래량으로 업계 최대 유동성. BTC/ETH 대형 페어 기준 정상 시장에서 슬리피지 ~1~5 bps 수준(추정). 대형 기관 주문에도 스프레드 타이트.
- OKX: Binance 대비 유동성 낮으나 봇 생태계 우수. 슬리피지는 정상 시장에서 Binance와 유사하나 중소형 페어에서 확대.
- 정량 수치 한계: 2025년 실측 bps 데이터는 공개 출처에서 확인 불가. 거래소들이 TWAP/알고 주문을 권장하는 것이 간접 증거 — 시장가 주문 슬리피지가 무시 못할 수준임을 시사.
- 실무 권고: 시장가 주문 대신 Limit/TWAP 사용, 포지션 크기를 호가창 깊이의 0.1% 이하로 제한(Cycle 1 교훈 재확인).

### 참고

- [October 2025 Crash — Amberdata](https://blog.amberdata.io/how-3.21b-vanished-in-60-seconds-october-2025-crypto-crash-explained-through-7-charts)
- [November 2025 Wipeout — Yahoo Finance](https://finance.yahoo.com/news/crypto-market-wipeout-2b-24-160816131.html)
- [Binance vs OKX Liquidity — Bitcompare](https://bitcompare.net/post/binance-vs-okx)


## [2026-04-11] Cycle 5 — Ensemble Strategies

### 앙상블 실전 성과 (2024-2025)

- ACM ICAIF FinRL 2023/2024 대회: 앙상블이 단일 에이전트보다 누적 수익·Sharpe 모두 우세. Sharpe 기중 앙상블 방식이 최고 성과.
- PLS/FFN/GRBT 앙상블 평균 예측: Sharpe 1.20+ 달성, 단일 모델 대비 일관되게 우위.
- 메타-러닝 앙상블(OGU/Fast Universalization): Sharpe 1.26 수준 — 자본을 고성능 포트폴리오에 동적 배분하는 방식이 핵심.
- 2026년 1월 기준 6전략 앙상블 실사례: 주간 +1.3%, YTD +1.5%, MDD 0% — 낮은 드로다운이 단일 전략 대비 가장 두드러진 차이.

### 앙상블 함정

- **과적합 위험 증폭**: 90%의 크립토 전략이 과적합 상태. 앙상블은 구성 전략 수가 많을수록 백테스트 Sharpe가 좋아 보이지만 live에서 일제히 실패할 수 있음. Win rate 80%+, PF 4.0+ 신호면 과적합 의심.
- **상관관계 붕괴**: 역사적 낮은 상관관계를 가정하고 조합한 전략들이 시장 스트레스 구간(예: October 2025)에서 동시에 같은 방향으로 손실 — "다양화 환상(diversification illusion)".
- **훈련 비용과 적응 지연**: 앙상블 훈련 시간이 선형 증가, 변동성 큰 크립토 시장에서 빠른 레짐 변화에 재적응 어려움. 복잡성 대비 실익을 반드시 검증해야 함.
- **샘플링 병목**: FinRL 앙상블은 다양한 에이전트 확보를 위해 대규모 시뮬레이션 환경 필요 — 소규모 팀/봇에서 현실적 구현 장벽.

### 우리 봇 적용 인사이트

- 현재 STRATEGY_REGISTRY에 등록된 전략들을 앙상블화할 때, Sharpe 가중 방식(각 전략의 최근 N일 Sharpe에 비례해 신호 가중)이 단순 다수결보다 우수.
- Walk-forward validation 없이 앙상블 구성 전략 선택 금지 — 백테스트 Sharpe가 높아도 OOS 성과 확인 필수.
- 스트레스 구간 상관관계 사전 검증: 정상 시장이 아닌 고변동성 구간(ATR spike)에서 전략 간 상관관계가 0.7 이상이면 앙상블 효과 없음으로 판단.

### 참고

- [FinRL Ensemble 2023/2024 — arXiv](https://arxiv.org/html/2501.10709v1)
- [Ensemble Deep RL for Trading — Springer](https://link.springer.com/chapter/10.1007/978-3-031-61037-0_9)
- [Overfitting in Crypto Strategies — TrendRider](https://trendrider.net/blog/how-to-avoid-overfitting-crypto-trading)


## [2026-04-11] Cycle 6 — Regime Detection Pitfalls

### 레짐 감지 실전 함정

- **전환 지연(Lag)**: HMM은 충분한 관측값이 쌓여야 레짐 전환을 확정 — 이미 절반이상 움직인 뒤에 신호가 나옴. 고빈도 크립토에서 치명적.
- **상태 수 결정 문제**: 너무 많으면 노이즈를 레짐으로 학습(과적합), 너무 적으면 전환을 못 잡음. AIC/BIC 기준도 주관성 완전히 제거 불가.
- **정규분포 가정 위반**: HMM 내부는 수익률이 정규 분포라고 가정하지만, 크래시(October 2025 등) 시 팻테일 발생 → 레짐 분류 오작동.
- **Markov 가정 한계**: 미래 상태가 오직 현재 상태에만 의존한다고 가정 — 장기 기억(momentum) 구간이 많은 크립토에서 구조적으로 맞지 않음.
- **OOS 성능 붕괴**: 훈련 기간에 없는 새 레짐(예: 기관 ETF 유입 이후 구조 변화)에서 모델이 기존 레짐으로 잘못 분류.

### 크립토 특화 주의점

- **레짐 지속 시간이 극단적으로 짧음**: 주식 시장 기준으로 설계된 HMM은 크립토의 며칠 단위 급등락을 하나의 안정적 레짐으로 처리하지 못함.
- **외생 변수 선택 어려움**: 볼륨·온체인 지표 등이 크립토 레짐에 영향을 미치지만, 2024년 이후 기관 ETF 거래량이 지배하면서 기존 온체인 변수의 예측력이 약화.
- **변동성 클러스터링 + 레짐 혼동**: GARCH 기반 변동성 클러스터링은 레짐 전환이 아닌 단순 ATR 스파이크를 레짐 변화로 오인하게 만들 수 있음 — 레짐 레이블 신뢰도 훼손.

### 참고

- [Regime Switching Forecasting for Cryptos — Springer Digital Finance](https://link.springer.com/article/10.1007/s42521-024-00123-2)
- [HMM Market Regime Pitfalls — QuantifiedStrategies](https://www.quantifiedstrategies.com/hidden-markov-model-market-regimes-how-hmm-detects-market-regimes-in-trading-strategies/)
- [Bitcoin HMM Analysis 2024-2026 — Preprints.org](https://www.preprints.org/manuscript/202603.0831)


## [2026-04-11] Cycle 7 — Feature Importance Pitfalls

### 피처 중요도 함정

- **Gini Importance 편향**: RF의 기본 Gini 중요도는 고유값 수가 많은 피처(가격, 거래량 등 연속형)를 과대평가. 크립토에서 price/volume 피처가 항상 상위에 나타나는 이유 — 실제 예측력이 아닌 수치적 아티팩트.
- **다중공선성 분산**: 상관 피처들(EMA5/EMA10/EMA20 등)이 있으면 RF/XGBoost가 중요도를 임의로 쪼개서 배분 → 어떤 피처가 진짜 중요한지 판단 불가. SHAP은 Shapley 값으로 공정하게 분배하지만 계산 비용이 큼.
- **제거 검증 필수**: 상위 중요도 피처를 실제로 제거했을 때 성능이 오히려 오르면 피처 누수 의심. 진짜 중요 피처는 제거 시 성능이 유의미하게 하락해야 함.
- **SHAP 실전 한계**: 트리 SHAP은 빠르지만, 피처 상호작용이 복잡한 크립토 시계열에서 인과관계가 아닌 상관관계를 설명한다는 점 주의. SHAP 높다 ≠ 인과 피처.

### 크립토 피처 누수 주의

- **Look-ahead bias**: 이동평균·RSI 등을 `shift()`없이 계산하면 당일 종가가 당일 신호에 사용됨. 반드시 `df['feature'].shift(1)`로 하루 지연 처리.
- **스케일러/인코더 전체 데이터 fit 금지**: 전체 데이터로 StandardScaler fit 후 train/test 분리 → 미래 통계가 과거 학습에 누수. 반드시 train 구간에서만 fit, test에는 transform만 적용.
- **Purged Cross-Validation**: 일반 K-Fold는 시계열에서 인접 샘플 간 누수 발생. 크립토처럼 자기상관이 강한 데이터에서는 시간 기반 분리 + embargo 기간(예: 5바) 설정 필수.

### 참고

- [Backtesting AI Crypto Safely — Blockchain Council](https://www.blockchain-council.org/cryptocurrency/backtesting-ai-crypto-trading-strategies-avoiding-overfitting-lookahead-bias-data-leakage/)
- [Look-Ahead Bias in ML Trading — MarketCalls](https://www.marketcalls.in/machine-learning/understanding-look-ahead-bias-and-how-to-avoid-it-in-trading-strategies.html)
- [Purged Cross-Validation — Wikipedia](https://en.wikipedia.org/wiki/Purged_cross-validation)


## [2026-04-11] Cycle 8 — Sortino vs Sharpe

### 실전 비교
- Sharpe는 상승 변동성까지 리스크로 계산해 강한 상승장 전략을 과소평가한다. Sortino는 하방 변동성만 분리하므로 비대칭 수익 구조를 가진 전략의 실제 효용을 더 정확히 반영.
- 둘 중 하나만 보면 안 됨. 두 지표를 같이 제시했을 때 Sortino > Sharpe면 상승 변동성이 큰 전략, Sortino ≈ Sharpe면 수익 분포가 대칭에 가까운 전략으로 해석.
- 백테스트 엔진의 현재 Sharpe >= 1.0 기준은 그대로 유지하되, Sortino도 추가 리포팅하면 전략 성격을 더 명확히 파악 가능.
- 실전 사례: BTC의 Sortino(1.86)가 Sharpe의 거의 2배 — 상승 변동성이 크게 기여. Trend 전략 Sortino 3.83 vs BTC Sortino 1.93으로 전략이 순수 하방 리스크 대비 2배 효율.

### 크립토 적용
- 크립토는 정상적으로 양의 비대칭(positive skew) 분포를 보임. Sharpe는 이 상승 꼬리(upside tail)를 페널티로 계산 → 크립토 전략의 리스크 조정 성과를 구조적으로 낮춰 보임.
- 따라서 크립토 전략 평가에서 Sortino가 더 대표성 있는 지표. 단, MAR(최소 수용 수익률) 설정에 따라 Sortino 수치가 크게 달라지므로 MAR을 명시하지 않은 Sortino 비교는 의미 없음.
- 권장: MAR = 0(또는 무위험 금리)으로 고정하고, 전략 간 비교 시 동일 MAR 사용.

### Sortino 계산 흔한 실수
- **MAR 불일치**: 수익률은 일 단위인데 MAR은 연간값 그대로 사용 → 하방 편차가 과소/과대 계산됨. 반드시 수익률 주기와 동일한 단위로 MAR 변환.
- **하방 편차 산출 방식**: MAR 이하 수익률만 사용해 표준편차 계산할 때 전체 N으로 나누느냐 음수 개수로 나누느냐에 따라 결과 달라짐. CFA Institute 원문 기준은 전체 N으로 나눔.
- **비정규 분포 무시**: 크래시 이벤트로 인한 극단 음수 수익(팻테일)이 하방 편차를 왜곡. 단순 std 대신 Lower Partial Moment(LPM) 사용 고려.

### 참고
- [Sharpe, Sortino & Calmar — XBTO](https://www.xbto.com/resources/sharpe-sortino-and-calmar-a-practical-guide-to-risk-adjusted-return-metrics-for-crypto-investors)
- [Sortino: A Sharper Ratio — CME Group / Red Rock Capital](https://www.cmegroup.com/education/files/rr-sortino-a-sharper-ratio.pdf)
- [ARK Invest — Measuring Bitcoin's Risk and Reward](https://www.ark-invest.com/articles/analyst-research/measuring-bitcoins-risk-and-reward)
