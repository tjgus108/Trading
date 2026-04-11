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


## [2026-04-11] Cycle 9 — Hedge Fund Risk Tools

### 실전 도구
- **Axioma (SimCorp)**: 팩터 리스크 모델 + VaR + 스트레스 테스트 통합 플랫폼. 2025년 5월 Worldwide Equity Factor Risk Model 업데이트에 머신러닝 기반 비선형 잔차 팩터 추가. 헤지펀드용 최적화·헤지 구축·규제 보고까지 원스톱.
- **MSCI RiskMetrics**: VaR/Expected Shortfall·상관관계 모델링 표준. 프랍 펌 및 기관 모두 내부 리스크 계산 벤치마크로 사용.
- **자체 구축 vs 상용**: 대형 퀀트 펀드(Two Sigma, DE Shaw 등)는 상용 도구를 레퍼런스로만 활용하고 실제 한도 집행은 자체 시스템으로 운영. 중형 이하는 Axioma/Bloomberg PORT를 그대로 사용.
- **VaR 한도 관행**: 95% VaR는 일상 모니터링, 99% VaR는 hard limit으로 사용. 상관관계 급증(스트레스 시장) 대응은 correlation-adjusted VaR 또는 Expected Shortfall(CVaR)로 전환 — 정규분포 가정이 붕괴되는 구간에서 VaR보다 ES가 더 보수적 한도 제시.
- **레버리지 한도**: 규제(Form PF 기준) + 내부 기준 이중 적용. 상관관계 급증 시 자동으로 gross leverage 축소하는 "correlation throttle" 프로토콜 운영.

### 우리 봇 적용 힌트
- `src/risk/` 에 95%/99% 두 단계 VaR 계산 추가 — 95%는 경고, 99%는 포지션 축소 트리거로 사용.
- 상관관계 급증 감지: 복수 전략 운영 시 전략 간 수익률 상관계수가 0.7 이상으로 오르면 앙상블 가중치 리밸런싱 또는 전체 포지션 축소 (Cycle 5 교훈과 연결).
- VaR보다 CVaR(Expected Shortfall)가 팻테일 이벤트(October 2025 등)에서 더 정확한 리스크 한도 기준 — 백테스트 엔진 리포트에 CVaR 추가 고려.

