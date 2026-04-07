# Trading Bot Roadmap

리서치 기반 (2025~2026 최신 사례):
- Claude 봇이 Polymarket에서 $1 → $3.3M 달성 (차익거래 속도 우위)
- Claude Opus 4.5가 자율적으로 전략 개발 → 시장 수익률 초과
- Multi-LLM 봇 (DeepSeek + Claude + GPT-4o + Grok) API 비용 $340 → $136/월
- Funding rate 역추세 전략, On-chain data, Order flow가 2024~2025 핵심 알파 소스

---

## Phase A — 즉시 구현 가능한 전략 (이번 스프린트)

### A1. Funding Rate 역추세 전략
**원리:** 영구선물 펀딩비가 과도하게 양수면 롱 과부하 → 하락 예측, 음수면 반대
**알파 소스:** Binance 펀딩비 API (8시간 주기)
**구현:** `src/strategy/funding_rate.py`
**담당:** strategy-researcher-agent → alpha-agent 검증 → backtest-agent

### A2. RSI 다이버전스 전략
**원리:** 가격 신고가 + RSI 낮아지면 약세 다이버전스, 진입 신호
**구현:** `src/strategy/rsi_divergence.py`
**담당:** strategy-researcher-agent

### A3. 볼린저밴드 Squeeze
**원리:** 변동성 수축(squeeze) 후 이탈 방향으로 진입
**구현:** `src/strategy/bb_squeeze.py`
**담당:** strategy-researcher-agent

---

## Phase B — 데이터 소스 확장 (다음 스프린트)

### B1. 감성 분석 에이전트
**원리:** Fear & Greed Index + Reddit/Twitter 감성 → 시장 과열 감지
**데이터:** alternative.me API (무료), CryptoQuant 감성 지표
**담당:** sentiment-agent (신규)

### B2. On-Chain 데이터
**원리:** Exchange 유입/유출, 고래 지갑 움직임, NVT ratio
**데이터:** Glassnode API (유료) 또는 checkonchain (무료)
**담당:** onchain-agent (신규)

### B3. 뉴스/이벤트 감지
**원리:** 중요 뉴스 발생 시 변동성 급증 → 포지션 축소 or 진입 기회
**담당:** news-agent (신규)

---

## Phase C — ML/LLM 고도화 (중기)

### C1. LLM 시장 분석 (Claude API 직접 호출)
**원리:** alpha-agent가 Claude API로 시장 컨텍스트 분석 + 신호 품질 점수 부여
**비용 최적화:** Haiku로 일상 분석, Sonnet은 중요 결정만
**담당:** alpha-agent 고도화

### C2. ML 신호 생성기
**원리:** CNN-LSTM으로 과거 패턴 학습 → BUY/SELL/HOLD 확률 출력
**라이브러리:** scikit-learn (초기), torch (고도화)
**담당:** ml-agent (신규)

### C3. 전략 자동 재평가
**원리:** 매 N 사이클마다 tournament 재실행 → 시장 체제 변화 감지
**담당:** orchestrator (tournament_interval 설정)

---

## Phase D — 인프라 고도화 (장기)

### D1. 멀티 LLM 앙상블
**원리:** Claude + GPT-4o 신호 동시 생성 → 합의 시만 진입 (비용 $340 → $136 사례 참고)
**담당:** alpha-agent 확장

### D2. 실시간 WebSocket 데이터
**원리:** REST polling → WebSocket 실시간 피드로 지연 최소화
**담당:** data-agent 고도화

### D3. 백테스트 워크포워드 최적화
**원리:** 과최적화 방지: in-sample 최적화 → out-of-sample 검증 반복
**담당:** backtest-agent 고도화

---

## 에이전트 팀 (업데이트)

| 에이전트 | 모델 | 역할 | 상태 |
|---|---|---|---|
| orchestrator | Sonnet | 전체 조율, 로드맵 계획 | 기존 |
| data-agent | Haiku | OHLCV + 지표 | 기존 |
| alpha-agent | Sonnet | 신호 생성 (Bull/Bear) | 기존 |
| risk-agent | Sonnet | 게이트키퍼 | 기존 |
| execution-agent | Haiku | 주문 실행 | 기존 |
| backtest-agent | Haiku | 전략 검증 | 기존 |
| memory-agent | Haiku | 상태 저장 | 기존 |
| researcher | Haiku | 코드 탐색 | 기존 |
| reviewer | Haiku | 코드 검토 | 기존 |
| **strategy-researcher-agent** | **Sonnet** | **신규 전략 리서치 + 초안 구현** | **신규** |
| **sentiment-agent** | **Haiku** | **감성/공포탐욕/펀딩비 수집** | **신규** |
| **onchain-agent** | **Haiku** | **온체인 데이터 수집 + 신호** | **신규** |
| **news-agent** | **Haiku** | **뉴스/이벤트 감지** | **신규** |
| **ml-agent** | **Sonnet** | **ML 모델 학습/추론** | **신규** |
