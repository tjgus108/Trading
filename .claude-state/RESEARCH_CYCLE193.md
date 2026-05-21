# Cycle 193 Research — 온체인 데이터 & DEX/CEX 분석

_작성일: 2026-05-22_

---

## 1. 온체인 고래 추적 실전 효과 (2024–2026)

### 고래 지갑 추적의 신호 유효성

- 단기(1–5일) 반응: sub-50% 승률, 약한 음의 드리프트. 10–15일 누적 시 초과수익 +2%p 피크. 30일 이후 소멸(~+0.2%p).
- 2025년 8월 사례: 고래가 24,000 BTC($2.7B) 매도 → $500M 청산 유발. AI 기반 블록체인 API 연동 봇은 수 시간 전 패턴 감지 가능.
- 단독 신호로는 신뢰도 낮음. 거래량 서지, 매크로 시그널과 결합 필수.

### 거래소 유입/유출(Exchange Inflow/Outflow)

- 2025년 Coin Metrics 연구: 유입량이 30일 평균보다 **2표준편차 초과** 시, 이후 1주 내 유의미한 하락을 **72% 정확도**로 예측.
- BTC 일일 유입 30,000 BTC 초과 → 평균 -5.2% (1주 기준).
- 단, Chainalysis 2025 보고서: 외형상 유입의 **15–20%는 내부 이체** (false signal). 지갑 라벨링 품질이 핵심.
- **해석 규칙**: 유입 증가 = 매도 준비(bearish). 유출 증가 = 축적/장기 보유(bullish). 단일 스파이크보다 **지속 추세** 기준.

### NVT / MVRV / SOPR 실전 신뢰도

| 지표 | 강점 | 약점 |
|------|------|------|
| **NVT** | 4/5 주요 사이클 탑 포착. 낮은 NVT = 실사용 기반 | ETF 시대 이후 온체인 TX 감소로 왜곡 (2023→ 일일 TX 50만→25만으로 반감) |
| **MVRV Z-Score** | 모든 주요 사이클 탑/바텀 사후 식별 | $73K-74K 돌파 후 2차 랠리에서 클린한 exit 신호 실패 |
| **SOPR** | SOPR > 1 = 수익 실현 구간, < 1 = 손절 구간 | 원시 시리즈 노이즈 심함. **28일 변화율(delta)** 활용 권장 |

- 2025 AIAI 논문: 온체인 + 기술 지표 결합 CNN-LSTM → **82.44% 방향 정확도** (vs 기술 지표만: ~65%).
- IntoTheBlock 2025: 온체인+기술 결합 전략, 기술 단독 대비 **45% 높은 위험조정수익률**.
- 결론: 온체인 지표는 **중장기(주간 이상) 추세 식별**에 유효. 단기 정밀 타이밍에는 부적합.

---

## 2. 온체인 데이터 API 현황 (무료/유료)

| 플랫폼 | 무료 여부 | 핵심 지표 | 비고 |
|--------|-----------|-----------|------|
| **Glassnode** | 기본 무료 (제한적) | MVRV, SOPR, Exchange Flow, HODL Waves | 유료: Professional/Advanced. 무료는 시간 해상도·범위 제한 |
| **CryptoQuant** | API 유료 (Professional+) | Exchange Inflow/Outflow, Miner Flow, Funding Rate | MCP Server 베타: 245개 지표 일부 무료 접근 가능 (2026) |
| **IntoTheBlock** | $10/월, 7일 무료 | AI 기반 신호, 대규모 거래자 포지션 | 가장 저렴한 유료 |
| **Etherscan API** | 무료 (5 req/s) | 지갑 잔고, TX 내역, ERC20 이벤트 | ETH 온체인 직접 조회. BTC 불가 |
| **DeFiLlama** | 완전 무료 | TVL, 프로토콜 유동성 | DeFi 특화. REST API 공개 |
| **Dune Analytics** | 무료 쿼리 (속도 제한) | 커스텀 SQL 온체인 분석 | Dune Sim API: EVM+Solana 디코딩 |
| **blockchain.com / mempool.space** | 무료 | BTC 미확인 TX, 멤풀 수수료, UTXO | 원시 BTC 데이터 |

**우리 프로젝트에 실용적인 무료 조합**:
1. Etherscan API → ETH 고래 지갑 모니터링
2. mempool.space API → BTC 멤풀/대형 TX
3. DeFiLlama API → TVL 변화 (유동성 이탈 신호)
4. Glassnode 무료 티어 → SOPR, MVRV 기본값 (일 단위)

