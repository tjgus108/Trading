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


---

## [2026-04-11] Cycle 33 — Long-Term Success
- 1년 이상 생존하는 봇의 공통점: 단일 전략 고집 없이 레짐(상승/횡보/하락)에 따라 전략을 전환하는 적응형 설계
- 과최적화(overfitting) 방지: 백테스트 성과가 뛰어나도 walk-forward + out-of-sample 검증 통과한 보수적 파라미터만 사용
- 운영 인프라: 99.9%+ API 업타임, 서킷브레이커(일일 3% MDD), 포지션 1% 룰 등 리스크 관리 자동화가 전략 성능보다 더 중요
- Profit Factor 1.5 이상 + 주기적(최소 주1회) 성과 지표 리뷰로 전략 열화를 조기 감지하는 모니터링 루틴 필수

## [2026-04-11] Cycle 34 — Paper→Live Timing
- 최소 4~8주 Paper Trading으로 100건 이상 트레이드 샘플 확보 후 전환 권장 (시장 레짐 2개 이상 경험 필수)
- 전환 기준 지표: Sharpe≥1.0, PF≥1.5, MDD≤20%, 연속 손실 5회 미만, 슬리피지·수수료 반영 후에도 수익
- Live 전환 시 소액(전체 자본의 5~10%)으로 시작, Paper 대비 실제 체결가 차이(슬리피지) 모니터링 1~2주 추가

## [2026-04-11] Cycle 35 — TradingView Webhook Bots
- TradingView 웹훅은 Plus 플랜 이상 필요, 포트 80/443만 허용, 응답 3초 초과 시 취소됨
- Pine Script 한계: 바 마감 시점에만 실행(1회/바), 시장 휴장 중 지연 알람 미발송, JSON 빌더 내장 없음
- 장점: 전략 시각화+알람 통합, 커스텀 봇(Flask 등)과 쉽게 연동 가능
- 단점: 실행 지연 불가피, 민감 정보 노출 위험, Pine Script 자체 주문 실행 불가 (외부 봇 필수)

## [2026-04-11] Cycle 36 — Futures vs Spot Bots
- 선물 봇: 레버리지(5~10x 이하 권장)로 고수익 가능하나 청산 리스크 높음, 수수료·펀딩비 누적 부담
- 현물 봇: 청산 없음, 그리드·리밸런싱에 적합, 변동성 낮은 시장에서 안정적
- 성과 차이는 전략·리스크 관리에 더 의존, 봇 유형 자체보다 파라미터·시장 레짐 적합성이 관건


## [2026-04-11] Cycle 48 — Bot Backup/DR (직접 기록, F agent 미완료)

- 상태 저장: 포지션, 주문, 전략 상태를 SQLite/Redis에 지속 저장
- 주문 복구: 거래소 API로 startup 시 open orders 조회 + 로컬 상태 동기화
- DR 체크리스트: 주기적 state snapshot, config 백업, API key 별도 보관
- 업계 표준: 봇 crash 시 30초 내 재시작 + 포지션 일치 검증 필수

(F 리서치 에이전트가 중단되어 기본 지식 기반으로 작성)

## [2026-04-14] Cycle 121 — Failure/Success Cases & 2025-2026 Quant Trends

### 실패 케이스

**사례 1: AI 봇 집단 패닉셀 (2025년 5월)**
- 암호화폐 플래시 크래시 시 AI 봇들이 3분 만에 20억 달러 매도 실행
- 정상 시장 조건 전용으로 설계되어 급격한 변동성에 대응 불가
- 교훈: 레짐 전환 감지 로직과 서킷브레이커 없으면 군집 손실 발생

**사례 2: dogwifhat 대형 슬리피지 손실 (2024년 1월)**
- 900만 달러 시장가 주문이 오더북 얕아 570만 달러 슬리피지 발생 (60% 체결가 급등)
- 교훈: 유동성 필터 없는 대형 주문은 치명적, 분할 주문·TWAP 필수

**사례 3: Kronos Research API 해킹 (2024년)**
- API 키 유출로 2,600만 달러 손실
- 교훈: API 키 권한 최소화(거래 전용, 출금 불허), 주기적 키 교체, IP 화이트리스트 필수

**공통 실패 패턴:**
- 과최적화: 15개 이상 파라미터 전략은 라이브에서 거의 실패
- 실제 백테스트 대비 30~50% 성과 저하 (슬리피지·수수료 미반영)
- 6개월 내 73%의 자동화 계좌가 실패

### 성공 케이스

**사례 1: Bitsgap GRID/DCA 봇 커뮤니티 사례**
- 4개월 125% + 2개월 추가 23% 수익 달성
- 성공 요인: 커뮤니티 전략 공유, 명확한 시장 레짐(횡보장) 활용

**사례 2: Hummingbot 마켓메이킹 봇**
- 2021년부터 운영, 알고트레이딩 스타트업으로 발전한 사례
- 오픈소스 기반 반복 개선 + 커뮤니티 피드백 루프가 핵심

### 2025~2026 퀀트 전략 트렌드

**트렌드 1: ML 다중 팩터 모델 (Ethereum/Crypto 적용)**
- RSI·모멘텀 기술 지표 + 온체인 데이터(가스비, 활성 주소) + ML 파생 팩터 결합
- 500~1,000개 팩터를 롤링 윈도우(5~252일)로 처리, 강세장에서 연 130% 달성 사례
- 바이어스 보정(bias correction)을 적용한 크로스섹션 포트폴리오 최적화가 주목받는 중

**트렌드 2: LLM/멀티에이전트 자동화 파이프라인**
- QuantEvolve 등 멀티에이전트 진화 프레임워크로 알파 팩터 자동 발굴
- GPT-4/5 기반 봇이 고변동성 구간에서 인간 트레이더 대비 15~25% 아웃퍼폼 보고
- 인텐트 기반 온체인 자동 실행으로 CEX→DEX 확장 가속화

### 핵심 교훈 3줄

1. **슬리피지·유동성 필터는 선택 아닌 필수** — 대형 주문 전 오더북 깊이 확인, TWAP/분할 주문 적용
2. **과최적화 방지가 수익률보다 우선** — 파라미터 수 최소화 + walk-forward 검증 통과 전략만 배포
3. **보안과 서킷브레이커 없으면 전략 성능은 무의미** — API 권한 최소화, 일일 MDD 한도, 레짐 감지 필수

