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