### 참고
- [Axioma Risk for Hedge Funds — SimCorp](https://www.axioma.com/solutions/hedge-fund-manager/)
- [RiskMetrics for Hedge Funds — MSCI](https://www.msci.com/documents/10199/3cdaaa94-43a6-4fb9-be62-f159ed624f19)
- [Quant Hedge Fund Due Diligence 2026 — Resonanz Capital](https://resonanzcapital.com/insights/quant-hedge-funds-in-2026-a-due-diligence-framework-by-strategy-type)

## [2026-04-11] Cycle 10 — LLM Trading Signals

### 실전 사례 2024-2025
- **MarketSenseAI (GPT-4 기반)**: S&P 100 15개월 테스트에서 excess alpha 10~30%, 누적 수익 최대 72%. CoT + ICL로 뉴스·펀더멘털·매크로 통합 분석.
- **Multi-LLM 크립토 봇**: DeepSeek·Claude·GPT-4o·Grok 멀티 LLM 거부권(veto) 시스템 + CNN-LSTM 조합, 2.3년 WFO 테스트 1,842% 수익·Sharpe 6.08. 단, 백테스트 과적합 의심.
- **실패/한계**: StockBench 연구에서 대부분 LLM 에이전트가 단순 Buy-and-Hold를 하회. 고빈도 거래는 추론 지연으로 LLM 부적합. LLM 행동이 실제 인간 트레이더와 다르다는 실험 결과 존재.

### 우리 봇 LLM 앙상블 유사성
- TradingAgents 프레임워크(Technical/Sentiment/뉴스 전문 에이전트 분업)가 우리 SpecialistEnsemble과 구조적으로 동일 — 독립 검증된 아키텍처.
- 멀티 LLM veto 방식은 우리 alpha-agent debate(bull_case/bear_case)와 유사. 단일 LLM 편향 완화 효과 확인됨.
- 앙상블 접근은 "프로덕션 미검증" 단계이나 학술 성과는 긍정적 — 일간 시그널 기반 운영 시 실용성 있음.

### 참고
- [MarketSenseAI — Springer Nature](https://link.springer.com/article/10.1007/s00521-024-10613-4)
- [TradingAgents Multi-Agent Framework](https://tradingagents-ai.github.io/)
- [LLM Agents vs Human Traders — arXiv](https://arxiv.org/html/2502.15800v3)


## [2026-04-11] Cycle 11 — Paper → Live Transition

### Top 5 실패 원인
- **오버피팅**: 90%의 알고 전략이 live에서 실패하는 근본 원인. 역사적 데이터를 암기한 전략은 새로운 시장 구조에서 즉시 붕괴.
- **슬리피지·수수료 미반영**: 백테스트에서 시장가 체결, 0 수수료 가정 → live에서 BTC/ETH도 1~5 bps 슬리피지 발생, 중소형 알트는 0.5~2%+.
- **감정(Emotional Gap)**: Paper에서는 없는 실자본 스트레스. 전략 규칙 이탈, 조기 청산, 과도 포지션 등 행동 오류 유발.
- **레짐 변화 무대응**: Paper 기간과 live 기간의 시장 구조가 다름 — ETF 유입 이후 크립토 레짐이 기관화. 훈련 시 존재하지 않던 새 레짐에서 모델 오작동.
- **실행 인프라 차이**: 지연(latency), 부분 체결(partial fill), 네트워크 장애 등 paper에서는 없는 운영 리스크. 거래소 API rate limit 초과 시 주문 누락.

### 체크리스트 (프로 퀀트 기준)
- **OOS 검증 완료**: Walk-forward test로 훈련 기간 외 구간에서 Sharpe/MDD 지표 재확인. 파라미터 1개당 OOS 트레이드 200개 이상 확보 권장.
- **실제 비용 반영 재백테스트**: 슬리피지(BTC 5 bps, 알트 0.5~2%), 수수료, 펀딩비 전부 포함한 상태로 Sharpe >= 1.0 재통과 여부 확인.
- **소규모 live 테스트**: 전체 자본의 1~5%로 먼저 live 실행 → 체결가 vs 백테스트 가정 차이(implementation shortfall) 측정 후 전략 조정.
- **서킷브레이커 사전 설정**: 일일 MDD 3%, 주간 7% 초과 시 자동 중단 로직 배포 완료 후 live 전환.
- **레짐 커버리지 확인**: 최소 상승/하락/횡보 3개 레짐에서 전략 성과 양호한지 스트레스 테스트 실시.

### 크립토 특화 주의점
- **펀딩비(Funding Rate)**: 선물 거래 시 롱/숏 포지션 보유 비용. Paper에서 무시하면 실전 수익성 과대 계산됨 — 특히 연율 30~100% 구간에서 치명적.
- **유동성 깊이(Market Depth)**: 포지션 크기가 호가창 깊이 0.1% 초과 시 자체 슬리피지 폭발. 소규모 알트코인에서 대형 포지션은 50%+ 슬리피지 유발 가능.
- **거래소 API 불안정**: ccxt 기반 운영 시 rate limit, 타임아웃, 부분 체결 처리 로직이 없으면 실전에서 미체결 주문 누적.

### 참고
- [Paper vs Live Trading — Alpaca](https://alpaca.markets/learn/paper-trading-vs-live-trading-a-data-backed-guide-on-when-to-start-trading-real-money)
- [Overfitting Crypto Strategies — TrendRider](https://trendrider.net/blog/how-to-avoid-overfitting-crypto-trading)
- [Backtesting with Realistic Costs — Paybis](https://paybis.com/blog/how-to-backtest-crypto-bot/)


## [2026-04-11] Cycle 12 — Monitoring Metrics

### 핵심 실시간 지표
- **Sharpe / Sortino 실시간 롤링**: 30~90일 롤링 윈도우로 전략 성과 열화 조기 감지. Sortino 급락 = 하방 리스크 증가 신호.
- **최대 낙폭(MDD) 실시간 추적**: 에쿼티 커브 peak-to-trough 연속 계산. 일일 3%, 주간 7% 초과 시 서킷브레이커 트리거.
- **Profit Factor 누적**: 실시간 총이익/총손실 비율. 1.5 이하로 하락 시 전략 성능 저하 경보.
- **체결가 vs 백테스트 가격 차이(Implementation Shortfall)**: 주문 접수~체결 간 가격 차이 누적. 슬리피지 예산 초과 여부 판단.
- **포지션 노출(Gross/Net Exposure)**: 전략별·전체 레버리지 실시간 합산. 상관관계 급증 시 gross 자동 축소 기준으로 사용.

### 크립토 특화 이상 징후
- **펀딩비 급변**: 8시간 주기 펀딩률이 0.05% 초과 시 한쪽 방향 과매수/과매도 신호. 이 임계치 돌파는 단기 반전 또는 강제 청산 cascade 전조.
- **청산 급증(Liquidation Spike)**: 대형 레버리지 포지션 동시 청산 → 10~20분 내 10~20% 급락 가능. 청산 볼륨이 일평균 3배 이상 시 봇 즉시 포지션 축소 권장.
- **거래량/시총 비율 급등**: 단시간 거래량이 시총의 수% 이상 → 펌프·덤프 또는 고래 이탈 패턴. Z-score 기반 이상치 탐지(Isolation Forest, LSTM Autoencoder)가 실용적.

### 참고
- [AI Trading Bot Metrics — 3Commas](https://3commas.io/blog/ai-trading-bot-performance-analysis)
- [Crypto Anomaly Detection (Deep Learning + Band Protocol) — Google Cloud](https://medium.com/google-cloud/technical-indicators-calculation-and-anomaly-detection-on-band-protocol-data-6dbf3b9b92c6)
- [Funding Rate Guide — Bitunix](https://blog.bitunix.com/en/2024/07/15/understanding-crypto-funding-rate/)

## [2026-04-11] Cycle 13 — Market Structure 2025

### ETF 자금 패턴 변화
- 2025년 연간 크립토 ETP 순유입 $46.7B, IBIT(BlackRock) 단독 $25.1B 흡수로 스팟 BTC ETF 카테고리의 약 60% 점유.
- 유입 패턴: 상반기~7월 강세(BTC $110k 돌파 견인), 11월부터 30일 이동평균 순유입이 음전환—연말 방어적 포지셔닝.
- Q1 2026 기준 글로벌 크립토 ETP 순유입 $18.7B(BTC $12.4B), 2026 연간 페이스가 2025($47.2B) 초과 예상.

### 거래소 집중도
- Binance 38.3%(2025년 12월 스팟), OKX 16.2%로 양사 합산 54% 이상. Bybit·Bitget 포함 상위 4개사가 스팟 70%+.
- OKX는 2025년 9월 파생상품 월간 거래량 $1.3T로 Binance 추월—파생 시장 집중도 이동 주목.

### 알고 트레이딩 비중
- 거래소별 공식 알고/수동 거래 분리 통계 미공개. 간접 지표로 상위 4개 거래소 70%+ 집중 + 고빈도 유동성 패턴이 알고 비중 확대 지속을 시사.
- 2024 대비 AI 봇 플래시 크래시(2025-05 $2B, 2025-10 $3.21B) 사례 증가 → 알고 비중 상승 부작용 가시화.

### 참고
- [Bitcoin ETF record outflows deceptive — CryptoSlate](https://cryptoslate.com/bitcoin-etf-record-outflows-are-deceptive-as-crypto-products-absorbed-46-7-billion-in-2025/)
- [Crypto Exchange Market Share — CoinGecko](https://www.coingecko.com/research/publications/centralized-crypto-exchanges-market-share)
- [Crypto ETFs 2025 Year in Review — Yahoo Finance](https://finance.yahoo.com/news/crypto-etfs-2025-bitcoin-ethereum-140103429.html)

## [2026-04-11] Cycle 14 — MEV and Bot Competition

### MEV 현황
- 2025년 MEV 총 거래량 $561.9M 중 샌드위치 공격이 51.6%($289.8M) 차지. 일평균 4,400건 이상.
- jaredfromsubway.eth 등 단일 봇이 2025-01 샌드위치 1건으로 $800k 수익; AI·ML 기반 봇들이 체인형 공격(샌드위치+차익거래 연결) 고도화.
- 이더리움 트랜잭션의 80%가 Flashbots Protect·MEV Blocker 등 프라이빗 RPC 사용—그러나 프라이빗 채널도 2024-11~12월 2,932건 샌드위치 피해 확인($40.9만 손실).

### 우리 봇 영향
- CEX 기반 봇(ccxt)은 온체인 MEV 직접 노출 없음. 단, DEX 연동·크로스 마켓 차익거래 추가 시 프론트러닝 리스크 즉시 발생.
- 슬리피지 설정 엄격화(tight slippage) + 고유동성 풀 한정 + 주문 크기 분할로 샌드위치 공격 비용 억제 가능.

### 참고
- [Sandwiched and Silent (arxiv 2512.17602)](https://arxiv.org/html/2512.17602v1)
- [Flashbots Protect RPC](https://docs.flashbots.net/flashbots-protect/overview)
- [Solana MEV 현황 — Solana Compass](https://solanacompass.com/learn/accelerate-25/scale-or-die-at-accelerate-2025-the-state-of-solana-mev)


## [2026-04-11] Cycle 15 — Recent Bot Failures (H2 2025)

### 신규 사례
- **Nova Trading Platform 보안 침해 (2025-09-16)**: $500k 탈취. 피해자 지갑이 Jupiter·Axiom·Photon·Nova 4개 플랫폼과 연결된 상태에서 "수동 드레인" 방식으로 실행. 프라이빗 키를 서드파티 봇 플랫폼에 위임한 구조 자체가 단일 장애점(SPOF). 다수 사용자가 동시 피해 → 플랫폼 레벨 시스템 취약점 의심.
- **XRP 예측 시장 AMM 봇 착취 (2025-12~2026-01)**: 익명 트레이더 a4385가 15분 인터벌 예측 시장의 AMM 봇·쿼트 모델을 48시간 동안 체계적으로 공략해 $280k 수익. 피해 봇 0x8dxd는 2025-12부터 $740k 누적 이익을 쌓은 "거의 완벽한" 커브를 기록했으나 단 한 번의 공략으로 전체 수익 소멸. 봇 행동 패턴의 예측 가능성(rigid/predictable behavior)이 역이용됨.
- **AI 봇 Flash Crash 가속 (2025-05)**: 정상 시장 조건용 AI 봇들이 갑작스러운 변동성에 $2B 매도 집행. Cycle 1에서 May 2025를 언급했으나 메커니즘 세부 확인: 레짐 감지 로직 완전 부재가 직접 원인.

### 공통 패턴
- **예측 가능한 행동 패턴이 역이용됨**: AMM/쿼트 봇의 고정 인터벌·규칙 기반 응답이 공격자에게 착취 벡터 제공. 봇 로직의 무작위성(jitter) 또는 파라미터 동적 변경 부재가 근본 원인.
- **서드파티 플랫폼 키 위임 리스크**: 프라이빗 키를 외부 봇 서비스에 맡기는 구조는 해당 플랫폼이 단일 장애점이 됨. CEX API Key 권한 최소화(출금 권한 제거) + 화이트리스트 IP 제한이 필수.

### 참고
- [Nova Trading Platform Breach — Cyber Defense Magazine](https://www.cyberdefensemagazine.com/nova-trading-platform-security-breach-half-a-million-dollars-drained-in-manual-attack/)
- [XRP AMM Bot Exploit — MEXC Blog](https://blog.mexc.com/news/mystery-trader-nets-280k-outsmarting-quant-bots/)
- [Bot Failures 2025 — Crypto Reporter](https://www.crypto-reporter.com/press-releases/most-crypto-trading-bots-promised-easy-money-the-market-killed-them-here-is-what-the-survivors-built-instead-123004/)

## [2026-04-11] Cycle 16 — Production Deployment

### 배포 전략
- **Canary 배포**: 전체 자본의 1~5%로 신전략 먼저 live 실행. 라우터/서비스 메시가 소량 트래픽(~5%)만 신버전으로 전달. 슬리피지·체결가 차이 측정 후 점진 확대.
- **Blue-Green 환경**: 구버전(Blue) 유지 상태에서 신버전(Green) 병렬 배포. 문제 발생 시 즉시 Blue로 트래픽 전환 → 롤백 시간 최소화.
- **Runbook 사전 작성**: 롤백 명령어, 알림 채널, 메트릭 대시보드 위치를 문서화. 스테이징 환경에서 매 스프린트 롤백 시뮬레이션 실시.

### Kill Switch 설계
- **Feature Flag 기반**: 개별 전략 또는 기능을 즉시 비활성화. 전체 재배포 없이 단일 전략만 off — 수술적 대응 가능.
- **자동 트리거 Circuit Breaker**: 일일 MDD 3%, 주간 7% 초과 또는 API 오류율 급증 시 모든 포지션 진입 즉시 중단. Telegram/Discord 실시간 알림 연동.
- **포지션 한도 하드코딩**: 포트폴리오당 최대 노출 10%, 저유동성 자산 주문 크기 시장 깊이의 0.1% 이하를 코드 레벨에서 강제.

### 참고
- [Canary Release vs Kill Switch — Unleash](https://www.getunleash.io/blog/canary-release-vs-kill-switch)
- [Trading System Kill Switch — NYIF](https://www.nyif.com/articles/trading-system-kill-switch-panacea-or-pandoras-box)
- [Algo Trading Risk Management — LuxAlgo](https://www.luxalgo.com/blog/risk-management-strategies-for-algo-trading/)

## [2026-04-11] Cycle 17 — Volatility Regime Detection (New Methods)

### 신규 기법
- **Soft Regime HAR**: HMM으로 레짐 확률 산출 후 HAR 모델 두 개(저변동/고변동)를 확률 가중치로 블렌딩 — 경계 구간 hard-switch 오류 제거
- **Probabilistic-Attention Transformer**: 외부 추정 쇼크 확률을 attention weight에 직접 임베딩, VIX 급등 조기 감지에 효과적
- **Ensemble-HMM Voting (Multi-Model)**: Random Forest·XGBoost·HMM을 앙상블 투표로 결합, 단일 모델 레짐 오분류 완화
- **VMD + Cascaded LSTM-Attention**: Variational Mode Decomposition으로 주파수 성분 분리 후 LSTM-Attention 통과, VIX 비선형 급변 포착

### 실전 한계
- Transformer/Attention 계열은 훈련 데이터가 부족한 저유동성 코인에서 과적합 심각, 실전 배포 전 OOS 검증 필수
- Soft-regime 블렌딩은 레짐 전환 지연(lag)이 여전히 존재 — 급격한 플래시 크래시엔 여전히 취약

### 참고
- [Soft Regime-Switching HAR (arxiv 2510.03236)](https://arxiv.org/html/2510.03236v1)
- [Probabilistic-Attention Transformer for VIX (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0952197624003816)
- [Ensemble-HMM Voting Framework (AIMS Press)](https://www.aimspress.com/article/id/69045d2fba35de34708adb5d)

## [2026-04-11] Cycle 18 — Exchange API Security

### 보안 사고 사례
- **Bybit 2025-02** — $1.5B ETH 탈취. 북한 연계 해커가 내부 IT직원 위장 침투(supply-chain), 콜드→핫 이전 서명 과정에서 UI 위장 공격으로 multisig 서명 탈취. 역대 최대 단일 해킹.
- **DMM Bitcoin 2024-05** — $320M(4,500 BTC) 탈취. 프라이빗 키 탈취로 핫월렛 직접 접근. 2024년 최대 거래소 사고.
- **WazirX 2024-07** — $235M 피해. 멀티시그 지갑 서명 프로세스 취약점 악용, API 키 탈취 후 대량 출금.

### 베스트 프랙티스
- **출금 화이트리스트**: API 키에 허용 주소 목록 고정, 임의 주소 출금 차단
- **최소 권한 원칙**: 트레이딩 봇용 키는 Read+Trade만, 출금 권한 절대 부여 금지
- **IP 화이트리스트**: API 키를 특정 서버 IP로만 사용 가능하도록 거래소에서 제한
- **키 로테이션**: 주기적(30~90일) API 키 재발급, 미사용 키 즉시 폐기
- **환경변수/시크릿 관리**: 코드에 하드코딩 금지, AWS Secrets Manager·Vault 등 사용 + 출금 딜레이 알림 설정

### 참고
- [Bybit Hack Analysis — Chainalysis](https://www.chainalysis.com/blog/bybit-exchange-hack-february-2025-crypto-security-dprk/)
- [Coinbase API Security Best Practices](https://docs.cdp.coinbase.com/get-started/authentication/security-best-practices)
- [Crypto Exchange Hacks Statistics — CoinLaw](https://coinlaw.io/crypto-exchange-hacks-and-security-statistics/)

## [2026-04-11] Cycle 19 — Funding Rate Arbitrage Reality

### 실전 수익률
- 2024 연평균 수익률 약 14.39%, 2025년 19.26%로 반등 — 강세장 펀딩비 상승 효과
- 강세장 구간 8시간 펀딩비 0.05~0.2%, 연환산 22~100%+ 가능; 횡보장은 0%에 수렴
- 전체 기회 중 40%만 거래비용·스프레드 반전 후 양의 수익 — 신중한 진입 필수
- 시장 참가자 증가로 아비트라지 풀이 커질수록 수익 축소 확인(ScienceDirect 연구)

### 우리 봇 funding_rate 전략 재평가
- 강세 사이클 의존도 높음 — 중립·약세장 진입 필터 없으면 수수료 손실 누적 위험
- 펀딩비 급변 시 델타 헤지 슬리피지로 단기 포지션 붕괴 가능, 서킷브레이커 필수

### 참고
- [ScienceDirect — Risk and Return of Funding Rate Arbitrage (CEX/DEX)](https://www.sciencedirect.com/science/article/pii/S2096720925000818)
- [Gate.io — Perpetual Contract Funding Rate Arbitrage 2025](https://www.gate.com/learn/articles/perpetual-contract-funding-rate-arbitrage/2166)
- [Amberdata — Ultimate Guide to Funding Rate Arbitrage](https://blog.amberdata.io/the-ultimate-guide-to-funding-rate-arbitrage-amberdata)

## [2026-04-11] Cycle 20 — Leveraged Tokens

### 구조와 함정
- 레버리지 토큰(예: BTC3L)은 매일 3x 레버리지를 자동 리밸런싱으로 유지. 수익 시 재투자, 손실 시 포지션 축소.
- **변동성 감쇠(Volatility Decay)**: 기초자산이 +10%→-9.09% 복귀 시 3x 토큰은 +30%→-27.27% = 순 손실. 지수가 제자리여도 토큰은 손실 발생.
- 연간 변동성 50% 환경에서 리밸런싱만으로 10~15% 연간 가치 잠식. 횡보 또는 고변동 구간에서 피해 극대화.
- 플랫폼별 리밸런싱 트리거 범위 상이(Gate: Long 2.25x~4.125x 유지). 급변동 시 강제 즉시 리밸런싱 발동.

### 봇 활용 시 주의
- 레버리지 토큰은 **단기(당일) 방향성 베팅 전용**. 봇이 다중 사이클 또는 횡보 구간에서 보유 유지 시 decay 누적으로 전략 수익 잠식.
- 리밸런싱 타이밍에 봇 진입이 겹치면 "고점 매수·저점 매도" 구조적 패턴에 편승하는 셈 — 진입 조건에 레짐 필터 및 보유 시간 상한 필수.

### 참고
- [All You Need to Know About Leveraged Tokens in 2025 — 3Commas](https://3commas.io/blog/leveraged-tokens)
- [4 Pitfalls of Trading Leveraged Tokens — Binance Blog](https://www.binance.com/en/blog/all/4-pitfalls-of-trading-leveraged-tokens-and-how-to-avoid-them-421499824684900885)
- [3x Leveraged ETFs Guide — Bitget Academy](https://www.bitget.com/academy/3x-leveraged-etfs)

## [2026-04-11] Cycle 21 — Infrastructure Best Practices

### 지연 최적화
- 거래소 서버와 같은 데이터센터(Equinix NY4/LD4 등)에 VPS 배치 시 RTT 0.3~1ms 달성 가능. 물리적 거리가 지연의 핵심.
- 10~20ms 지연만으로도 스캘핑/브레이크아웃 전략 수익의 30~50% 잠식. 표준 NIC(20~50µs) 대비 kernel-bypass NIC(1~5µs) 고려.
- 암호화폐는 Binance/OKX 서버가 주로 AWS Tokyo/Singapore 기반 → 해당 리전 VPS 선택이 우선.

### Failover & 모니터링
- **systemd**: `Restart=always` + `RestartSec=5s` 설정으로 크래시 시 자동 재기동. 가장 경량 옵션.
- **Docker**: 컨테이너 격리로 환경 일관성 보장. `--restart=unless-stopped` 플래그로 failover. Freqtrade/Hummingbot 모두 공식 Docker 이미지 제공.
- **다중 인스턴스**: Primary/Standby 구성 + 헬스체크 엔드포인트로 active failover. 단일 장애점 제거 필수.

### 참고
- [Low Latency Trading Infrastructure — QuantVPS](https://www.quantvps.com/blog/low-latency-trading)
- [Algo Trading VPS Optimization 2025 — TradingFXVPS](https://tradingfxvps.com/api-trading-vps-optimization-2025-websocket-rest-for-algo-strategies/)
- [Crypto Trading Bot Best Practices 2024 — Alwin.io](https://www.alwin.io/best-practices-for-optimizing-your-crypto-trading-bot-in-2024)

## [2026-04-11] Cycle 22 — New Performance KPIs

### 신규 지표
- **Deflated Sharpe Ratio (DSR)**: Sharpe를 복수 전략 테스트에 따른 선택 편향(selection bias) + 비정규 수익 분포(팻테일, 왜도)로 보정. Probabilistic Sharpe Ratio(PSR)가 먼저 true SR > 임계값일 확률을 계산하고, DSR은 여러 전략을 시험했을 때의 기댓값 보정까지 추가.
- **Probability of Backtest Overfitting (PBO)**: CSCV(Combinatorially Symmetric Cross Validation) 방식으로 in-sample 최적 전략이 OOS에서 underperform할 확률을 0~1로 수치화. PBO > 0.5면 과적합으로 판단.
- **MCC (Matthews Correlation Coefficient)**: TP/TN/FP/FN을 모두 반영하는 이진 분류 품질 지표(범위 -1~1). 클래스 불균형에 강건해 시그널 예측 정확도 평가에서 Accuracy/F1보다 신뢰도 높음.
- **Calmar Ratio**: 연환산 수익률 / MDD. 드로다운 대비 수익 효율 지표로 크립토처럼 MDD가 급변하는 자산에 유용. Sharpe는 변동성 전체, Calmar은 최악 드로다운만 대비.

### 우리 봇 적용 가능성
- 백테스트 엔진에 DSR/PBO 추가 시 "Sharpe >= 1.0은 통과하지만 실제론 과적합" 전략을 사전 필터링 가능 — 현재 엔진의 Sharpe·MDD·PF 3종 기준에 DSR을 4번째 게이트로 추가 검토.
- MCC는 BUY/SELL/HOLD 시그널 품질 평가에 즉시 적용 가능. Signal 생성 후 실제 결과와 대조하는 모니터링 레이어에 MCC 계산 추가.

### 참고
- [The Deflated Sharpe Ratio — Bailey & Lopez de Prado](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)
- [Probability of Backtest Overfitting — Bailey et al.](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf)
- [pypbo: PBO in Python — GitHub](https://github.com/esvhd/pypbo)

## [2026-04-11] Cycle 23 — 2025 Performance Benchmark

### 수익률 분포
- 상위 10% (기관급 AI봇): 연간 40%+ 수익률, Profit Factor 4.0+, Sharpe 1.8+ (Tickeron FLM 기준 PF 4.4 기록)
- 중위 50% (일반 알고봇): 연간 15~25% 수익률, 알고 전략 평균 Sharpe 1.8 vs 재량 트레이딩 1.1
- 하위 90% 경계선: 크립토 HFT 마켓메이킹 8~12%, 플랫폼 상위봇 연간 12~25% 범위 분포

### 생존율
- 공개된 신뢰할 수 있는 12개월 생존율 통계 없음 (마케팅 수치만 존재)
- 업계 통설: 소매 알고봇 80% 이상이 1년 내 수익 미달로 운영 중단 추정 (출처 불명확)

### 참고
- [Is AI Bot Trading Profitable in 2025? Real Results Revealed](https://agentiveaiq.com/blog/is-ai-bot-trading-profitable-the-2025-reality-check)
- [78 Algorithmic Trading Statistics Every Trader Should Know in 2025](https://medium.com/@algorithmictradingstrategies/78-algorithmic-trading-statistics-every-trader-should-know-in-2025-c7e03c36ee44)
- [AI Trading Bots - 2025 Performance Benchmarks Revealed](https://redhub.ai/ai-trading-bots-2025/)

## [2026-04-11] Cycle 24 — Session/Holiday Patterns

### 세션별 패턴
- EU-US 오버랩(12:00–16:00 UTC)이 하루 중 가장 높은 변동성·거래량 구간. 미국 세션이 전체 중 긍정 수익 집중도 가장 높음.
- 아시아 세션(도쿄)은 상대적으로 낮은 변동성·높은 안정성. 유럽·미국 주식 시장 개장 시간과 겹칠수록 BTC 변동성도 증가.
- 주말은 유동성 감소 + 낮은 거래량이지만, 뉴스/내러티브 주도 스파이크 후 월요일 mean-revert 패턴이 자주 관찰됨.
- 크리스마스·연말 같은 휴일에는 기관 참여 감소로 유동성 극도 취약 — 저유동성 급등/급락이 복귀 시 빠르게 되돌림.

### 봇 적용
- 세션 필터: 아시아 단독 세션(00:00–08:00 UTC)은 브레이크아웃 전략 신뢰도 낮음 → 이 구간 신규 진입 신호 스킵 또는 confidence 하향 조정 검토.
- 주말/휴일 필터: 금·토·일(UTC) 또는 주요 공휴일 기간에는 포지션 사이즈 축소, 또는 HOLD 강제 유지로 유동성 리스크 회피.

### 참고
- [Bitcoin's Weekend Effect — ResearchGate](https://www.researchgate.net/publication/396418897_Bitcoin's_Weekend_Effect_Returns_Volatility_and_Volume_2014-2024)
- [Trading Between Hours: Volatility Dispersion Across Multiple Regions — Amberdata](https://blog.amberdata.io/trading-between-hours-volatility-dispersion-across-multiple-regions)
- [Time-of-day periodicities of trading volume and volatility in Bitcoin — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1544612319301904)

## [2026-04-11] Cycle 25 — AI Agent Trading Reality

### 실전 성과
- Claude Opus 4가 생성한 전략은 백테스트에서 $10K → $32K (SPY $16.6K 대비), Sortino 1.11 vs SPY 0.81 기록.
- GPT-5, Claude 4, Gemini 등 5개 모델이 Alpha Arena 경쟁에서 각 $10K로 실제 크립토 거래 — 결과는 모델별로 크게 상이.
- 다중 에이전트 조합(Perplexity+Claude+GPT)이 단독 모델보다 승률 25~40% 향상 보고. 단, 이는 대부분 시뮬레이션/백테스트 기반.

### 비용 vs 수익
- 단일 분석당 비용: GPT-5 $0.50~1.00, Claude 4 $0.30~0.60. 봇 100개 기준 월 약 $2,400.
- 토큰 최적화(저렴한 모델 70% + 고급 모델 30% 혼용) 시 비용 80~90% 절감 가능, 월 1차 ROI 달성 사례 있음.
- 실전 순수익 데이터는 공개 사례 부족 — 대부분 백테스트 수치이며 슬리피지·거래 비용 미반영.

### 참고
- [Claude Opus 4 Trading Strategy — Medium](https://medium.com/@austin-starks/i-let-claude-opus-4-create-a-trading-strategy-it-destroyed-the-market-c200bf1a19a4)
- [LLM Trading Bots Comparison — FlowHunt](https://www.flowhunt.io/blog/llm-trading-bots-comparison/)
- [LLM API Pricing 2025 — IntuitionLabs](https://intuitionlabs.ai/articles/llm-api-pricing-comparison-2025)

## [2026-04-11] Cycle 26 — Regulatory Landscape

### 주요 규제 동향
- EU MiCA(Markets in Crypto-Assets) 2025년 1월 전면 시행. 기존 MiFID와의 해석 충돌 문제로 각국 적용 편차 존재.
- 한국: 2024년 7월 「가상자산 이용자 보호법」 시행. 시세조종·미공개정보 이용 등 불공정거래 행위 형사처벌 대상. "시장조성" 행위의 법적 정의 미비로 자동매매 봇 운영이 그레이존에 해당.
- 미국: SEC는 알고리즘 트레이딩 자체를 금지하지 않으나 시세조종 금지법·기록보관·공시 의무는 동일 적용. 2025-06 자동화 투자자문 가이드라인 발표.
- 한국 2단계 규제(디지털자산기본법): 2026년 1월 입법 예고 예정. 스테이블코인·해외 사업자 포함 통합 프레임워크.

### 개인 봇 운영자 주의점
- 자기 자금만 운용하는 개인은 별도 라이선스 불필요(한국·미국·EU 공통). 단, 타인 자금 운용·유료 신호 서비스는 투자자문업 등록 필요(미국 CTA/RIA, 한국 투자일임업).
- 한국 가상자산 이용자 보호법상 "시장조성" 정의 불명확 → 마켓메이킹 전략 운용 시 법적 위험 존재. 허수주문(Spoofing)·세탁거래(Wash Trading)는 명시적 위반.
- 거래소 ToS 위반(봇 금지 조항)도 계정 정지·자산 동결로 이어질 수 있어 별도 확인 필수.

### 참고
- [2025 Crypto Regulatory Round-Up — Chainalysis](https://www.chainalysis.com/blog/2025-crypto-regulatory-round-up/)
- [South Korea Crypto Regulations — CoinTelegraph](https://cointelegraph.com/learn/articles/crypto-regulations-in-south-korea)
- [AI Crypto Trading Bots Legal Guide — internetlawyer-blog.com](https://www.internetlawyer-blog.com/ai-crypto-trading-bots-navigating-state-federal-and-international-laws/)

## [2026-04-11] Cycle 27 — Psychological Failure Modes

### 운영자 실수 패턴
- 드로다운 발생 시 봇을 수동 중단하거나 파라미터를 즉흥 수정 → 정상 손실 구간을 전략 실패로 오인한 감정적 개입
- 백테스트 과최적화(Overfitting)로 연 수백% 수익률 착각 → 실제 자본 과대 투입 후 라이브 시 즉시 붕괴 (in-sample vs out-of-sample 상관관계 0.05 미만)
- "Set and forget" 심리로 모니터링 방치 → 이상 거동·슬리피지 누적 미감지. 자동화 계좌의 73%가 6개월 내 실패
- 2025-05 플래시 크래시: AI 봇들이 정상 조건 전용으로 과적합되어 2분 만에 $2B 매도 집행, 변동성 레짐 전환 미감지

### 방지책
- 백테스트 지표(Sharpe, MDD)에 walk-forward 검증 필수. 단일 in-sample 결과로 자본 배분 금지
- 드로다운 한도(예: 일일 3%) 초과 시 자동 서킷브레이커 적용, 수동 개입 프로세스 사전 문서화
- 라이브 실행 시 소규모(실제 운용 자본의 5% 이하) 파일럿 우선 → 심리적 손실 내성 확인 후 증액

### 참고
- [Do Trading Bots Fail? — Finance Monthly](https://www.finance-monthly.com/2024/01/do-trading-bots-fail/)
- [How to Avoid Overfitting in Crypto Trading Bots — DEV Community](https://dev.to/trendrider/how-to-avoid-overfitting-in-crypto-trading-bots-lessons-from-10000-backtested-trades-2oci)
- [AI Trading Bots Advisory — CFTC](https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/AITradingBots.html)

## [2026-04-11] Cycle 28 — AMM/DEX Interaction

### 봇-LP 상호작용
- MEV 봇(샌드위치 공격, 차익거래)은 유동성 제공자(LP)로부터 연간 $500M 이상을 추출. 이를 Loss-versus-Rebalancing(LVR)이라 부름
- AMM은 가격이 시장 가격보다 낮을 때 차익거래 봇이 먼저 거래하여 LP가 손실을 입는 구조적 취약점 존재
- 일반 CeFi 봇은 DEX와 직접 상호작용 시 MEV 봇에 샌드위치 당할 위험이 있음 — 슬리피지 설정 필수
- Uniswap v3 집중 유동성(concentrated liquidity) LP 중 약 50%가 단순 보유(hold) 대비 음수 수익 기록

### 주의점
- CeFi 봇이 DEX 호가를 참고할 때, AMM 가격은 차익거래 봇이 정리하기 전까지 시장 가격에 지연됨 — 신호 오염 가능성
- LP 포지션을 봇 전략의 일부로 사용하면 변동성 급등 시 임펄스 손실(IL)이 일반 봇 손실보다 훨씬 커질 수 있음

### 참고
- [AMMs: Toward More Profitable Liquidity Provisioning](https://arxiv.org/html/2501.07828v1)
- [Bots fleece DeFi LPs for $500m/year — DL News](https://www.dlnews.com/articles/defi/new-cow-swap-amm-will-stop-mev-bots-and-save-users-millions/)
- [CoW DAO MEV-Capturing AMM](https://cow.fi/learn/cow-dao-launches-the-first-mev-capturing-amm)

## [2026-04-11] Cycle 29 — Successful Bot Patterns

### 성공 공통 요소
- Profit Factor 2.0+ 유지, Sharpe 1.5+, MDD 15-20% 이내 — 살아남는 봇의 최소 기준이 아닌 운영 목표로 설정
- 단순 전략 우선: 복잡한 ML 모델보다 규칙 기반 단순 전략이 라이브에서 더 안정적. 과적합 위험 낮음
- 멀티 데이터 통합: 기술 지표 단독이 아닌 센티멘트·거시 신호 병합 시 적응력 향상
- 52%의 자동화 계좌가 3개월 내 실패 — 생존 봇은 포지션 크기 알고리즘 + 일일 손실 한도 + 상관관계 모니터링 3종 세트 보유
- 30일·90일 롤링 일관성으로 성과 측정 (백테스트 최고 수익률 기준 금지)

### 운영 습관
- 1쌍 1타임프레임으로 시작 → 실제 자본 5% 이하 파일럿 → 다변화 순서 준수
- 봇 오버라이드 금지: 수동 개입 시 평균 68% 자본 손실. 전략 신뢰 또는 전략 교체 둘 중 하나만
- 지속적 모니터링 + 보안 패치: "set and forget" 방치 계좌 73%가 6개월 내 실패

### 참고
- [Why AI Trading Bots Fail — Amplework](https://www.amplework.com/blog/ai-trading-bots-failures-how-to-build-profitable-bot/)
- [Why Most Trading Bots Lose Money — ForTraders](https://www.fortraders.com/blog/trading-bots-lose-money)
- [AI Bot Trading Profitable 2025? — AgentiveAIQ](https://agentiveaiq.com/blog/is-ai-bot-trading-profitable-the-2025-reality-check)

## [2026-04-11] Cycle 30 — Market Microstructure 2025

### 주요 변화
- Binance CEX 스팟 점유율 2025년 40%대 → 2026 Q1 32%로 하락. CEX 전체 거래량 Q1 2026 기준 전기 대비 48% 감소
- Hyperliquid, 2025년 perp DEX 시장의 최대 80% 점유 후 경쟁자(Aster 등) 등장으로 38%대로 축소. Perp DEX 전체 점유율은 파생상품 시장의 26%(전년 한 자릿수 → 급성장)
- 기관 자금: 비트코인 스팟 ETF 2025년 순유입 $26B, 기관+기업 합산 $70B+ 유입(전년 $30B 대비 2배+). 비트코인이 기관 포트폴리오 정식 편입

### 봇 영향
- DEX 유동성 분산(CEX→DEX 이동)으로 CEX 기반 호가/체결 데이터의 대표성 약화. 주요 페어는 Hyperliquid 오더북 병행 모니터링 필요
- 기관 유입으로 변동성 패턴 변화: 과거 리테일 주도의 급등락 감소, 트렌드 지속성 증가 가능성 → 추세추종 전략 유리 환경

### 참고
- [DEXs Hit Record Market Share — CoinDesk](https://www.coindesk.com/markets/2025/07/21/decentralized-crypto-exchanges-hit-record-market-share-in-q2-volume-coingecko-report)
- [Hyperliquid chips away at Binance — The Block](https://www.theblock.co/post/368674/hyperliquid-captures-80-of-decentralized-perps-market-chipping-away-at-binance)
- [Institutional Crypto Adoption 2025 — Grayscale](https://research.grayscale.com/reports/2026-digital-asset-outlook-dawn-of-the-institutional-era)

## [2026-04-11] Cycle 31 — Developer Regrets

### Top 후회 사례
- **백테스트 과적합**: 과거 특정 기간에 최적화된 파라미터가 라이브에서 즉시 붕괴. 백테스트 Sharpe가 40% 이상 하락하거나 MDD가 2배 이상 증가하면 이미 과적합
- **트랜잭션 비용 미반영**: 수수료·슬리피지 누락으로 백테스트 수익성이 실제와 극단적으로 괴리. 초기부터 현실적 비용 모델 미적용 후회
- **리스크 한도 부재**: 손절/일일 손실 한도 없이 배포하면 작은 버그가 대규모 드로다운으로 확대. "실행 중단" 로직을 처음부터 설계하지 않은 것이 최대 후회
- **API 키 노출**: 코드 저장소·스크린샷·공유 설정 파일에 API 키 유출 — 계정 탈취로 직결. 보안 설계 후행 처리 후회

### 초기에 했어야 할 일
- **Walk-forward 검증 습관화**: 초기 윈도우 학습 → 다음 윈도우 테스트 → 롤링 반복. 단순 전체 기간 백테스트 금지
- **단순 전략 우선 배포**: 복잡한 다중 인디케이터 조합보다 단일 규칙 전략으로 라이브 동작 확인 후 확장
- **서킷브레이커 설계 선행**: 일일 드로다운 한도·레짐 감지 필터를 첫 번째 기능으로 구현
- **Paper trading 의무화**: 실자본 투입 전 최소 30일 포워드 테스트로 슬리피지·레이턴시 현실 확인

### 참고
- [The Biggest Mistakes I Made Building a Crypto Bot — Medium](https://swaeth.medium.com/the-biggest-mistakes-i-made-building-a-crypto-bot-7d3509883f25)
- [Common Pitfalls: What Beginners Get Wrong — Coin Bureau](https://coinbureau.com/guides/crypto-trading-bot-mistakes-to-avoid)
- [Why Most Crypto Trading Bots Fail — DEV Community](https://dev.to/matrixtrak/why-most-crypto-trading-bots-fail-and-how-to-build-one-that-actually-works-257g)

## [2026-04-11] Cycle 32 — 2025 Final Trends
- 온체인 AI 에이전트 부상: 거래소 API 기반 봇에서 온체인 직접 자산 보유·프로토콜 상호작용 에이전트로 전환. BNB Chain ERC-8004 등 표준 등장
- LLM 기반 적응형 봇: 고정 규칙 대신 실시간 시장 복잡성을 처리하는 학습·적응형 AI 에이전트가 주류화, AI 관련 토큰 시총 $23B→$50.5B 급증(2024→2025)
- 인텐트 기반 트레이딩: 사용자 목표를 온체인 액션으로 자동 변환하는 지갑·봇 통합 방식 등장
- DeFi 자동화 확장: 유동성 공급·수익 최적화 AI 봇이 CEX 중심에서 DEX/DeFi로 확장, 멀티체인 중재 전략 증가

