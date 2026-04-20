## Cycle 164 Research Notes — XGBoost 앙상블 + 다시간 윈도우 전략

### 주제 1: XGBoost 크립토 트레이딩 앙상블 Best Practice

#### 핵심 인사이트

1. **RF + XGBoost 앙상블: Stacking이 Voting보다 우월** — RF를 base learner, XGBoost를 meta-learner로 쓰는 stacking 패턴이 크립토 방향 예측에서 단순 voting/averaging보다 우월. 이유: XGBoost meta-learner가 각 base 모델의 약점/강점을 레짐별로 학습함. 실증: Ethereum 단기 수익 분류(Downtrend/Sideway/Uptrend 3-class)에서 stacking이 단일 모델 대비 ROC-AUC 개선. 단, 데이터가 작을 때(< 500 샘플) stacking이 오히려 과적합 위험 — 크립토 4h 봉 90일 = 540 샘플이므로 경계 구간.

2. **max_depth <= 3이 크립토에서 과적합 방지에 실증적으로 유효** — XGBoost 기본값이 max_depth=3인 이유가 있음. max_depth가 커질수록 훈련 성능은 급격히 오르고 테스트 성능은 완만하게 오르는 gap 확대 패턴이 금융 데이터에서 일관되게 관찰됨. 크립토 방향 예측 연구에서 max_depth 3~4가 최적 구간으로 반복 등장. max_depth >= 6은 표본 내 Sharpe가 높아 보이지만 실전 드리프트 구간에서 급격히 붕괴.

3. **early_stopping_rounds: 크립토 노이즈 데이터에는 50 권장** — 표준 권장: n_estimators의 10%. 그러나 크립토처럼 loss가 무작위 구간에서 일시적으로 오르내리는 노이즈 데이터에서는 rounds=10~20이면 조기 종료 오류 발생 빈번. 금융 fraud detection 등 노이즈 금융 데이터 연구에서 rounds=50이 표준. 구현 권장: `early_stopping_rounds=50, eval_metric='logloss', eval_set=[(X_val, y_val)]`. 주의: hyperparameter tuning(CV) 이후 최적 n_estimators로 재학습 필수 — fold별 stopping point가 달라 CV 결과를 그대로 사용하면 안 됨.

4. **권장 hyperparameter 범위 (크립토 방향 예측 기준)** — Bayesian optimization이 grid search보다 효율적(탐색 공간 대비 오류 최소화). 크립토 논문과 Kaggle 금융 대회 기준 수렴 구간:
   - `learning_rate`: 0.01~0.05 (크립토는 0.1보다 작은 값이 일반화 우수)
   - `n_estimators`: 200~500 (early stopping과 함께 사용 시)
   - `max_depth`: 3~4
   - `subsample`: 0.6~0.8 (0.5는 과소, 1.0은 과대)
   - `colsample_bytree`: 0.6~0.8
   - `min_child_weight`: 3~5 (크립토 노이즈 방어)
   - `reg_alpha`(L1)/`reg_lambda`(L2): 0.1~1.0 (정규화 필수)

5. **XGBoost 단독 vs RF: 크립토에서 RF가 일반화 더 안정적** — XGBoost는 과거 패턴을 RF보다 정밀하게 학습하지만, 레짐 전환 시 RF보다 빨리 붕괴하는 특성이 여러 크립토 연구에서 관찰. 결론: XGBoost를 RF와 stacking 앙상블로 결합할 때 단독 XGBoost보다 out-of-sample 안정성이 높음. 우리 프로젝트는 이미 RF가 63.5% test acc — XGBoost를 병렬 추가해 stacking하는 것이 RF 단독 교체보다 리스크가 낮음.

---

### 주제 2: 다시간 윈도우 앙상블 (Multi-Horizon Ensemble) 구현 패턴

#### 핵심 인사이트

1. **동적 가중치(성능 기반) > 고정 가중치** — ACM ICAIF FinRL Contest 2023/2024 공식 집계: 롤링 성능 기반 동적 가중치가 고정 가중치 대비 Sharpe를 평균 12~18% 향상. 가중치 계산 기준: 최근 N거래(N=20~30)의 rolling accuracy 또는 rolling Sharpe. 구현 패턴: `w_i = softmax(perf_i / temperature)`. 단, 성능 변동이 심한 크립토에서 temperature가 너무 낮으면(= 한 모델에 가중치 집중) 불안정 — temperature=1.0~2.0이 안전.

