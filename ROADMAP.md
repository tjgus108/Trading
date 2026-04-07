# Trading Bot Roadmap

리서치 기반 (2025~2026 실증 데이터):
- Funding Rate 역추세: Sharpe 1.66~3.5 (ScienceDirect 2025)
- BTC-Neutral 평균회귀: Sharpe 2.3 (Medium, briplotnik)
- BTC-ETH 페어 트레이딩: Sharpe 2.45, 연 16.34% (Springer 2024)
- TradingAgents 멀티에이전트: 모든 기존 전략 대비 Sharpe 상승 (ICML 2025)
- Claude 봇 $1 → $3.3M Polymarket 차익거래 (2026.04)
- 비용 최적화: 태스크별 모델 라우팅 + 배치 API → 최대 95% 절감

---

## Phase A — 신규 전략 3종 (이번 스프린트)
**담당: strategy-researcher-agent**

### A1. Funding Rate 역추세 ★ 최우선
- 원리: 펀딩비 +0.03% 이상(롱 과밀) → 숏, -0.01% 이하(숏 과밀) → 롱
- 실증: Sharpe 1.66~3.5, Calmar Ratio 5~10
- 데이터: Binance API 무료, 8시간 주기
- 파일: `src/strategy/funding_rate.py`

### A2. BTC-Neutral 잔차 평균회귀 ★ 고우선
- 원리: 알트코인 수익률에서 BTC 영향 제거(rolling regression) → 잔차 z-score ±2 역방향 진입
- 실증: Sharpe 2.3, 2021년 이후 특히 강함
- 파일: `src/strategy/residual_mean_reversion.py`

### A3. BTC-ETH 페어 트레이딩
- 원리: Engle-Granger 공적분 → 스프레드 z-score ±2 진입/0 청산
- 실증: 연 16.34%, Sharpe 2.45, 변동성 8.45% (2019~2024)
- 파일: `src/strategy/pair_trading.py`

---

## Phase B — 알파 소스 확장 (다음 스프린트)
**담당: sentiment-agent, onchain-agent, news-agent**

### B1. 감성 + 펀딩비 통합
- Fear & Greed Index (alternative.me 무료)
- 펀딩비 + Open Interest ccxt로 직접 수집
- alpha-agent의 Bull/Bear 토론 컨텍스트에 점수 주입

### B2. 온체인 데이터
- Exchange Inflow/Outflow (CryptoQuant 무료 tier)
- NVT Ratio, Whale 추적 (checkonchain 무료)
- 신호: 거래소 순유입 급증 → 매도 경계

### B3. 뉴스 이벤트 리스크
- 규제 발표, 해킹, ETF 이벤트 감지
- HIGH 이벤트 시 포지션 50% 자동 축소

---

## Phase C — ML/LLM 고도화 (중기)
**담당: ml-agent, alpha-agent**

### C1. ML 신호 생성기
- RandomForest (초기): 기술 지표 → BUY/SELL/HOLD 확률
- LSTM (고도화): 시계열 패턴 학습
- 실증: ETH ML 모델 연 97%, Sharpe 2.5 (ACM 2025) — 오버피팅 주의
- Walk-forward validation 필수

### C2. LLM 시장 분석 통합
- alpha-agent가 Claude API 직접 호출 (이벤트 기반)
- 패턴: LLM은 뉴스/감성 분석만, 주문은 규칙 기반
- 실증: TD3+FinGPT Sharpe 1.38 (arXiv 2510.10526)
- 비용: Haiku(분류) + Sonnet(분석) + 배치 API → 최대 95% 절감

### C3. 전략 자동 재평가 주기
- tournament 매 72사이클 자동 실행 (1h 기준 3일마다)
- 시장 체제 변화 감지 후 전략 자동 교체

---

## Phase D — 인프라 고도화 (장기)
**담당: data-agent, backtest-agent**

### D1. 멀티 LLM 앙상블
- Claude + GPT-4o 동시 신호 → 합의 시 진입
- 사례: Multi-LLM 봇 비용 $340 → $136/월

### D2. 실시간 WebSocket 피드
- REST polling → Binance WebSocket (지연 최소화)
- Order Flow Imbalance 실시간 감지

### D3. Walk-Forward 최적화
- in-sample 학습 → out-of-sample 검증 반복
- 과최적화 방지 + 전략 파라미터 자동 튜닝

---

## 에이전트 배정 현황

| 에이전트 | 모델 | Phase A 할 일 | Phase B 할 일 |
|---|---|---|---|
| strategy-researcher-agent | Sonnet | A1~A3 전략 구현 + 백테스트 | 새 전략 지속 탐색 |
| backtest-agent | Haiku | A1~A3 검증 (PASS/FAIL) | C1 ML 모델 성과 검증 |
| sentiment-agent | Haiku | (대기) | B1 Fear&Greed + 펀딩비 수집 |
| onchain-agent | Haiku | (대기) | B2 온체인 신호 수집 |
| news-agent | Haiku | (대기) | B3 이벤트 리스크 감지 |
| ml-agent | Sonnet | (대기) | (대기) → C1 |
| alpha-agent | Sonnet | A1~A3 신호 검토 | B1~B3 컨텍스트 통합 |
| risk-agent | Sonnet | 계속 운영 | 계속 운영 |
| orchestrator | Sonnet | Phase A 조율 | Phase B 조율 |
| data-agent | Haiku | 계속 운영 | D2 준비 |
| reviewer | Haiku | A1~A3 코드 검토 | 계속 운영 |

---

## 핵심 원칙 (리서치 기반)

1. **모멘텀 + 평균회귀 조합** — 단독보다 결합(50:50)이 Sharpe 향상
2. **펀딩비가 가장 즉시 활용 가능한 알파** — 무료 데이터, 코드 단순
3. **LLM은 분석가, 주문은 코드** — 환각 위험 차단
4. **비용**: Haiku(반복작업) / Sonnet(추론) / 배치 API(비동기) → 95% 절감
5. **백테스트 없이 live 없음** — backtest gate 항상 유지