---

## 3. DEX vs CEX 유동성 분석

### 구조적 차이

- CEX: 중앙화 limit order book. 마켓메이커가 bid-ask 형성. 레이턴시 <1ms 가능.
- DEX (AMM): 스마트컨트랙트 가격 곡선(x*y=k). Uniswap V3의 **집중 유동성**은 특정 가격 구간에 유동성 집중 → 자본 효율 최대 **4,000배** 향상.

### DEX/CEX 차익거래 기회 (2025)

- 스프레드는 초기 대비 축소되었으나 수십 개 CEX + 수백 개 DEX 환경에서 여전히 일일 다수 기회 발생.
- Binance-Uniswap V3 시뮬레이션(2025.07–09): 슬롯 타임 단축 시 차익거래 TX 수 **535% 증가**, 거래량 **203% 증가**.
- 실전 한계: 성공하는 차익거래는 소수 "searcher" 집단이 block-builder 통합으로 지배. 진입장벽 높음.

### MEV의 영향

- 2024년 MEV 추출 규모: **$600M+**. 2020년 이후 누적 **$7.2B+**.
- 일반 DeFi 거래자 실질 비용: 합법적 수수료 외 **0.5–2% 추가 MEV 세금**.
- MEV 유형:
  - **샌드위치 공격**: 대형 스왑 전후로 봇이 매수/매도 → 체결가 악화
  - **프론트런닝**: 멤풀 TX 감지 후 먼저 체결
  - **청산 봇**: DeFi 담보 청산 포착
- 대응책: private mempool (Flashbots Protect), slippage tolerance 최소화, 소액 분할 주문.
- **우리 봇 영향**: CEX(Bybit) 중심이므로 MEV 직접 피해 없음. DEX 연동 시 private RPC 사용 필수.

### DEX Aggregator vs 직접 호출

| | DEX Aggregator (1inch, Jupiter) | 직접 DEX 호출 |
|---|---|---|
| 장점 | 최적 라우팅, 분산 유동성 통합, 가격 개선 | 단순, 투명, 가스 절약 가능 |
| 단점 | 라우팅 레이어 추가 → 가스 증가 | 단일 풀 유동성만 사용 |
| 추천 규모 | $1K–$50K: 1inch Fusion/ParaSwap | <$1K 또는 유동성 집중 페어 |
| 체인별 | EVM: 1inch/CowSwap, Solana: Jupiter | 체인 특화 DEX |

---

## 4. 트레이딩봇 인프라 트렌드 (2025)

### Python vs Rust/C++

| | Python | Rust |
|---|---|---|
| 속도 | 느림 (GIL, 인터프리터) | C++ 수준. GC 없음 → 예측 가능한 레이턴시 |
| 메모리 | 봇당 100–200 MiB | 봇당 5–10 MiB |
| 개발속도 | 빠름. 데이터 분석 생태계 풍부 | 느림. 컴파일 타임 학습 필요 |
| 크립토 적합성 | 중저빈도(초 단위) 전략 충분 | 밀리초 이하 전략 |

- **실용적 결론**: 우리 프로젝트(Bybit 연동, 분/시간봉 전략)에서 Python 성능은 병목이 아님. 병목은 **거래소 API 레이턴시** (모두 HTTPS/WebSocket, 하드웨어 가속 불가).
- 하이브리드 패턴: 전략 로직/ML Python + 주문 실행 Rust. 현재 규모에서는 과잉 엔지니어링.

### 코로케이션(Colocation) vs 클라우드

- 전통 금융: 코로케이션으로 20–30% 레이턴시 개선. CME 코로케이션 $12,000/월.
- 크립토 현실: 거래소 API가 HTTPS/WebSocket → 하드웨어 가속 불가. 한 트레이더 사례: $30K 들여 800μs → 200μs 최적화 후 체결률 변화 없음 (병목: 거래소 처리 시간).
- **결론**: 크립토 봇의 경우 **거래소 근처 클라우드 리전**(예: AWS us-east-1 for Binance, AWS ap-northeast-1 for Bybit) VPS로 충분. 전용 코로케이션 불필요.
- 권장 스펙: VPS 2–4 vCPU, 4–8GB RAM, SSD. 위치는 거래소 데이터센터 근접 리전.