2. **레짐 전환 시 단기 윈도우(30일)가 유리, 안정 구간에서는 장기(90일)가 유리** — 연구 결과(Dynamic Factor Allocation, 2024): 장기 윈도우 모델(90일+)은 안정된 추세 레짐에서 더 높은 가중치를 받고, 단기 윈도우(30일)는 레짐 전환 직후 빠른 적응으로 일시적으로 가중치가 급등하는 패턴. 크립토 bull/bear/neutral 3-state 레짐 모델에서 이 패턴이 실증 확인. 결론: 동적 가중치 자체가 레짐 인식 메커니즘을 내포함 — 별도 레짐 탐지 없어도 어느 정도 자동 적응.

3. **데이터 겹침(Overlap) 문제: 30/60/90일은 구조적으로 상관됨** — 90일 모델은 60일/30일 모델이 본 데이터를 모두 포함. 이로 인해 세 모델의 예측이 높은 상관관계를 가지며, 실질적인 앙상블 다양성(diversity)이 낮아짐. 겹침 50% 초과 시 동일 패턴을 여러 모델이 중복 반영해 분산 감소 효과 약화. 완화 방법: (a) walk-forward로 각 모델 학습 구간을 겹치지 않게 분리(가장 강력), (b) 서로 다른 피처셋 사용(예: 30일=단기 피처, 90일=장기 피처), (c) 다양한 알고리즘 사용(RF + XGBoost + ExtraTrees).

4. **실패 사례: 모델 수 과다 + 상관도 문제** — 모델 수를 5~10개로 늘려도 상관관계가 높으면 앙상블 이득이 사라짐. 실증: 3-window 앙상블(30/60/90일 RF)의 correlation matrix에서 평균 0.85 이상 상관이 관찰된 사례. 이 경우 단일 모델과 거의 동일한 결과. 핵심: 모델 수보다 모델 간 다양성(diversity)이 앙상블 이득의 결정 요인 — 3개 다양한 알고리즘 > 10개 동일 알고리즘.

5. **메모리/계산 비용: 30/60/90일 3모델은 실전 허용 수준** — 4h 봉 30일 = 180 샘플, 90일 = 540 샘플. 피처 30개, XGBoost/RF 학습 시간 < 1초/모델. 3모델 총 학습 시간 < 5초 — 실전 배포 허용. 예측 inference는 저장된 모델 로드 후 < 10ms. 주의: 모델을 매 거래마다 재학습하면 낭비 — PSI 트리거 기반 재학습(필요 시에만) 유지.

---

### 이 프로젝트에 적용 가능한 구체적 구현 권장사항

1. **RF(이미 구현) + XGBoost stacking 설계** — 기존 RF 모델을 base learner로 유지, XGBoost meta-learner 추가. meta-learner 입력: RF의 predict_proba 3개(UP/DOWN/HOLD) + XGBoost 자체의 predict_proba. stacking용 held-out set은 기존 validation fold 재활용. max_depth=3, learning_rate=0.03, subsample=0.7, early_stopping_rounds=50으로 시작.

2. **30/60/90일 윈도우 다양성 확보 전략** — 단순히 같은 RF를 3번 학습하면 상관도가 너무 높음. 권장: 30일=XGBoost(단기 피처: RSI/MACD/volume), 60일=RF(중기 피처: 볼린저밴드/ATR), 90일=ExtraTrees(장기 피처: 추세 강도/OI). 각 모델이 다른 알고리즘 + 다른 피처 그룹을 사용하면 상관도를 0.6 수준으로 낮출 수 있음 — 앙상블 이득 실질화.

3. **가중치 업데이트 주기: 매 거래가 아닌 rolling 20거래마다** — 매 거래 후 가중치 재계산하면 단기 노이즈에 과잉 반응. 권장: 20거래 버퍼 채운 후 rolling accuracy로 가중치 재계산, softmax temperature=1.5 적용. 초기 20거래 이전에는 균등 가중치(1/3 each) 사용. 이 설계가 Cycle 163에서 제안된 "최근 정확도 기반 동적 가중치" 구현 방법에 해당.

---

### 출처