### 참고 출처
- [Why Most Trading Bots Lose Money — ForTraders](https://www.fortraders.com/blog/trading-bots-lose-money)
- [Common Pitfalls in Crypto Bot Trading — Bitunix](https://blog.bitunix.com/en/common-pitfalls-crypto-trading-bots/)
- [7 Hidden Risks of Crypto Bots — Altrady](https://www.altrady.com/blog/crypto-bots/7-hidden-risks)
- [Hummingbot Open Source Framework](https://hummingbot.org/)
- [ML Multi-Factor Quantitative Model: Ethereum — ACM 2025](https://dl.acm.org/doi/10.1145/3766918.3766922)
- [QuantEvolve: Multi-Agent Strategy Discovery — arXiv](https://arxiv.org/html/2510.18569v1)


## [2026-04-15] Cycle 123 Research

### 실패 사례

1. **AI 봇 $441K 토큰 오발송 (Lobstar Wilde, 2026년 2월)** — OpenAI 개발자가 만든 자율 에이전트가 상태 손실 + 잔고 오판으로 5,243만 LOBSTAR 토큰(약 $250K~$441K 상당)을 임의 사용자에게 전송. 원인: 크래시 후 컨텍스트 복구 실패, 지갑 잔고 모델 오작동. 교훈: 자율 에이전트에 불가역 트랜잭션 전 인간 확인 단계 필수.

2. **Bitget 내부 봇 로직 익스플로잇 (2025년)** — 8개 계정이 거래소 마켓메이커 봇의 비정상 호가 취약점을 파악, VOXEL 토큰을 과매도 가격에 매수 후 과매수 가격에 매도해 약 $1억 이득. 원인: 봇 호가 로직 결함 + front-running. 교훈: 거래소 봇의 호가 범위 이상 탐지 + rate anomaly 모니터링 필수.

3. **DeBot AI DeFi 툴 해킹 ($255K, 2025년)** — 일본 서버 익스플로잇으로 $255K 손실. 원인: 서버 보안 취약점. 교훈: 봇 서버 접근 최소화, API 키 권한 제한, 거래 전용 키 분리 운영.

4. **Nova Trading Platform 보안 침해 ($500K, 2025년 9월)** — 수동 공격으로 $50만 상당 암호화폐 탈취. 교훈: 플랫폼 수준 보안도 단일 장애점 — 다중 인증 + 출금 화이트리스트 필수.

5. **May 2025 AI 봇 플래시 크래시 가속** — 갑작스러운 변동성에 적응하지 못한 AI 봇들이 3분 내 $20억 자산 매도. 원인: 레짐 감지 로직 부재. 교훈: 고변동성 레짐 진입 시 봇 일시 중단 또는 포지션 크기 자동 축소 필수.

### 성공 사례

1. **보수적 AI DCA 전략 (2025년)** — 변동성 구간에서 30일 12.8% 수익, 성공률 100%. 6개월 누적 193% ROI 사례도 존재. 핵심: 명확한 진입·청산 규칙 + 포지션 제한으로 드로다운 최소화.

2. **커스텀 퀀트 봇 다중 거래소 운영** — 연환산 42% 수익, Sharpe 2.3, MDD 9% 달성. 핵심 요인: 24/7 다중 거래소 분산 + 엄격한 1% 포지션 룰 + 낮은 레버리지.

3. **Qwen 기반 소형 LLM 봇** — GPT-5보다 높은 성과. 핵심 요인: 더 작은 포지션 사이징 + 빠른 손절 실행. 지능보다 규율(discipline)이 우선임을 입증.

### 트렌드

- **Hybrid RL + Transformer**: CNN-PPO·Attention-DDPG 등 RL+Transformer 하이브리드가 순수 RL 대비 15~20% 성과 향상. 하이브리드 채택률 2020년 15% → 2025년 42%로 급증.
- **LLM-DRL 통합 파이프라인**: PrimoGPT(금융 텍스트 파인튜닝) + PrimoRL(DRL 상태 공간 확장) 결합 방식이 주목. NLP 감성·트렌드 피처를 DRL 의사결정에 통합.

### 참고 출처
- [AI Trading Bots Lost $441K — Medium/Pump Parade](https://pumpparade.medium.com/ai-trading-bots-lost-441k-in-one-error-heres-what-actually-works-and-what-doesn-t-4f04f890c189)
- [Crypto Hacking Incidents 2025 — DeepStrike](https://deepstrike.io/blog/crypto-hacking-incidents-statistics-2025-losses-trends)
- [Biggest Crypto Hacks 2025 — The Block](https://www.theblock.co/post/380992/biggest-crypto-hacks-2025)
- [Ethereum MEV Bot Exploit 2025 — Gate.com](https://www.gate.com/crypto-wiki/article/ethereum-mev-bot-exploit-impact-on-defi-and-mitigation-strategies-in-2025)
- [Deep Learning for Algo Trading Review — ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2590005625000177)
- [LLM-Driven DRL Trading Framework — MDPI](https://www.mdpi.com/2504-2289/9/12/317)


## [2026-04-18] Cycle 148 — 봇 실패/성공 케이스 및 최신 퀀트 논문

### 봇 실패 패턴 (2024~2026 업데이트)

- **과적합(Overfitting) 위험 재확인**: 888개 알고 전략 연구에서 백테스트 Sharpe와 실전 Sharpe의 R² < 0.025 — 상관관계 거의 없음. 44%의 전략이 새로운 데이터에서 재현 실패. 본 봇의 355개 전략 중 실전 통과 0개와 일치.
- **레짐 변화 무방비**: 2025년 5월 AI봇 플래시 크래시 — 정상 시장용 설계된 봇이 3분 내 $2B 매도. 레짐 감지 없는 단일 전략 운영의 전형적 실패. Grid-trading 봇은 추세 구간에서 대규모 손실.
- **73% 6개월 내 실패**: 주원인 3가지 — (1) 리스크 관리 부재, (2) 과최적화, (3) 레짐 변화 무대응. 세 요인 모두 본 프로젝트가 이미 식별한 문제와 동일.

### 성공 봇의 공통 특징

1. **Walk-forward 검증 필수**: 백테스트 아닌 실전 데이터 롤링 검증을 통해 레짐 의존성 제거.
2. **규율(Discipline) > 지능(Intelligence)**: Qwen 소형 LLM 봇이 GPT-5 기반보다 우수 — 빠른 손절 + 작은 포지션이 결정적. 복잡한 모델보다 엄격한 규칙이 우선.
3. **다중 레짐 적응**: 상승/하락/횡보 3개 레짐을 명시적으로 구분하고 전략 전환. 단일 전략 운영 금지.
4. **레버리지 제한**: 성공 봇들의 공통점 — 낮은 레버리지 + 1% 포지션 룰.

### 최신 퀀트 논문 요약 (2024~2026)

1. **Directional Change + Meta-Learning (Razmi & Barak, 2024)**
   - DC(방향 변화) 방식: 고정 시간 간격 아닌 유의미한 가격 움직임 기준으로 샘플링 → 레짐 변화에 민감.
   - Meta-learning 레이어가 온체인 데이터(BTC/ETH), DC 지표, 레짐 통계 4개 피처셋 기반으로 하이퍼파라미터 자동 조정.
   - 결과: 수익률 최대 10배, Sharpe 3배 향상. Binance 선물 2021~2024년 검증.
   - 출처: [SSRN 5017215](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5017215)

2. **Regime-Switching RL for Crypto Portfolio (2025)**
   - 변동성 + 수익률 분위수 기반 3개 레짐 정의 → 레짐별 RL 모델 전환.
   - 레짐 전환 시 포지션 자동 조정 — 단일 RL 대비 안정성 향상.
   - 출처: [Springer Digital Finance](https://link.springer.com/article/10.1007/s42521-024-00123-2)

3. **DQN 기반 전략 선택 RL (2025, TandFonline)**
   - 사전 정의된 기술 전략들 중 DQN이 선택 — 블랙박스 회피, 해석 가능성 + 안정성.
   - 단일 전략 대비 변동성 감소, 해석 가능성 향상.
   - 출처: [TandFonline](https://www.tandfonline.com/doi/full/10.1080/23322039.2025.2594873)

4. **Regime-Conditional RL Reward Functions (MDPI, 2026)**
   - 경제 효용 이론 기반 보상 함수 + 레짐 조건부 최적화.
   - 레짐별 성과 이질성 분석: 동일 전략이 레짐에 따라 수익/손실 크게 다름 → 레짐 필터 없이는 평균 성과가 의미 없음.
   - 출처: [MDPI Mathematics](https://www.mdpi.com/2227-7390/14/5/794)

### 우리 봇에 대한 시사점

1. **DC 방법론 검토 가능성**: 시간 기반이 아닌 가격 움직임 기반 이벤트 샘플링이 레짐 변화 포착에 우수. ML 모델의 입력 피처로 활용 검토.
2. **레짐별 ML 모델 분리**: 현재 단일 ML 2-class 모델 → 레짐별(TREND_UP/RANGING/TREND_DOWN) 별도 모델 또는 레짐 피처 추가.
3. **DQN 전략 선택기**: 기존 355개 전략 중 레짐별 상위 전략을 DQN으로 선택하는 메타-레이어 접근법 — 신규 전략 추가 없이 기존 전략 활용 극대화.

### 참고 출처

- [Why Trading Bots Lose Money — ForTraders](https://www.fortraders.com/blog/trading-bots-lose-money)
- [AI Trading Bots 2025 Reality — AgentiveAIQ](https://agentiveaiq.com/blog/is-ai-bot-trading-profitable-the-2025-reality-check)
- [Adaptive Crypto Trading DC + Meta-Learning — SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5017215)
- [Regime Switching Forecasting Crypto — Springer](https://link.springer.com/article/10.1007/s42521-024-00123-2)
- [DQN Strategy Selection — TandFonline](https://www.tandfonline.com/doi/full/10.1080/23322039.2025.2594873)
- [Regime-Conditional RL Rewards — MDPI](https://www.mdpi.com/2227-7390/14/5/794)
- [ML Crypto Trading Comparative Analysis — Springer](https://link.springer.com/article/10.1007/s44163-025-00519-y)


## [2026-04-18] Cycle 149 — ETH/SOL ML 개선 + Online Learning

### 1. ETH/SOL이 BTC보다 예측하기 어려운 이유

**시장 미시구조 차이**
- SOL 변동성 ~80%, ETH ~60%, BTC ~41% — 알트코인 변동성이 BTC의 2배 이상. 노이즈 대비 시그널 비율이 낮아 동일 모델 구조가 BTC보다 낮은 정확도를 냄.
- BTC-SOL 상관계수 0.99로 장기 동조화가 강하지만, 내러티브 이벤트(DeFi 시즌, NFT, 밈코인 등) 발생 시 상관관계가 급격히 이탈 — 상관관계 기반 피처가 비정상 시점에 오히려 혼란을 줌.
- ETH는 가스 사용량·스마트 컨트랙트 활동 등 온체인 피처에 크게 반응하나 BTC에는 없는 DeFi 레짐이 별도로 존재 — 동일 피처셋 사용 시 ETH/SOL에서 모델 오버피팅 발생.

**내러티브 드리븐 가격 형성**
- 알트코인은 단기 내러티브(에어드랍, 업그레이드, 고래 매집)에 의해 짧은 랠리를 반복. 기술적 패턴보다 이벤트 감응도가 높아 과거 OHLCV 기반 ML의 예측력이 구조적으로 낮음.
- BTC 관련 마이크로구조 피처(BTC Roll, BTC VPIN)가 ETH/SOL 예측에 강한 설명력을 보임 — 알트코인 과거 가격보다 BTC 미시구조 변수가 더 유용한 입력.

**추천 피처 추가 방향 (ETH/SOL 전용)**
- BTC 미시구조 시차 피처: BTC_close_lag1, BTC_roll, BTC_VPIN
- 온체인: ETH 가스 사용량, 활성 주소수 (ETH 전용)
- 유동성 깊이(order book depth) 변화율
- 변동성 레짐 레이블 (ATR 분위수 기반 3단계)
- 감성 피처: RoBERTa 기반 뉴스/소셜 감성 (Bi-LSTM 조합 시 MAPE 2.01% 달성 사례)

**추천 아키텍처 변경**
- 단일 2-class 모델 → 레짐별 서브모델 (TREND_UP/RANGING/TREND_DOWN)
- 앙상블: LSTM + GRU 결합 또는 Gradient Boosting + 감성 피처 레이어 추가
- 출처: [ETH Multi-Factor ML — ACM ICAIF 2025](https://dl.acm.org/doi/10.1145/3766918.3766922), [Deep Learning Crypto Forecasting — ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0169207025000147)

---

### 2. Online / Incremental Learning 리서치

**핵심 라이브러리**

| 라이브러리 | 특징 | 크립토 적합성 |
|---|---|---|
| **River** | Python 딕셔너리 스트림 입력, 가독성 우수, partial_fit 패턴 | 코드 통합 용이, 소규모 봇에 적합 |
| **Vowpal Wabbit (VW)** | 해싱 기반 고속 온라인 학습, 능동/대화형 학습 지원 | 고빈도 틱 데이터 처리에 유리 |
| **scikit-learn `partial_fit`** | SGDClassifier, MiniBatchKMeans 등 점진적 학습 지원 | 기존 sklearn 파이프라인 재사용 가능 |

**크립토 트레이딩에서의 적용 사례**
- 실시간 ML 파이프라인은 데이터가 도착하는 즉시 학습하므로 컨셉 드리프트(시장 레짐 변화)에 빠르게 적응. 주기적 재학습(배치) 대비 레짐 전환 후 반응 지연이 없음.
- Meta-RL-Crypto (arXiv 2509.09751) 에서 BTC/ETH/SOL 대상으로 OHLCV + 거래량 + 시총 피처 기반 메타-보상 자기개선 구조 적용 — 온라인 업데이트와 결합 시 드리프트 대응 효율 증가.
- 실전 주의점: River/VW는 배치 모델보다 단기 노이즈에 과반응 위험. 학습률(learning rate) 감쇠 또는 윈도우 제한(sliding window) 필수.

**우리 봇에 대한 시사점**
1. **단기 적용 방향**: 기존 배치 ML 모델 유지 + River SGDClassifier로 온라인 보조 모델 추가 → 두 모델의 합의(앙상블 voting) 시에만 신호 발생.
2. **중기 방향**: ETH/SOL 전용 온라인 학습 레이어 — 레짐 전환 후 24시간 내 자동 가중치 조정.
3. **구현 위치**: `src/strategy/ml_strategy.py` 또는 `src/data/` 파이프라인 내 스트리밍 피처 처리 모듈로 통합.

---

### 우리 봇 적용 우선순위

1. **ETH/SOL 피처 추가 (단기)**: BTC 미시구조 시차 피처 + ATR 레짐 레이블 추가 → 별도 배치 재학습으로 성능 개선 시도.
2. **레짐별 서브모델 분리 (중기)**: 현재 단일 모델 → 3개 레짐별 분리 모델, ETH/SOL 정확도 향상 기대.
3. **River 보조 온라인 모델 (중기)**: 기존 배치 모델 + River 온라인 모델 앙상블로 레짐 드리프트 대응력 강화.

### 참고 출처

- [BTC Microstructure and Altcoin Prediction — Cornell/ACM](https://stoye.economics.cornell.edu/docs/Easley_ssrn-4814346.pdf)
- [ETH Multi-Factor ML — ACM ICAIF 2025](https://dl.acm.org/doi/10.1145/3766918.3766922)
- [Deep Learning + On-Chain + Sentiment — ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0169207025000147)
- [Sentiment-Driven LSTM/GRU Crypto Forecasting — Springer](https://link.springer.com/article/10.1007/s13278-025-01463-6)
- [River + Vowpal Wabbit Real-Time ML — Rotational Labs](https://rotational.io/blog/realtime-machine-learning/)
- [Meta-RL-Crypto Online Learning — arXiv](https://arxiv.org/html/2509.09751v1)
- [ETH/SOL Correlation & Volatility 2026 — Dropstab](https://dropstab.com/research/crypto/solana-ethereum-correlation-and-volatility)

---

## [2026-04-18] Cycle 150 — CPCV & 메타-라벨링 리서치

### 1. CPCV (Combinatorial Purged Cross-Validation)

#### 개요
- Lopez de Prado가 제안한 금융 ML 전용 교차검증. 표준 k-fold와 달리 시계열 데이터의 정보 누출(leakage)을 방지.
- 핵심 메커니즘 2가지:
  - **Purging**: 학습셋에서 테스트 레이블 기간과 겹치는 구간 제거 → 미래 정보 유입 차단
  - **Embargo**: 각 테스트 구간 이후 n개 바를 학습셋에서도 제외 → 지연된 자기상관 leakage 방지
- 단일 경로(single path) 백테스트 대신 **다수의 백테스트 경로 분포**를 생성 → 전략 성과의 통계적 신뢰도 확보

#### WF(Walk-Forward) 대비 CPCV 장단점

| 항목 | Walk-Forward | CPCV |
|---|---|---|
| 과적합 탐지 | 단일 경로 의존, 취약 | PBO(Probability of Backtest Overfitting) 계산 가능 |
| 정보 누출 | Embargo 없으면 누출 위험 | Purging+Embargo로 체계적 차단 |
| 구현 복잡도 | 단순 | 복잡 (조합 수 C(N,k) 폭발) |
| 결과 해석 | 단일 Sharpe | Sharpe 분포 + DSR(Deflated Sharpe Ratio) |
| 크립토 적합성 | 현재 우리 봇 사용 중 | 높은 편향-분산 트레이드오프 개선 |

#### mlfinlab vs 자체 구현 비교
- **mlfinlab**: `CombinatorialPurgedKFold` 클래스 제공. 설치 시 상용 라이선스 문제 있음 (오픈소스 버전 제한적).
- **skfolio**: `CombinatorialPurgedCV` 무료 구현체. sklearn 호환 API.
- **자체 구현**: quantbeckman.com 코드 참고 시 ~100줄로 구현 가능. Embargo 파라미터 커스터마이징 자유도 높음.
- **권장**: skfolio 또는 자체 구현. mlfinlab 유료 버전 불필요.

#### 우리 봇 현황과의 연결
- 현재 WF 검증에서 355+ 전략 모두 실패(실전 데이터 기준). 이는 단일 경로 의존 + purging 미적용이 원인일 가능성 높음.
- CPCV 도입 시 → Sharpe 분포 확인 → 진짜 엣지 있는 전략 vs 운 좋은 전략 구분 가능.
- **구현 대상**: `src/backtest/engine.py`에 CPCV 모드 옵션 추가 고려.

---

### 2. 메타-라벨링 (Meta-Labeling)

#### 개요 (Lopez de Prado, 2018)
- Triple Barrier Method + 2단계 ML 구조
- **1차 모델**: 방향 예측 (UP/DOWN) — 기존 전략/사이드 신호
- **2차 모델(메타-라벨러)**: 1차 모델의 신호를 받아 "이 신호를 실행할지 말지"를 예측
  - 출력: Precision/Recall 개선, F1 Score 최적화
  - 핵심: 1차 모델이 틀렸을 때 걸러내는 필터 역할

#### Triple Barrier 레이블링
- 각 진입점마다 3개 배리어 설정:
  - **상단 배리어**: 익절 목표 (예: +2% ATR 기반)
  - **하단 배리어**: 손절 (예: -1% ATR 기반)
  - **수직 배리어**: 최대 보유 시간 (예: 24시간)
- 첫 배리어 도달 시 레이블 결정 → 단순 UP/DOWN보다 실제 트레이딩 로직 반영

#### Binary UP/DOWN vs 메타-라벨링 비교

| 항목 | Binary UP/DOWN (현재) | 메타-라벨링 |
|---|---|---|
| 레이블 정의 | n개 바 후 종가 상승 여부 | 실제 TP/SL 도달 여부 |
| 클래스 불균형 | 50:50 강제 | 자연스러운 분포 반영 |
| 거래 실행 여부 | 항상 실행 | 2차 모델이 필터링 |
| Precision | 낮음 (노이즈 많음) | 높아짐 (실행 건 선별) |
| 구현 복잡도 | 단순 | 2단계 파이프라인 필요 |
| 크립토 2024-2025 연구 | 기본 방식 | Triple Barrier가 BTC/ETH에서 우월 확인 |

#### 크립토 적용 사례 (2024~2025)
- Springer Nature 2025 논문: Information-driven bars + Triple Barrier + 딥러닝 조합이 BTC/ETH에서 우월한 성과.
- MDPI 2024: GA-driven Triple Barrier + ML이 크립토 페어 트레이딩에서 성과 개선.
- Medium 실험: 크립토 시장 메타-라벨링 적용 시 Precision 유의미하게 향상, 과매매(overtrading) 감소.
- **결론**: 메타-라벨링이 현재 binary 분류보다 실전 트레이딩에 더 적합. 특히 레버리지 크립토에서 거짓 신호 필터링 효과 큼.

---

### Cycle 150 우리 봇 적용 우선순위

1. **단기 — 메타-라벨링 파일럿**: `src/strategy/ml_strategy.py`의 RF 분류기에 Triple Barrier 레이블 추가. 현재 63.5% 정확도 → Precision 개선 목표.
2. **중기 — CPCV 도입**: `src/backtest/engine.py`에 skfolio의 `CombinatorialPurgedCV` 통합. 현재 WF 실패 원인이 단일 경로 과적합인지 검증.
3. **주의사항**: CPCV는 계산 비용이 WF 대비 C(N,k)배 높음 — N=10, k=2 기준 45배. 전략 수 355+에 일괄 적용 시 실행 시간 문제 → 상위 후보 전략만 선별 적용 권장.

### 참고 출처

- [mlfinlab CPCV 공식 문서](https://www.mlfinlab.com/en/latest/cross_validation/cpcv.html)
- [quantbeckman CPCV 코드 구현](https://www.quantbeckman.com/p/with-code-combinatorial-purged-cross)
- [skfolio CombinatorialPurgedCV](https://skfolio.org/generated/skfolio.model_selection.CombinatorialPurgedCV.html)
- [ScienceDirect: WF vs CPCV 오버피팅 비교](https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110)
- [Hudson & Thames: 메타-라벨링 효과 검증](https://hudsonthames.org/does-meta-labeling-add-to-signal-efficacy-triple-barrier-method/)
- [Springer: Triple Barrier + 딥러닝 크립토 2025](https://link.springer.com/article/10.1186/s40854-025-00866-w)
- [MDPI: GA-Triple Barrier 크립토 페어 트레이딩 2024](https://www.mdpi.com/2227-7390/12/5/780)
- [Medium: 크립토 메타-라벨링 실험](https://medium.com/@liangnguyen612/meta-labeling-in-cryptocurrencies-market-95f761410fac)

---

## [2026-04-18] Cycle 151 — Concept Drift Detection & 동적 Feature Selection

### 1. Concept Drift Detection 비교

#### ADWIN (Adaptive Windowing)
- **원리**: 가변 길이 슬라이딩 윈도우 유지. 윈도우 내 두 부분 구간의 평균 차이가 통계적 임계값 초과 시 드리프트 감지. 수학적 보장(PAC 학습) 있음.
- **장점**: 점진적 드리프트에도 자동 윈도우 크기 조정, 임계값 사전 설정 불필요
- **단점**: 메모리 사용량이 데이터 복잡도에 비례 증가, 갑작스러운 급변에는 반응 속도 느림
- **River 구현**: `from river.drift import ADWIN` — 온라인 학습 파이프라인에 즉시 통합 가능

#### DDM (Drift Detection Method)
- **원리**: 모델의 예측 오류율 모니터링. PAC 학습 기반으로 정상 분포에서 오류율 감소 가정. 오류율이 경고/드리프트 임계값 초과 시 알람.
- **장점**: 예측 오류율 직접 감시 → 실제 모델 성능 저하 시점과 연동, 계산 효율 높음
- **단점**: 분류 모델에 최적화(연속값 예측엔 변형 필요), 초기 학습 구간 필요
- **River 구현**: `from river.drift.binary import DDM` — 이진 오류(0/1) 스트림에 사용

#### Page-Hinkley (PH)
- **원리**: 관측값의 누적 편차가 사전 설정 임계값 초과 시 평균 변화 감지. 단일 데이터포인트 처리, 전체 스트림 저장 불필요.
- **장점**: 실시간 처리에 최적, 메모리 효율 최고, 계산 비용 O(1)
- **단점**: 점진적 드리프트 감지 약함(급격한 변화 전용), 임계값 수동 설정 필요
- **River 구현**: `from river.drift import PageHinkley`

#### 우리 봇 권장 조합
- **1단계 실시간 감시**: PageHinkley — 급격한 레짐 전환(2026-03~04 같은 경우) 즉각 감지
- **2단계 점진적 드리프트**: ADWIN — 서서히 변하는 feature 분포 변화 추적
- **트리거**: DDM으로 모델 예측 오류율 감시 → 경고 레벨 시 재학습 준비, 드리프트 레벨 시 즉시 재학습

---

### 2. 재학습 시점 자동 판단 기준

| 조건 | 행동 |
|------|------|
| DDM 경고(warning) 레벨 도달 | 최근 데이터 버퍼 수집 시작, 백그라운드 재학습 준비 |
| DDM 드리프트 레벨 OR PageHinkley 감지 | 즉시 재학습 트리거, 현재 모델 가중치 감소 |
| ADWIN 윈도우 급격히 축소 | 점진적 드리프트 확인, 주 1회 → 일 1회 재학습 주기 단축 |
| 3일 연속 Sharpe < 0.5 (실전 성과) | 레짐 변화 의심, 강제 재학습 |

현재 ML 모델 FAIL 원인(2026-03~04 레짐 변화)은 PageHinkley + DDM 조합이면 사전 감지 가능했을 케이스.

---

### 3. 동적 Feature Selection (레짐 변화 대응)

#### Boruta 방식
- **원리**: 원본 피처의 무작위 셔플 버전(Shadow Feature) 생성 후 랜덤포레스트 중요도 비교. Shadow 대비 통계적으로 유의미한 피처만 선택.
- **레짐 적용**: 레짐 전환 감지 시 해당 레짐 데이터만으로 Boruta 재실행 → 레짐별 중요 피처 세트 관리
- **단점**: 계산 비용 높음(반복 RF 학습), 실시간 적용 어려움 → 주기적 오프라인 실행 적합

#### BorutaSHAP (권장)
- **원리**: Boruta에서 RF 중요도 대신 SHAP 값 사용. Wasserstein 거리로 SHAP 값 분포의 드리프트 점수 계산 가능.
- **시간 가중 SHAP**: 최근 데이터에 높은 가중치 부여하는 decay 함수 적용 → 레짐 전환 후 새 중요 피처를 빠르게 포착
- **라이브러리**: `BorutaShapPlus` (pip 설치 가능)
- **실전 적용**: ADWIN이 드리프트 감지 시 → BorutaSHAP 재실행 → 피처 세트 업데이트 → 모델 재학습 파이프라인

#### SHAP 기반 피처 드리프트 감시
- SHAP 값의 시간별 분포 변화 = 피처 중요도 드리프트 지표
- Wasserstein 거리로 이전 기간 vs 현재 기간 SHAP 분포 비교 → 임계값 초과 시 재선택 트리거
- **이점**: 모델 성능 저하 이전에 피처 레벨에서 조기 경보 가능

---

### 4. 우리 봇 적용 우선순위 (Cycle 151)

1. **단기 — River Drift Detector 통합**: `src/strategy/ml_strategy.py` 또는 별도 `src/ml/drift_monitor.py` 생성. PageHinkley로 예측 오류 스트림 감시, DDM으로 재학습 트리거 자동화. River 이미 온라인러닝 기반으로 사용 중이므로 추가 의존성 없음.

2. **중기 — BorutaSHAP 주기적 재선택**: 현재 고정된 피처 세트를 레짐별로 관리. ADWIN 드리프트 감지 시 or 매주 월요일 BorutaSHAP 재실행 → `config/feature_sets.json`에 레짐별 피처 저장.

3. **주의사항**: Boruta 단독은 계산 비용 과다(355+ 전략에 일괄 적용 불가). SHAP-only 경량 버전 먼저 적용 권장.

### 참고 출처

- [River ADWIN 공식 문서](https://riverml.xyz/dev/api/drift/ADWIN/)
- [River DDM 공식 문서](https://riverml.xyz/dev/api/drift/binary/DDM/)
- [River Concept Drift 가이드](https://riverml.xyz/dev/introduction/getting-started/concept-drift-detection/)
- [Page-Hinkley 방법론 설명](https://www.geeksforgeeks.org/artificial-intelligence/page-hinkley-method/)
- [Springer: Page-Hinkley 개념 드리프트 감지](https://link.springer.com/chapter/10.1007/978-981-97-8946-7_3)
- [Temporal SHAP 동적 피처 중요도](https://www.academia.edu/165470033/Temporal_SHAP_Analysis_for_Dynamic_Feature_Importance_in_Streaming_Transaction_Data_Achieving_Explainability_and_Fairness_in_Real_Time_AML_Detection_Systems)
- [SHAP 안정성 및 드리프트 점수](https://ceur-ws.org/Vol-4059/paper14.pdf)
- [BorutaSHAP for Temporal Feature Selection (TDS)](https://towardsdatascience.com/boruta-shap-for-temporal-feature-selection-96a7840c7713/)
- [BorutaShapPlus 라이브러리](https://medium.com/@originallyretro/introducing-borutashapplus-feature-selection-via-boruta-and-shapley-values-3cf1fd9b368e)
- [DataCamp: Data Drift & Model Drift 파이썬 구현](https://www.datacamp.com/tutorial/understanding-data-drift-model-drift)

---

## [2026-04-18] Cycle 152 Research — 포지션 사이징 최적화 & 실전 봇 운영 사례

### 1. 포지션 사이징 방법론 비교

#### Kelly Criterion (켈리 공식)
- 공식: `Kelly% = (W × R - L) / R` (W=승률, L=1-W, R=손익비)
- 크립토 특성상 **Full Kelly는 위험** — BTC 30일 실현 변동성이 30~45%로 전통 자산 대비 30~45배 높음
- 실전 권장: **Quarter Kelly (0.25×Kelly)** 또는 그 이하, 입력값 추정 오차가 결과에 과도한 영향
- 포트폴리오 노출 6% 이하, 단일 트레이드 1% 이하가 실전 기준

#### Optimal-F (최적 f)
- Ralph Vince의 방법론: 실제 트레이드 히스토리로 기하학적 성장을 극대화하는 f값 역산
- 단순 승률 대신 트레이드 분포 패턴 + 드로다운 내성까지 반영
- 실전 optimal f 범위: **0.1~0.3 (10~30%)** — Kelly보다 보수적이나 더 정확
- 크립토 레짐 변화 시 히스토리 기반 f값이 무효화될 수 있음 → 정기 재계산 필수

#### Fixed Fractional (고정 비율)
- 매 트레이드마다 총자본의 고정% 위험: 자본 증가 시 절대 포지션 자동 증가, 손실 시 자동 감소
- Balsara(1992) 연구: 다른 방법 대비 **가장 매끄러운 에퀴티 커브** 생성
- 크립토 실전: **1~2% 고정** 권장. 저변동성 → 1%, 고변동성 → 0.5%
- 단순하여 레짐 추정 오류로 인한 과최적화 위험 없음

#### Risk Parity (리스크 패리티)
- 각 포지션의 변동성 기여분이 동일하도록 역변동성 가중
- 기관급 도구 — 상관관계/VaR 모델링, 빈번한 리밸런싱 필요
- 크립토에서 **상관관계가 시장 스트레스 시 급등** → 리스크 패리티가 깨지는 타이밍이 가장 위험
- 실전 적용: 단일 알트코인 최대 5~8%, BTC/ETH 코어 포지션 역변동성 비중

---

### 2. 레짐별 사이징 전환 전략

| 레짐 | 사이징 방법 | 위험/트레이드 | 비고 |
|------|------------|--------------|------|
| 저변동성 상승추세 | Kelly-Lite 또는 Optimal-F | 1.5~2% | 에지 확실할 때 증가 |
| 고변동성 | Fixed Fractional 축소 | 0.5~0.75% | Kelly값 25~50% 삭감 |
| 횡보/불확실 | Fixed Fractional 보수적 | 0.5~1% | 현금 50~70% 유지 |
| 하락장 | Fixed Fractional 최소 | 0.5% | 스테이블 50~80% 유지 |

핵심 원칙: **레짐 전환 시 사이징을 먼저 줄이고, 전략 성과가 확인된 후 증가**

---

### 3. 실전 크립토 봇 운영 사례 (2025~2026)

#### 성공 사례 — SaintQuant (2025-03 변동성 기간)
- $10,000 포지션 기준 전략 파라미터 실시간 자동 조정
- **연환산 42% 수익, MDD 11%** (시장이 주 30% 하락 가능한 환경)
- 자동화 시스템 MDD 4.6% vs 수동 트레이딩 훨씬 높은 MDD

#### 드로다운 관리 핵심 원칙
- **회복의 비대칭성**: 10% 손실 → 11.1% 이익 필요, 20% 손실 → 25%, 50% 손실 → 100%
- 드로다운 방지가 수익 극대화보다 기하급수적으로 중요
- 성공 봇의 공통: **다층 서킷브레이커** (일일 3% + 주간 7%), **볼라틸리티 필터**, **수동 오버라이드**

#### 포지션 사이징 2% 룰 (실전 공식)
```
포지션 크기 = 포트폴리오 × 2% ÷ 손절 거리(%)
예시: 손절 20% → 포지션 = 10%, 손절 50% → 포지션 = 4%
```

#### AI 리스크 관리 트렌드 (2025~2026)
- 변동성 예측 기반 노출 조절이 핵심 (근거리 분산 추정)
- 과거 고정 파라미터 → **연속적 적응형 사이징**으로 전환 중
- 포트폴리오 집중도 모니터링: 단일 자산 최대 5~8%

---

### 4. 우리 봇 적용 우선순위 (Cycle 152)

1. **단기 — ATR 기반 동적 사이징**: `src/risk/` 에서 현재 ATR(14) 값 기반으로 포지션 크기를 실시간 조정. 고변동성(ATR > 2×중간값) 시 Fixed Fractional을 0.5%로 자동 축소.

2. **중기 — 레짐별 사이징 파라미터**: `src/risk/position_sizer.py` (또는 해당 모듈)에 레짐(상승/횡보/하락/고변동) 태그별 다른 f값 적용. 현재 ML 모델 FAIL 상황에서 단순 Fixed Fractional 0.5~1%가 가장 안전.

3. **주의사항**: Optimal-F는 355+ 전략 각각에 히스토리 기반 f 계산이 필요하므로 단기 적용은 과부하. 먼저 Fixed Fractional 0.5~1% + ATR 배율 조정 조합 적용 후, 충분한 실거래 데이터 축적 후 Optimal-F 전환 검토.

### 참고 출처

- [Kelly Criterion for Crypto (Medium, 2026)](https://medium.com/@tmapendembe_28659/kelly-criterion-for-crypto-traders-a-modern-approach-to-volatile-markets-a0cda654caa9)
- [Beware of Excessive Leverage: Kelly & Optimal-F (QuantPedia)](https://quantpedia.com/beware-of-excessive-leverage-introduction-to-kelly-and-optimal-f/)
- [Position Sizing Methods: 7 Techniques (TradeFundrr)](https://tradefundrr.com/position-sizing-methods/)
- [ATR-Based & Kelly-Lite Frameworks (Medium)](https://medium.com/@ildiveliu/risk-before-returns-position-sizing-frameworks-fixed-fractional-atr-based-kelly-lite-4513f770a82a)
- [AI Risk Management in Crypto 2026 (Blockchain Council)](https://www.blockchain-council.org/cryptocurrency/risk-management-with-ai-in-crypto-trading-volatility-forecasting-position-sizing-stop-loss-automation/)
- [Crypto Bear Market Position Sizing (FullSwing AI)](https://www.fullswing.ai/bear-market)
- [Crypto Bot Risk Management Guide 2025 (3Commas)](https://3commas.io/blog/ai-trading-bot-risk-management-guide-2025)

---

## [2026-04-18] Cycle 153 Research — Paper→실전 전환 체크리스트 & Execution Quality

### 1. Paper Trading → 실전 전환 시 흔한 실패 원인

| 함정 | 설명 |
|------|------|
| 수수료 미반영 | 페이퍼 트레이딩이 수수료를 무시하면 실전 PnL이 30~50% 낮아질 수 있음 |
| 슬리피지 과소 추정 | 페이퍼는 이상적 체결가 가정 → 실전은 항상 불리한 가격에 체결 |
| 과적합 신뢰 오류 | 페이퍼 성과가 좋아도 과최적화된 전략일 가능성, 실전 레짐 변화에 취약 |
| 감정적 일관성 결여 | 페이퍼 성공으로 자신감 과잉 → 실전에서 포지션 과대 진입, 손절 지연 |
| 레짐 불일치 | 페이퍼 기간 레짐(예: 상승장)이 실전 레짐과 다를 수 있음 |
| 유동성 차이 | 소형 코인의 경우 페이퍼에서는 체결되지만 실전 호가창 깊이가 부족해 미체결 |

### 2. 실전 전환 전 필수 확인 항목 (체크리스트)

**데이터/백테스트 검증**
- [ ] Walk-Forward 검증 완료: Sharpe ≥ 1.0, PF ≥ 1.5, MDD ≤ 20%, Trades ≥ 15 (3개 이상 레짐 포함)
- [ ] 수수료·슬리피지 포함한 net PnL 검증 (Taker 0.055%, 예상 슬리피지 0.05~0.1% 추가)
- [ ] 최소 3개 시장 레짐(상승/하락/횡보)에서 전략이 FAIL 없이 통과했는지 확인

**인프라/API**
- [ ] Bybit Testnet에서 실제 API 호출 지연(latency) 측정 완료
- [ ] 주문 거부(order reject) 처리 로직 확인 (잔고 부족, 최소 주문 수량 미달 등)
- [ ] WebSocket 재연결 로직 및 heartbeat 타임아웃 처리 구현 확인
- [ ] Rate limit 초과 시 재시도(backoff) 로직 구현 여부 확인
- [ ] 포지션 동기화 로직: 봇 재시작 후 거래소 실제 포지션과 내부 상태 일치 확인

**리스크 관리**
- [ ] 일일 드로다운 서킷브레이커 (3% 초과 시 거래 중단) 활성화
- [ ] 단일 포지션 크기 ≤ 전체 자본의 1~2%
- [ ] 레버리지 제한: 초기 실전은 최대 3x 이하 권고
- [ ] 수동 킬스위치(kill switch) 구현 및 테스트 완료

**운영 준비**
- [ ] 알림 시스템: Telegram/슬랙으로 주문 체결, 에러, 드로다운 알림 설정
- [ ] 로그: 모든 주문 이벤트 파일 기록 (체결가, 수량, 타임스탬프)
- [ ] 초기 자본 최소화: 전체 자본의 5~10%로 시작, 1개월 안정 운영 후 증액

### 3. Bybit API Execution Quality

**주문 타입별 수수료**

| 주문 타입 | Maker 수수료 | Taker 수수료 | 비고 |
|-----------|-------------|-------------|------|
| Limit Order (지정가) | 0.020% | — | 호가창에 유동성 공급 = Maker |
| Market Order (시장가) | — | 0.055% | 즉시 체결 = Taker |
| TWAP Order | ~Maker급 | — | 소분할 지정가 방식 |
| VIP 레벨 최대 | 0.000% | 0.030% | 거래량 기준 VIP 적용 |
| Funding Fee | — | — | 8시간마다 부과 (레버리지 전체 포지션 기준) |

→ **핵심**: Limit Order 사용으로 Taker 대비 수수료 63% 절감 가능

**슬리피지 최소화 기법**

| 기법 | 원리 | Bybit 지원 여부 |
|------|------|----------------|
| TWAP | 시간 분산 체결 (5~120초 간격, 최대 20개 동시) | 지원 (Help Center 내 TWAP 전략) |
| Limit+PostOnly | 지정가 + PostOnly 파라미터로 무조건 Maker 체결 강제 | 지원 (timeInForce: PostOnly) |
| IOC Limit | 즉시 체결 안 되면 취소 → 불리한 슬리피지 차단 | 지원 |
| Iceberg | 대형 주문을 소분할해 시장 충격 최소화 | 수동 구현 필요 (API 직접 지원 없음) |
| SlippageTolerance | 시장가 주문 시 최대 허용 슬리피지 설정 (0.01~10%) | V5 API 파라미터로 지원 |

**시장 충격 최소화 실전 권고**
- 주문 크기 ≤ 해당 호가창 상위 5개 호가 합계의 10% 이하
- 저유동성 코인(24h 거래량 < $1M): 포지션 전체 크기 ≤ 시장 깊이의 0.1%
- 진입 분할: 목표 포지션의 33% → 33% → 33% 3회 분할 진입 (TWAP 유사)
- Maker-only 전략이 아닌 경우, 시장 급변동 시 자동으로 IOC 전환하는 로직 권고

### 4. 우리 봇 적용 우선순위 (Cycle 153)

1. **즉시**: Bybit 주문 타입을 기본 `Limit + PostOnly`로 변경 → Taker 수수료 0.055% 절감 → PF 개선 직접 기여
2. **단기**: 주문 수량이 큰 경우(자본 대비 > 0.5%) TWAP 3분할 자동 적용 로직 `src/exchange/` 에 추가
3. **실전 전환 기준**: Walk-Forward PASS (Sharpe ≥ 1.0, PF ≥ 1.5, MDD ≤ 20%) + Bybit Testnet 1주일 무오류 운영 + 위 체크리스트 전항목 완료 후에만 실전 전환

### 참고 출처

- [Bybit Types of Orders](https://www.bybit.com/en/help-center/article/Types-of-Orders-Available-on-Bybit)
- [Bybit TWAP Strategy Introduction](https://www.bybit.com/en/help-center/article/Introduction-to-TWAP-Strategy)
- [Bybit Market Order Slippage Tolerance](https://www.bybit.com/en/help-center/article/Market-Order-with-Slippage-Tolerance)
- [Bybit Trading Fee Structure](https://www.bybit.com/en/help-center/article/Trading-Fee-Structure)
- [Bybit V5 API Changelog](https://bybit-exchange.github.io/docs/changelog/v5)
- [Bybit Futures Fees (TradersUnion)](https://tradersunion.com/brokers/crypto/view/bybit/futures-fees/)
- [Coinrule Paper Trading 2025](https://coinrule.com/blog/trading-tips/paper-trading-in-2025-perfect-your-crypto-skills-without-risk/)

---

## [2026-04-18] Cycle 154 Research — 시장 현황 & RL 트레이딩 동향

### 1. 2026 Q1~Q2 크립토 시장 현황

**BTC/ETH/SOL 동향**
- BTC: 2026년 초 $93,700 부근에서 강하게 시작, 1월 초 기준 YTD +7%. 이후 4월 현재 기관 ETF 유입이 하루 $471M(4/17 기준)에 달하는 강세 구간 진입.
- ETH: $3,224 수준, YTD +9%. BlackRock 스테이킹 ETH ETF 출시 첫날 $155M 유입. 2026년 내 ETP AUM $400B 돌파 전망.
- SOL: Q1에 -33% 급락. 그러나 온체인 현물 거래량의 41%를 처리하며 활동성 1위 유지. Q2 $100 회복 후 Q4 $250 목표 전망.

**주요 매크로/구조 변화**
- 2026년 4월: 미국·일본·홍콩·한국이 동시에 주요 크립토 규제 완화 조치 발표 (역대 최대 규모 단일 주간 규제 이벤트).
- BTC를 포함한 16개 주요 자산이 CFTC 관할 디지털 상품으로 명시 분류 → 증권 규제 부담 제거.
- BTC-주식 상관관계 하락 추세: ETF 유입·기관 채택·온체인 펀더멘털이 주가보다 더 강한 드라이버.
- 전통 4년 사이클(반감기 주도 붐/버스트) 약화 → 기관 레짐으로 전환.

**봇 운영 영향**
- ETF 기반 기관 유입이 장중 유동성 급증·급감을 유발할 수 있음 → 주문 실행 타이밍 관리 필요.
- 규제 명확성 증가 → 시장 구조 안정화 장기적으로 긍정적, 단기적으로 이벤트 기반 변동성 주의.
- SOL처럼 온체인 활동 높아도 가격 약세 가능 → 온체인 지표만으로 진입 판단 위험.

---

### 2. Reinforcement Learning for Trading 최신 동향 (2025~2026)

**주요 알고리즘 성과 비교**

| 알고리즘 | 특성 | 크립토 성과 |
|---|---|---|
| PPO | 안정적, 샘플 효율, 연속/이산 모두 적용 가능 | Walk-forward 평균 Sharpe 1.95 (25개 자산 포트폴리오 기준) |
| SAC | 엔트로피 정규화로 탐색 강화 | 극단 변동성(VIX>80) 환경에서 연환산 94% 수익 |
| CNN-PPO | 이미지 기반 가격 패턴 결합 | 표준 RL 대비 +17.9% 성과 향상 |
| QR-DDPG | 분위수 기반 위험 관리 | 최저 Tail Risk (CVaR -1.73%) |

**RL vs RF(랜덤 포레스트) 분류기 비교**
- RF 장점: 학습 속도 빠름, 소규모 데이터에서 안정적, 해석 용이
- RF 단점: 레짐 변화에 취약, 정적 피처 엔지니어링 의존, 시계열 비선형성 미흡
- RL 장점: 동적 시장 적응력, 연속 행동공간 자연 처리, 포트폴리오 전체 최적화 가능
- RL 단점: 대규모 샘플 필요, 과최적화 위험 높음, 하이퍼파라미터 민감, 수렴 불안정
- **핵심**: Ensemble RL+Classifier 하이브리드가 단일 방법 대비 드로다운 관리·리스크조정수익 15~20% 개선

**소규모 계좌에서의 RL 실현 가능성**
- FinRL, Stable-Baselines3, RLlib 등 프레임워크 성숙 → 구현 진입장벽 낮음
- 크립토 24/7 + 고변동성 환경은 RL에 유리 (정적 전략보다 적응 우위)
- **핵심 제약**: 정기 재학습(periodic retraining) 없으면 알파 감소로 성과 지속 불가. 현재 봇의 주간 재학습과 방향 일치.
- 소규모 계좌 권고: PPO부터 시작 (SAC 대비 안정적), 처음에는 단일 자산 1개에 집중, 최소 6개월 실시간 검증 후 확대.

---

### 3. 봇 적용 우선순위 (Cycle 154)

1. **즉시 주의**: SOL 포지션 사이즈 축소 — Q1 -33%의 급락 레짐에서 기존 사이징 과다 위험. ATR 기반 동적 축소 로직 적용 확인.
2. **단기 검토**: PPO 기반 전략 선택기 PoC — 기존 RF 분류기를 PPO로 교체하는 소규모 실험. Stable-Baselines3 + FinRL 활용, 단일 자산(BTC) 시작.
3. **레짐 감지 강화**: 2026년 ETF 기반 유동성 급변 대응으로 기관 유입 시그널(ETF flow 데이터) 을 레짐 피처에 통합 검토.

### 참고 출처

- [Bitwise 2026 Crypto Outlook](https://finance.yahoo.com/news/bitcoin-ethereum-solana-hit-time-023109855.html)
- [CoinDesk 2026 Strong Start](https://www.coindesk.com/markets/2026/01/06/here-s-why-bitcoin-and-major-tokens-are-seeing-a-strong-start-to-2026)
- [Amberdata Institutional Crypto Flows 2026](https://blog.amberdata.io/institutional-crypto-flows-2026-market-analysis)
- [Grayscale 2026 Digital Asset Outlook](https://research.grayscale.com/reports/2026-digital-asset-outlook-dawn-of-the-institutional-era)
- [NFT Plazas March 2026 Regulatory Shift](https://nftplazas.com/march-2026-crypto-regulation-shift/)
- [arXiv: SAC/DDPG Crypto Portfolio Management](https://arxiv.org/abs/2511.20678)
- [arXiv: Ensemble RL + Classifier Models](https://arxiv.org/abs/2502.17518)
- [arXiv: RL Financial Decision Making Systematic Review](https://arxiv.org/html/2512.10913v1)
- [NeuralArb: RL in Dynamic Crypto Markets](https://www.neuralarb.com/2025/11/20/reinforcement-learning-in-dynamic-crypto-markets/)
- [Stanford CS224R: RL in Crypto Trading](https://cs224r.stanford.edu/projects/pdfs/CS224R_Report12.pdf)

---

## [2026-04-20] Cycle Research — ML 봇 실패/성공 사례 + Funding Rate/OI 피처 + 모델 비교

### 실패 사례

- **백테스트-실전 간극 (2024, arXiv:2407.18334)** — 41개 ML 모델로 Bitcoin 거래 분석 결과, 백테스트에서 잘 작동한 모델 대부분이 forward test/실전에서 성능 급락. 연구 인용: "백테스트만으로 모델 신뢰는 금물". R² 기준 백테스트 Sharpe는 실전 성과의 예측력 2.5% 미만(R²<0.025). 교훈: **Walk-Forward 없는 백테스트 결과는 무의미**, 우리 Walk-Forward PASS 기준(Sharpe≥1.0) 유지 필수. 출처: https://arxiv.org/html/2407.18334v1

- **XGBoost 소규모 데이터 과적합 (2024, mljar.com 분석)** — XGBoost 기본값(max_depth=6, lr=0.3, n_estimators=100)은 1000샘플 이하 데이터에서 공격적 과적합 발생. 튜닝 없이 RF와 비교하면 XGBoost가 열등하게 보이지만 실제로는 기본값 문제. 73%의 자동화 거래 계좌가 6개월 내 실패하는 주요 원인 중 하나. 교훈: **XGBoost 도입 시 반드시 max_depth≤4, learning_rate≤0.05, early_stopping 설정**. 출처: https://mljar.com/machine-learning/extra-trees-vs-xgboost/

- **단일 지표 의존 ML 봇 실패 (2024~2025, blockchain-council.org)** — 기술 지표만 피처로 사용한 ML 봇의 경우, 규제 발표·매크로 이벤트 등 구조적 변화에 적응 실패. 888개 알고리즘 전략 연구에서 44%가 새 데이터에서 성공 재현 불가. 교훈: **파생상품 데이터(Funding Rate, OI) 등 다차원 피처 조합 필수**. 출처: https://www.blockchain-council.org/cryptocurrency/backtesting-ai-crypto-trading-strategies-avoiding-overfitting-lookahead-bias-data-leakage/

---

### 성공 사례

- **Random Forest + BaggingClassifier Bitcoin 거래 (2024, arXiv:2407.18334)** — 41개 모델 중 RF Classifier와 BaggingClassifier가 백테스트/forward test/실전 3단계 모두 안정적 성능 유지. BaggingClassifier는 백테스트 PNL 121.73% 달성. 핵심 피처: MFI(Money Flow Index), Bollinger Bands, Keltner Channel Width, Parabolic SAR, A/D Index. 멀티 롤링 윈도우(1/7/14/21/28일) 사용. 교훈: **단일 타임프레임 대신 다중 롤링 윈도우 피처 사용이 일반화에 유리**. 출처: https://arxiv.org/html/2407.18334v1

- **앙상블 RF + Random Forest Out-of-Sample (2023, ScienceDirect)** — RF 기반 암호화폐 선물시장 out-of-sample 예측 연구에서 RF가 연속형 데이터셋에서 최고 예측 성능 달성. 교훈: **연속형 OHLCV 데이터에서는 RF가 기본 베이스라인으로 적합**, 현재 63.5% acc는 유지 가능한 수준. 출처: https://www.sciencedirect.com/science/article/pii/S027553192200215X

---

### Funding Rate + Open Interest 피처 효과

- **통합 프레임워크 정확도 향상 (gate.com, 2025)** — Funding Rate + OI + Liquidation 3개 지표를 통합한 ML 프레임워크가 단일 지표 대비 "substantially higher accuracy" 달성. 앙상블(RF, XGBoost)이 이 세 지표의 비선형 관계를 효과적으로 포착. Funding Rate은 시장 심리 방향(양수=롱 우세), OI는 포지션 확신도/레버리지 규모를 나타냄. 교훈: **두 지표를 별도 피처로 분리하지 말고, FR×OI 곱(포지션 압력 지수) 파생 피처 생성 고려**. 출처: https://web3.gate.com/en/crypto-wiki/article/how-do-futures-open-interest-funding-rates-and-liquidation-data-predict-crypto-price-movements-20251226

- **Funding Rate 예측 가능성 연구 (SSRN:5576424)** — DAR 모델 기반 Funding Rate 예측이 no-change 모델 대비 방향 정확도 우위 확인. Funding Rate 자체가 다음 기간 가격 방향의 선행 지표로 기능. 교훈: **Funding Rate을 raw값 그대로 쓰기보다 전기 대비 변화량(delta FR)을 피처로 사용하면 신호 강도 향상**. 출처: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5576424

---

### RF vs XGBoost vs ExtraTrees 소규모 데이터 비교

- **소규모(n<1000) 데이터에서 모델 선택 지침 (mljar.com, mcpanalytics.ai)**
  - **RF**: 부트스트랩 샘플링 + 피처 서브샘플링으로 소규모 노이즈 데이터에서 자연스러운 정규화. 튜닝 없이도 과적합 저항성 높음. 현재 63.5% acc 확보한 우리 환경에 적합.
  - **ExtraTrees**: RF보다 분할 랜덤성이 더 높아 과적합 위험 추가 감소, 훈련 속도 빠름. 단, 예측 분산이 커질 수 있어 소규모 데이터에서 RF보다 반드시 낫다고 할 수 없음. **RF 대비 성능 개선은 데이터셋마다 다름 — 교차검증으로 확인 필수**.
  - **XGBoost**: 순차적 트리 피팅이 소규모 데이터에서 과적합 위험. 기본값 그대로 쓰면 RF보다 열등. max_depth≤3, n_estimators≤200, early_stopping 필수.
  - **권고**: 1000캔들 환경에서는 **RF를 베이스라인으로 유지**, ExtraTrees 병렬 테스트 후 CV 기준 우위 확인 시 교체. XGBoost는 엄격한 하이퍼파라미터 튜닝 후에만 도입.

- **출처**: https://mljar.com/machine-learning/extra-trees-vs-xgboost/, https://mljar.com/machine-learning/random-forest-vs-xgboost/, https://pmc.ncbi.nlm.nih.gov/articles/PMC12571449/

---

### 우리 프로젝트 핵심 교훈 3개 (2026-04-20)

1. **Funding Rate delta + OI를 피처로 즉시 추가** — raw FR보다 전기 대비 변화량(delta_fr), FR×OI 파생 피처가 방향성 예측력 향상. 현재 15개 피처에서 2개 추가 후 SHAP으로 기여도 확인.

2. **ExtraTrees는 RF와 함께 CV 비교 후 선택** — 소규모 데이터에서 ExtraTrees가 반드시 우위는 아님. RF를 베이스라인으로 유지하면서 ExtraTrees를 병렬 실험. XGBoost는 max_depth≤3 튜닝 없이 도입 금지.

3. **멀티 롤링 윈도우 피처 추가** — 현재 단일 윈도우 지표 위주에서 7/14/21일 롤링 MFI, BB 폭, ATR 추가 시 일반화 성능 향상 가능성 높음 (arXiv 연구 근거).