---

## 5. 우리 프로젝트 적용 가능한 온체인 신호 추천

### 구현 난이도 vs 효과 매트릭스

| 우선순위 | 지표 | 데이터 소스 | 구현 난이도 | 예상 효과 | 신호 방향 |
|----------|------|------------|------------|----------|----------|
| **1** | BTC Exchange Netflow (거래소 순유입) | mempool.space / Glassnode 무료 | 낮음 | 중상 | 유입 증가 → Bearish |
| **2** | SOPR 28일 Delta | Glassnode 무료 (일별) | 중간 | 중상 | delta > 0 가속 → 과매수 경고 |
| **3** | Stablecoin Exchange Inflow | Etherscan API (USDT 대형 이체 추적) | 중간 | 중 | 스테이블 유입 → 매수 대기 자금 bullish |
| **4** | DeFiLlama TVL 급감 | DeFiLlama API (무료) | 낮음 | 중 | TVL -10% 이상 → 리스크 오프 신호 |
| **5** | 대형 지갑 잔고 변화 (whale wallet delta) | Etherscan API | 높음 | 중 | Top-100 지갑 순매도 → Bearish |

### 구현 권고사항

1. **1순위 (Exchange Netflow)**: `src/data/` 에 `onchain_feed.py` 모듈 추가. mempool.space REST API는 완전 무료이며 BTC 대형 TX 실시간 조회 가능. 시그널은 전략 필터(confidence 조정)로 활용, 단독 진입 신호로 사용 금지.

2. **2순위 (SOPR Delta)**: Glassnode 무료 티어에서 일별 SOPR CSV 다운로드 → 28일 변화율 계산. 자동화 시 Glassnode 유료 API 필요하므로 초기엔 수동 갱신 파이프라인으로 시작.

3. **4순위 (TVL)**: DeFiLlama `/api/protocols` 엔드포인트 → TVL 일변화율 계산. 완전 무료, 구현 쉬움. 리스크 오프 필터로 활용.

### 통합 방식 권고

온체인 신호는 **독립 전략이 아닌 기존 전략의 confidence 조정 레이어**로 구현 권장:
- Exchange Netflow bearish + 기존 전략 BUY → confidence 한 단계 하향 (HIGH → MEDIUM)
- TVL 급감 + 기존 전략 BUY → HOLD로 전환 검토
- 이 방식으로 355+ 전략 재개발 없이 온체인 정보 활용 가능.

---

## 참고 자료

- [Whale Tracking Signal Research - ainvest](https://www.ainvest.com/news/real-time-whale-tracking-crypto-alerts-signal-major-market-move-2601/)
- [Exchange Netflow Predictive Power - Gate Wiki](https://web3.gate.com/crypto-wiki/article/how-does-exchange-net-inflow-outflow-predict-cryptocurrency-price-movements)
- [MVRV/SOPR/NVT 2025 - Glassnode Insights](https://insights.glassnode.com/sth-lth-sopr-mvrv/)
- [Bitcoin Price Top Indicators Failed - Bitcoin Magazine](https://bitcoinmagazine.com/markets/why-bitcoin-price-top-indicators-failed)
- [CryptoQuant API Docs](https://cryptoquant.com/docs)
- [DeFiLlama](https://dune.com/home)
- [DEX-CEX Arbitrage 2025 - Bitium](https://blog.bitium.agency/dex-cex-arbitrage-guide-in-2025-new-opportunities-for-builders-848f44ef0f48)
- [MEV Implications - ESMA Report 2025](https://www.esma.europa.eu/sites/default/files/2025-07/ESMA50-481369926-29744_Maximal_Extractable_Value_Implications_for_crypto_markets.pdf)
- [Python vs Rust Trading Bot - DEV Community](https://dev.to/frankdotdev/switching-from-python-to-rust-a-high-frequency-trading-case-study-34hc)
- [Colocation vs Cloud Crypto - Medium](https://medium.com/@laostjen/high-frequency-trading-in-crypto-latency-infrastructure-and-reality-594e994132fd)
- [1inch vs Jupiter Aggregators 2026 - eco.com](https://eco.com/support/en/articles/13314092-best-dex-aggregators-in-2026-1inch-jupiter-paraswap-and-more)
- [Free Onchain Tools - Phemex](https://phemex.com/news/article/top-free-onchain-analysis-tools-for-crypto-analysts-35037)