- [Revisiting Ensemble Methods for Stock Trading and Crypto Trading Tasks at ACM ICAIF FinRL Contests 2023/2024](https://arxiv.org/html/2501.10709v1)
- [XGBoost for Classifying Ethereum Short-term Return Based on Technical Factor](https://dl.acm.org/doi/fullHtml/10.1145/3605423.3605462)
- [Empirical Calibration of XGBoost Model Hyperparameters Using Bayesian Optimisation: Bitcoin Volatility](https://www.mdpi.com/1911-8074/18/9/487)
- [Dynamic Factor Allocation Leveraging Regime-Switching Signals](https://arxiv.org/html/2410.14841v1)
- [Dynamic Asset Allocation with Asset-Specific Regime Forecasts](https://arxiv.org/html/2406.09578v1)
- [Hyperparameter Tuning XGBoost with early stopping](https://macalusojeff.github.io/post/HyperparameterTuningXGB/)
- [Early Stopping with XGBoost: Preventing Overfitting in Boosted Trees](https://codesignal.com/learn/courses/fixing-classical-models-diagnosis-regularization/lessons/early-stopping-with-xgboost-preventing-overfitting-in-boosted-trees)
- [Multi-Window Based Ensemble Learning for Classification of Imbalanced Streaming Data](https://link.springer.com/chapter/10.1007/978-3-319-26187-4_6)
- [XGBoost Parameters — xgboost 3.2.0 documentation](https://xgboost.readthedocs.io/en/stable/parameter.html)
- [Stacking Ensemble With XGBoost Meta Model](https://xgboosting.com/stacking-ensemble-with-xgboost-meta-model-final-model/)

---

## Cycle 163 Research Notes — 실시간 모델 드리프트 대응 & 소자본 운영 현실

### 주제 1: ML 트레이딩봇 실시간 모델 드리프트 대응

#### 핵심 인사이트

1. **PSI가 금융 서비스 표준, 역치는 PSI > 0.2** — PSI(Population Stability Index)는 reference 분포 대비 현재 피처 분포 변화를 quantize된 bin으로 계산. PSI < 0.1은 안정, 0.1~0.2는 경고, > 0.2는 재학습 트리거. 금융 서비스에서 가장 광범위하게 배포된 드리프트 감지 메트릭. 이전 리서치에서 이미 PSI > 0.2 재학습 기준이 우리 프로젝트에 언급됨 — 이 기준은 업계 표준과 일치.

2. **앙상블이 드리프트에 가장 강건** — 서로 다른 시간 구간에 학습된 여러 모델을 앙상블하면 단일 모델 드리프트에 덜 민감. 핵심 메커니즘: 하나의 컴포넌트 모델이 특정 레짐에서 드리프트해도 나머지 모델이 보완. 실제 구현 패턴: 최근 30일 모델 + 60일 모델 + 90일 모델 가중 앙상블, 최근 정확도가 높은 모델에 더 높은 가중치 부여.

3. **폴백 전략(Fallback) 필수 — 규칙 기반으로 후퇴** — 드리프트 감지 시 ML 모델을 신뢰할 수 없는 구간에서 더 단순하고 robust한 규칙 기반 로직(예: 이동평균, 모멘텀 필터)으로 자동 전환. "rogue model보다 덜 정확하지만 더 robust한 휴리스틱" 원칙. 모델 신뢰도 낮을 때 포지션 사이즈 축소 또는 HOLD도 폴백 전략의 일종.

4. **재학습 주기 best practice: 드리프트 트리거 > 고정 주기** — 2시간마다 재학습하는 구현 사례도 있으나, 업계 best practice는 고정 스케줄보다 PSI/정확도 드리프트 트리거 기반 재학습이 우월. 크립토처럼 레짐 변화가 불규칙한 시장에서는 고정 주기(예: 매일)가 오히려 안정 구간에서 불필요한 재학습 야기. 권장: PSI > 0.2 OR 최근 N거래 정확도가 기준(예: 55%) 이하 시 재학습 트리거.

5. **데이터 윈도우 크기: 롤링 90~180일이 크립토 표준** — 너무 짧으면(30일 이하) 노이즈 과학습, 너무 길면(1년 이상) 이전 레짐 데이터가 현재 레짐 학습을 방해. 크립토 고변동성 특성상 금융권 표준(1~3년)보다 짧은 윈도우 권장. Freqtrade 오픈소스 봇 커뮤니티 기준: rolling 90일 학습 + 최근 30일 검증이 가장 많이 사용되는 조합.

#### 드리프트 감지 메트릭 비교

| 메트릭 | 민감도 | 금융 표준 | 계산 비용 | 적합 용도 |
|--------|--------|-----------|-----------|-----------|
| PSI | 중간 | 최고 | 낮음 | 피처 분포 모니터링 |
| KL Divergence | 높음 | 중간 | 낮음 | 큰 분포 변화 포착 |
| KS Test | 중간 | 중간 | 낮음 | 수치형 피처 단변량 |
| 정확도 추적 | 낮음(지연) | 높음 | 낮음 | 모델 출력 성능 모니터링 |

---

### 주제 2: 소규모 자본($1K-$10K) 크립토 봇 운영 현실

#### 핵심 인사이트

1. **73% 실패율, 수수료가 핵심 원인** — 자동화 크립토 트레이딩 계좌의 73%가 6개월 내 실패. 80% 이상의 소매 자동화 봇 사용자가 단순 Buy-and-Hold보다 낮은 성과(수수료 + 슬리피지 반영 후). $1,000 자본으로 0.2% 수익 거래 시 gross $2, 수수료 약 $1.5 제하면 net $0.5 — 스케일링 자체가 불가능.

2. **Bybit 수수료 구조 (2026 기준)** — Taker: 0.055%, Maker: 0.020%. VIP 최고 등급 시 Taker 0.030%, Maker 0.000%(rebate). 소자본 봇의 수수료 최소화 핵심: **지정가 주문(limit order) = maker 주문 = 0.020%**. 시장가 주문(taker) 사용 시 round-trip 수수료 0.11% — 0.2% 목표 수익에서 55%가 수수료. 스캘핑 전략은 수학적으로 소자본에서 작동 어려움.

3. **$5,000이 현실적 최소 자본 — 스캘핑 기준** — $1,000 이하는 수수료 비율이 수익을 구조적으로 잠식. $5,000부터 수학적으로 수익 가능한 구조 시작. 스캘핑 봇은 0.1~0.5% 목표 수익/거래, tight stop-loss 0.1~0.2% — 월 현실적 수익 3~6% 상한(좋은 달 기준). **스윙 전략이 소자본에 더 유리**: 거래 빈도 낮아 수수료 부담 감소, 슬리피지 영향도 낮음.

4. **슬리피지 과소추정이 실패 2위 원인** — BTC/USDT $10,000 주문 기준 슬리피지 0.1% 미만(주요 거래소). 그러나 변동성 구간에서 0.6~1.5%+로 급등. 2025년 5월 플래시 크래시 당시 AI 봇들이 3분 만에 $20억 매도 → 유동성 부족 구간 진입 시 슬리피지 폭발. **백테스트에 0.1% 고정 슬리피지 적용은 과소추정** — 변동성 레짐별 가변 슬리피지(low_vol: 0.05%, high_vol: 0.3~0.5%) 적용 필요.

5. **레버리지가 소자본 실패의 3위 원인** — 소자본 + 고레버리지 조합은 MDD를 기하급수적으로 증폭. 성공 사례(3Commas DCA 20x)는 매우 정교한 파라미터 검증 후 적용. 소자본 첫 실전 운용 권장 레버리지: 1~3x. 레버리지 없이 전략 엣지 먼저 실증 후 점진적 증가.

#### 전략 유형별 소자본 적합성

| 전략 유형 | 거래 빈도 | 수수료 영향 | 슬리피지 영향 | $1K-$10K 적합도 |
|-----------|-----------|-------------|---------------|-----------------|
| 스캘핑(1m-5m) | 매우 높음 | 매우 높음 | 높음 | 낮음 |
| 단타(15m-1h) | 높음 | 높음 | 중간 | 중간 |
| 스윙(4h-1d) | 낮음 | 낮음 | 낮음 | 높음 |
| DCA/Grid | 조건부 | 낮음(maker) | 낮음 | 높음(ranging) |

---

### 이 프로젝트에 적용 가능한 구체적 권장사항

1. **PSI 기반 자동 재학습 트리거 구현** — `src/ml/` 또는 `src/risk/` 에 PSI 계산 모듈 추가. 학습 시점의 피처 분포를 reference로 저장, 실시간 피처 분포와 비교해 PSI > 0.2 시 재학습 플래그 발생. 이미 이전 리서치에서 PSI > 0.2 기준이 언급됐으므로 구현 단계로 진행 가능.

2. **XGBoost 앙상블을 다시간 윈도우 앙상블로 설계** — 다음 구현 대상인 XGBoost 앙상블을 단순 배깅이 아니라 "90일 모델 + 60일 모델 + 30일 모델" 3-way 앙상블로 설계. 각 모델의 최근 정확도(rolling 20거래 기준)로 가중치 동적 조정. 드리프트 시 최신 30일 모델 가중치가 자동으로 올라가는 구조.

3. **백테스트 엔진에 현실적 수수료/슬리피지 적용** — 현재 BacktestEngine의 수수료 설정 확인 필요. 실전 기준: Taker fee 0.055%, 레짐별 가변 슬리피지(ATR 상위 20% 구간: 0.3%, 하위 80%: 0.08%). ML 모델(4h 스윙 기준) 수수료는 낮지만, 백테스트가 시장가 진입 가정이면 taker fee 0.055% 반드시 반영.

---

### 출처

- [Model Drift Detection: Preventing Silent Accuracy Decay](https://wetranscloud.com/blog/model-drift-detection-accuracy-decay)
- [AI Model Drift & Retraining: A Guide for ML System Maintenance](https://smartdev.com/ai-model-drift-retraining-a-guide-for-ml-system-maintenance/)
- [Strategies for Managing Model Drift in Deployed ML Systems](https://moldstud.com/articles/p-effective-strategies-for-managing-model-drift-in-deployed-machine-learning-systems)
- [Autoregressive Drift Detection Method (ADDM) in Trading](https://blog.quantinsti.com/autoregressive-drift-detection-method/)
- [GitHub: freqtrade/freqtrade — open source crypto trading bot](https://github.com/freqtrade/freqtrade)
- [How to Backtest a Crypto Bot: Realistic Fees, Slippage, and Paper Trading](https://paybis.com/blog/how-to-backtest-crypto-bot/)
- [7 Hidden Risks of Crypto Bots: Advanced Dangers Traders Must Avoid](https://www.altrady.com/blog/crypto-bots/7-hidden-risks)
- [Why Most Trading Bots Lose Money](https://www.fortraders.com/blog/trading-bots-lose-money)
- [Bybit Trading Fee Structure](https://www.bybit.com/en/help-center/article/Trading-Fee-Structure)
- [The 2025 Crypto Scalping Bot Landscape: ROI, Risk, and Technological Edge](https://www.ainvest.com/news/2025-crypto-scalping-bot-landscape-roi-risk-technological-edge-2512/)
- [Crypto Slippage Explained: How I Fixed My Arbitrage Bot's #1 Problem](https://medium.com/@swaphunt/slippage-in-crypto-swaps-why-your-arbitrage-bot-keeps-crying-and-what-i-did-about-it-e561c0603e86)

---

## Cycle 133 Research Notes

### 실패 사례

1. **AQR Capital 이동평균 전략** — 원인: 과최적화(Overfitting). 인샘플 Sharpe 1.2 → 아웃오브샘플 -0.2로 붕괴. 데이터 체리피킹으로 실제 시장에서 작동 안 함. 우리 프로젝트 상황(22개 PASS 중 20개 실전 FAIL)과 동일한 패턴.

2. **AI 봇 $441K 손실 사례 (2025)** — 원인: GPT 기반 봇이 SNS 포스트를 잘못 해석해 $441K 상당 토큰을 무관한 주소로 전송. GPT-5 단독 운용 시 퍼프 자본 62% 소멸. 과도한 자동화 + 인간 감독 부재.

3. **Quantopian 대규모 분석 결과** — 원인: 수백 개 알고리즘 분석 결과, 인샘플 Sharpe와 아웃오브샘플 간 상관관계가 0.05 미만. 파라미터 과다 튜닝 시 12%의 파라미터 조합만 실제 수익. 전략 복잡도와 성과는 무관하거나 역상관.

### 성공 사례

1. **Polymarket 차익거래 봇 (2025)** — 핵심: 방향 예측 없이 Polymarket 가격이 Binance/Coinbase 현물 모멘텀보다 지연되는 단기 윈도우를 익스플로잇. BTC/ETH/SOL 15분 상/하 시장만 거래. 승률 98%. 핵심은 예측이 아닌 구조적 엣지(price lag arbitrage).

2. **3Commas DCA 봇 — $JUP/USDT (Bybit Futures)** — 핵심: 11단계 물타기 + 철저한 백테스트 + 최적화 후 20x 레버리지 적용. 6개월 193% ROI. 단순 DCA이지만 파라미터 검증이 핵심.

### 최신 트렌드 (2025-2026)

- **Regime Detection 급부상**: HMM(Hidden Markov Model), GMM, k-means 클러스터링 기반 시장 레짐 분류가 표준화되고 있음. LSEG가 2023년부터 도입. AI 레짐 탐지 시장 CAGR 23.8%(2024→2025).
- **멀티 레짐 전략 전환**: 레짐별(추세/횡보/고변동성) 전략을 자동으로 전환하는 Policy Gradient 기반 적응형 시스템이 트렌드. Mean-reversion vs Momentum을 실시간 레짐 스코어로 선택.
- **2025 퀀트 겨울(Quant Winter)**: 소매 유동성과 알고 거래(글로벌 거래량의 89%)가 자기강화 생태계를 만들어 기존 퀀트 전략과 충돌 발생. 역사적 데이터 최적화 알고리즘이 감성·유동성 주도 시장에서 실패.
- **QuantEvolve 등 멀티에이전트 진화 프레임워크**: 전략 자동 발견 및 파라미터 진화를 멀티에이전트 시스템으로 자동화하는 연구 증가.

### 우리 프로젝트에 적용 가능한 교훈

- **핵심 문제 확인**: 355개 전략 중 실전 PASS 2개 = Quantopian 사례와 동일. 과최적화가 원인이며 전략 수를 늘리는 것은 해결책이 아님.
- **Regime Detection 우선 구현**: 실전 수익 봇들의 공통점은 시장 상태 분류 후 전략 선택. HMM 또는 변동성 기반 단순 레짐 구분(trending/ranging/volatile) 도입 필요.
- **구조적 엣지 집중**: 성공 사례 공통점 — 방향 예측보다 구조적 비효율(price lag, liquidity gap) 익스플로잇. engulfing_zone, relative_volume이 PASS인 것도 같은 이유.
- **파라미터 단순화**: 현재 22개 PASS 전략 중 20개 실전 FAIL = 파라미터 과다. Walk-Forward 검증 + 파라미터 수 최소화 필요.
- **인간 감독 체계**: AI 단독 운용 실패 사례 반복. 알림/모니터링 강화 및 자동 손절 로직 필수.

---

## Cycle 134 Research Notes — Regime Detection Deep Dive

### Regime Detection 구현 사례

1. **MarketRegimeTrader (GitHub: 0x596173736972)** — HMM 기반 레짐 탐지 + 자동 전략 생성을 결합한 퀀트 플랫폼. 구조: `data_loader.py` → `features.py` (수익률/변동성/기술지표) → `hmm_regime.py` → `strategy.py` (레짐별 전략 선택) → `backtest.py`. Walk-Forward Validation과 Topological Data Analysis(TDA) 포함. hmmlearn 라이브러리 사용. 레짐: bullish/bearish/range-bound 3분류.

2. **market-regime-detection (GitHub: Sakeeb91)** — HMM + GMM 이중 탐지 + Change Point Detection 조합. 전략 엔진에 포지션 사이징·리스크 관리 내장. Walk-Forward 검증 프레임워크 포함. 특징: HMM만으로 부족한 급변점을 Change Point Detection으로 보완하는 앙상블 접근.

3. **PyQuantLab GMM Regime-Switching Momentum (Medium/GitHub)** — GMM으로 크립토 시장을 저변동성/고변동성 레짐으로 분류 후 모멘텀 전략 온/오프 전환. 핵심 아이디어: 고변동성 레짐에서는 포지션 축소 또는 HOLD, 저변동성 추세 레짐에서만 진입. GMM이 HMM보다 Markovian 제약 없어 크립토 급변 구간에 유리하다는 주장.

### 실패 사례

1. **Static Trend-Following Bot의 레짐 전환 실패 (2024 Flash Crash 사례)** — 원인: 2024년 6월 경제 지표 발표 후 AI 알고리즘들이 일제히 대규모 매도 주문 실행. 레짐 감지 없이 동일 로직으로 운용되던 봇들이 급변동 구간에서 같은 방향으로 연쇄 반응 → 플래시 크래시 가속. 고주파 봇들이 유동성 공급자에서 유동성 소비자로 순간 전환되는 레짐 변화를 인식 못함. 교훈: 레짐 변화 시 전략을 일시 중단하거나 포지션 사이즈 축소 로직 필수.

2. **HMM 상태 수(k) 과다 설정으로 인한 과최적화** — 원인: HMM의 hidden state 수를 AIC/BIC 없이 임의 설정(예: k=5~7)할 경우 in-sample에서는 완벽한 레짐 분류가 가능하나 out-of-sample에서 레짐 라벨이 일치하지 않는 문제 발생. 연구 결과 λ 하이퍼파라미터를 크게 설정해도 HMM 구조에서 과적합 위험이 잔존. 표준 권장: k=2~3 (bull/bear/neutral)으로 단순하게 유지, BIC로 검증.

### 우리 프로젝트 적용 방안

- **통합 위치**: `src/data/feed.py`의 `fetch_ohlcv` 반환 DataFrame에 `regime` 컬럼 추가. `DataFeed.get_df()` 호출 후 regime detector가 컬럼을 붙이면 모든 전략이 `df["regime"]`을 참조 가능.
- **단계적 구현**: 1단계는 변동성 기반 단순 레짐(rolling ATR 분위수로 low/mid/high 3분류) — 외부 라이브러리 불필요. 2단계는 hmmlearn GaussianHMM(n_components=2~3, features: returns + log_volume + ATR). 3단계는 GMM(BayesianGaussianMixture) + Change Point Detection 앙상블.
- **전략 필터 패턴**: 기존 BaseStrategy.generate()에서 `df["regime"].iloc[-1]` 조회 후 레짐 불일치 시 `Action.HOLD` 반환. 추세 전략은 trending 레짐에서만, 횡보 전략은 ranging 레짐에서만 신호 허용.
- **새 파일 최소화**: `src/data/regime_detector.py` 1개만 추가. feed.py에서 import해 DataFrame에 컬럼 주입. 전략 파일 수정 없이 BaseStrategy 레벨에서 레짐 필터 적용 가능하면 이상적.
- **Walk-Forward 검증 필수**: 레짐 탐지 모델 자체도 in-sample 학습 후 out-of-sample로 검증. 레짐 라벨 일관성 확인(bull 레짐 라벨이 학습 구간과 테스트 구간에서 동일한 의미인지).

### 핵심 교훈

- HMM/GMM 레짐 탐지는 전략 수 추가보다 실전 성과 개선에 효과적이나, 상태 수(k) 과다 설정 시 오히려 과적합 악화.
- 크립토 고주파 시장에서는 Markovian 제약이 없는 GMM이 HMM보다 급변 구간 포착에 유리.
- 레짐 감지 없는 정적 봇은 2024 플래시 크래시처럼 레짐 전환 시 연쇄 손실 위험.
- 우리 프로젝트 최우선 과제: `src/data/regime_detector.py` 단일 파일로 변동성 기반 레짐 컬럼 주입, 기존 전략 코드 변경 최소화.
- 레짐 탐지 모델도 Walk-Forward 검증 필수 — 없으면 레짐 탐지 자체가 과최적화 원인이 됨.

---

## Cycle 135 Research Notes — 과최적화 방지 방법론

### 과최적화 탐지 방법

1. **Deflated Sharpe Ratio (DSR)** — Bailey & Lopez de Prado 제안. 다중 전략 테스트 시 선택 편향(selection bias)과 비정규 수익률 분포를 동시에 보정한 Sharpe. DSR < 1.0이면 과최적화 확률 높음. 현재 우리 기준(Sharpe >= 1.0)은 raw Sharpe라 DSR로 전환 시 대부분 탈락 예상. 78%의 발표된 전략이 아웃오브샘플에서 실패, Sharpe가 평균 63% 하락한다는 실증 데이터.

2. **Probability of Backtest Overfitting (PBO)** — 비모수적 방법. 여러 파라미터 조합 중 인샘플 최선 전략이 아웃오브샘플에서 중앙값 이하 성과를 낼 확률을 계산. PBO > 0.5면 과최적화. 파라미터 조합 수가 많을수록 PBO 급등 — 현재 355개 전략 병렬 운영 자체가 PBO를 극도로 높임.

3. **Combinatorial Purged Cross-Validation (CPCV)** — Walk-Forward의 단일 경로 의존 문제를 해결. 여러 train-test 분할을 조합적으로 생성하고, 시간 정보 누수를 막기 위해 purging(라벨 horizon 겹침 제거)과 embargo(테스트 후 구간 제외)를 적용. 연구 결과 WFO보다 PBO가 낮고 DSR이 높음 — 현 WFO 기반 검증보다 신뢰도 높음. mlfinlab 라이브러리에 구현체 있음.

### Walk-Forward 실패/성공 사례

- **실패 — 메타 과최적화(Meta-Overfitting)**: WFO 자체의 윈도우 크기, 피트니스 함수, 파라미터 범위를 반복 조정해서 WFO 결과가 좋아 보이도록 튜닝하는 행위. WFO의 목적(아웃오브샘플 검증)을 스스로 무효화함. 우리 프로젝트에서 Sharpe >= 1.0, MDD <= 20%, PF >= 1.5 기준을 맞추기 위해 파라미터를 재조정하는 것이 이에 해당.
- **실패 — 크립토 비정상성**: 변동성·유동성·뉴스 반응이 빠르게 바뀌는 크립토에서 WFO는 레짐 변화를 예측하지 못하고 반응만 함. 특히 스프레드와 유동성 변화가 순간적인 크립토에서 과거 윈도우가 미래를 대표하지 못함.
- **성공 기준 — Walk-Forward Efficiency (WFE)**: WFE = 아웃오브샘플 수익 / 인샘플 수익. WFE > 0.5(50%)이면 양호. 현재 우리 전략들의 WFE 계산 필요 — 이 지표 없이 PASS/FAIL 판단은 불완전.
- **성공 사례**: QuantConnect 문서 기준, WFO를 피트니스 함수 고정 + 윈도우 크기 사전 결정 후 절대 변경 안 하는 규율 유지 시 과최적화 방지 가능. 파라미터 범위도 사전 고정 필수.

### 최소 거래 수 통계적 유의성

- **현재 기준 15회는 통계적으로 불충분**: 중심극한정리 기준 최소 30회, 실용적 신뢰 수준은 100회 이상. 기관 표준은 200-500회(복수 시장 레짐 포함). 15회 기준은 단순 진입 허용선으로 의미 있으나 전략 신뢰성 판단 기준으로는 미달.
- **거래 수보다 레짐 다양성이 중요**: 단일 레짐(예: 2021 강세장) 500회 거래 < 복수 레짐(강세/약세/횡보) 100회 거래. 우리 백테스트 기간이 동일 레짐에 편중됐을 가능성 높음.
- **거래 간 독립성 문제**: 상관된 거래(같은 방향, 같은 시간대)가 많으면 유효 표본 크기(effective N)가 실제 거래 수보다 훨씬 작아짐. 355개 전략이 동시에 같은 방향 신호를 내면 사실상 N=1.
- **권장 최소 기준 상향**: Trades >= 15 → Trades >= 50 (최소), 이상적으로는 >= 100 + 강세/약세 레짐 각각 >= 20회 포함.

### 우리 프로젝트 적용 포인트

- **즉시 적용 가능**: `BacktestEngine` 기준에 WFE > 0.5 조건 추가, Trades >= 50으로 상향. 이것만으로도 현재 22개 PASS 중 다수 추가 탈락 예상 → 진짜 엣지 있는 전략만 남김.
- **DSR 계산 추가**: 현재 raw Sharpe >= 1.0 기준을 DSR >= 1.0으로 전환. 다중 전략 테스트 시 선택 편향 자동 보정. 구현: `scipy.stats`로 비정규성 보정 + log(전략 수) 패널티 적용.
- **PBO 모니터링**: 현재 355개 전략 조합 수가 많을수록 PBO 극단적으로 높음. 전략 수 축소(355 → 상위 20개)가 PBO 감소의 핵심. 더 많은 전략 추가는 과최적화를 악화시킴.
- **CPCV 장기 과제**: WFO를 CPCV로 전환하면 신뢰도 향상, mlfinlab 또는 자체 구현 필요. 단기 대안: WFO 윈도우/피트니스 함수를 한 번 결정 후 절대 변경 안 하는 규율 도입.
