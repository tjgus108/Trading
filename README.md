# Trading Bot — 사용 매뉴얼

> ccxt 기반 암호화폐 자동 트레이딩봇. Python 3.11+

---

## 목차
1. [빠른 시작](#1-빠른-시작)
2. [설치](#2-설치)
3. [설정](#3-설정)
4. [실행 옵션](#4-실행-옵션)
5. [전략 목록](#5-전략-목록-9종)
6. [ML 모델 학습](#6-ml-모델-학습)
7. [백테스트](#7-백테스트)
8. [알파 소스](#8-알파-소스)
9. [리스크 관리](#9-리스크-관리)
10. [대시보드](#10-대시보드)
11. [아키텍처](#11-아키텍처)
12. [테스트](#12-테스트)
13. [트러블슈팅](#13-트러블슈팅)

---

## 1. 빠른 시작

```bash
# API 키 없이 전체 기능 체험 (합성 데이터)
python3 main.py --demo --tournament --dashboard

# ML 학습 후 실행
python3 scripts/train_ml.py --demo --model rf
python3 main.py --demo --tournament --dashboard
```

---

## 2. 설치

### 필수 의존성
```bash
pip install ccxt pandas numpy python-dotenv requests
```

### 선택 의존성 (없어도 동작)
| 패키지 | 기능 | 설치 |
|---|---|---|
| scikit-learn | RandomForest ML | `pip install scikit-learn` |
| torch | LSTM (없으면 numpy fallback) | `pip install torch` |
| websockets | Binance WebSocket (없으면 REST) | `pip install websockets` |
| openai | GPT-4o 앙상블 (없으면 Claude 단독) | `pip install openai` |
| anthropic | Claude 분석/앙상블 (없으면 mock) | `pip install anthropic` |

---

## 3. 설정

### `.env` 파일 (루트에 생성)
```env
# 거래소 API
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret

# 알림 (선택)
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# LLM (선택)
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key

# 뉴스 (선택)
CRYPTOPANIC_API_KEY=your_key
```

### `config/settings.json` 주요 설정
| 파라미터 | 기본값 | 설명 |
|---|---|---|
| `symbol` | `"BTC/USDT"` | 거래 심볼 |
| `timeframe` | `"1h"` | 캔들 주기 |
| `capital` | `10000` | 초기 자본 (USD) |
| `risk_per_trade` | `0.01` | 트레이드당 리스크 (1%) |
| `max_daily_loss` | `0.05` | 일일 최대 손실 (5%) |
| `max_drawdown` | `0.20` | 최대 낙폭 (20%) |

---

## 4. 실행 옵션

```
python3 main.py [OPTIONS]
```

| 옵션 | 설명 |
|---|---|
| `--demo` | MockExchangeConnector 사용 (API 키 불필요) |
| `--live` | 실거래 모드 (API 키 필요, backtest gate 자동) |
| `--tournament` | 전략 토너먼트 실행 후 최고 전략 선택 |
| `--loop` | 캔들 마감마다 반복 실행 |
| `--dashboard` | 웹 대시보드 (기본 포트 8080) |
| `--websocket` | Binance WebSocket 실시간 피드 (REST fallback) |
| `--ensemble` | Claude + GPT-4o 앙상블 신호 |
| `--walk-forward` | Walk-Forward 파라미터 최적화 후 실행 |

### 권장 조합

```bash
# 데모 전체 기능
python3 main.py --demo --tournament --dashboard

# 실거래 풀 스택
python3 main.py --live --websocket --ensemble --walk-forward --loop --dashboard

# 백테스트만
python3 main.py --demo --tournament
```

---

## 5. 전략 목록 (9종)

| 이름 | 설명 | 예상 Sharpe | 데이터 요구사항 |
|---|---|---|---|
| `ema_cross` | EMA20/50 골든/데드크로스 | 0.5~1.0 | OHLCV |
| `donchian_breakout` | 20바 Donchian 채널 돌파 | 0.5~1.2 | OHLCV |
| `funding_rate` | 펀딩비 역추세 (극단값 반전) | 1.66~3.5 | OHLCV + 펀딩비 |
| `residual_mean_reversion` | BTC-neutral 잔차 z-score | ~2.3 | OHLCV |
| `pair_trading` | BTC-ETH 공적분 스프레드 | ~2.45 | BTC+ETH OHLCV |
| `ml_rf` | RandomForest (15피처) | 학습 의존 | OHLCV + 학습 필요 |
| `ml_lstm` | LSTM 2-layer (torch/numpy) | 학습 의존 | OHLCV + 학습 필요 |
| `rsi_divergence` | RSI 강세/약세 다이버전스 | 0.8~1.5 | OHLCV |
| `bb_squeeze` | Bollinger Band 스퀴즈 돌파 | 0.7~1.3 | OHLCV |

### 전략 토너먼트
```bash
# 9개 전략 병렬 백테스트 → Sharpe 순위 → 최고 전략 자동 선택
python3 main.py --demo --tournament
```
- 기준: Sharpe≥1.0, MDD≤20%, PF≥1.5, 거래≥30
- 72사이클마다 자동 재평가 (C3 auto-tournament)

---

## 6. ML 모델 학습

### RandomForest
```bash
# 데모 데이터로 학습
python3 scripts/train_ml.py --demo --model rf

# 실제 데이터로 학습 (API 키 필요)
python3 scripts/train_ml.py --symbol BTC/USDT --timeframe 1h --limit 2000 --model rf
```

### LSTM
```bash
# numpy fallback (torch 없이)
python3 scripts/train_ml.py --demo --model lstm

# PyTorch LSTM (torch 설치 시)
pip install torch
python3 scripts/train_ml.py --demo --model lstm
```

- 모델 저장 경로: `models/rf_btcusdt_<date>.pkl` / `models/lstm_btcusdt_<date>.pt`
- 통과 기준: test_accuracy ≥ 54%
- Walk-Forward: 60/20/20 시간순 분할 (train/val/test)

**15개 학습 피처**: return_1/3/5/10/20, RSI14, RSI z-score, ATR%, volatility_20, EMA ratio, price_vs_EMA20/50, volume_ratio_20, Donchian%, price_vs_VWAP

---

## 7. 백테스트

```python
from src.backtest.engine import BacktestEngine
from src.strategy.ema_cross import EmaCrossStrategy

engine = BacktestEngine()
result = engine.run(EmaCrossStrategy(), df)
print(result.summary())
```

### Walk-Forward 최적화
```python
from src.backtest.walk_forward import optimize_ema_cross

result = optimize_ema_cross(df, n_windows=3)
print(result.summary())
# STABLE이면 result.best_params 사용
```

- IS/OOS 비율 < 0.5 → 과최적화 경고
- OOS Sharpe std > 0.8 → UNSTABLE 판정

---

## 8. 알파 소스

### 감성 지표 (B1)
```python
from src.data.sentiment import SentimentFetcher
sf = SentimentFetcher()
score = sf.get_score()          # -3 ~ +3
# 데모: SentimentFetcher.mock()
```
- Fear & Greed Index (alternative.me, 무료)
- Binance 펀딩비 / 미결제약정

### 온체인 지표 (B2)
```python
from src.data.onchain import OnchainFetcher
oc = OnchainFetcher()
score = oc.get_score()          # -3 ~ +3
# 데모: OnchainFetcher.mock()
```
- blockchain.com: 해시레이트, 거래량, 거래소 유입량
- Glassnode (API 키 필요 시)

### 뉴스 모니터 (B3)
```python
from src.data.news import NewsMonitor
nm = NewsMonitor()
events = nm.get_latest_events()
# HIGH: hack/exploit/breach → 진입 자동 차단
```
- CryptoPanic API (무료 티어 지원)
- HIGH/MEDIUM/LOW 자동 분류

### MarketContext 통합
```python
from src.alpha.context import MarketContextBuilder
ctx = MarketContextBuilder().build(use_mock=True)
# ctx.composite_score: -3 ~ +3
# ctx.adjust_signal(signal) → 신호 조정/차단
```
- composite_score = sentiment×0.6 + onchain×0.4
- HIGH 뉴스 시 진입 완전 차단

### Order Flow (실시간)
```python
from src.data.order_flow import OrderFlowFetcher
of = OrderFlowFetcher()
score = of.get_score()          # OFI 기반 -3 ~ +3
```
- Binance depth API (상위 20호가)
- OFI = (bid_vol - ask_vol) / total_vol

---

## 9. 리스크 관리

### 서킷 브레이커 (하드코딩, LLM 개입 없음)
| 조건 | 동작 |
|---|---|
| 일일 손실 ≥ `max_daily_loss` | 당일 거래 중단 |
| 낙폭 ≥ `max_drawdown` | 봇 종료 |
| 연속 손실 ≥ 5회 | 거래 일시 중단 |
| 5분 내 가격 ≥ 10% 급락 | 플래시크래시 감지, 즉시 중단 |

### 포지션 사이징
- 트레이드당 자본의 `risk_per_trade`% 리스크
- ATR 기반 손절 자동 계산
- 최대 포지션: 자본의 10%

---

## 10. 대시보드

```bash
python3 main.py --demo --dashboard
# http://localhost:8080 접속
```

- 30초 자동 갱신
- 현재 포지션 / 일일 PnL / 전략 토너먼트 결과
- 서킷 브레이커 상태
- stdlib HTTP (외부 의존성 없음)

---

## 11. 아키텍처

```
main.py
  └── BotOrchestrator
        ├── DataFeed (OHLCV 수집)
        │     ├── ExchangeConnector (ccxt)
        │     └── BinanceWebSocketFeed (실시간)
        ├── MarketContextBuilder (알파 소스 통합)
        │     ├── SentimentFetcher (Fear&Greed, 펀딩비)
        │     ├── OnchainFetcher (blockchain.com)
        │     └── NewsMonitor (CryptoPanic)
        ├── Strategy Tournament
        │     └── BacktestEngine (Sharpe/MDD/PF/거래수)
        ├── TradingPipeline
        │     ├── BaseStrategy.generate() → Signal
        │     ├── MarketContext.adjust_signal()
        │     ├── MultiLLMEnsemble (Claude + GPT-4o)
        │     ├── LLMAnalyst (분석 텍스트, 주문 금지)
        │     └── RiskManager → 포지션 사이즈/손절
        ├── PositionTracker / DailyPnL
        ├── CircuitBreaker (하드코딩)
        ├── TelegramNotifier
        └── Dashboard (HTTP)
```

### 주요 디렉토리
```
src/
  strategy/   — 9개 매매 전략
  exchange/   — ccxt 연결, MockConnector
  data/       — OHLCV, WebSocket, 감성/온체인/뉴스/주문흐름
  alpha/      — MarketContext, LLMAnalyst, Ensemble
  ml/         — FeatureBuilder, Trainer, RF/LSTM 모델
  backtest/   — BacktestEngine, WalkForwardOptimizer
  pipeline/   — TradingPipeline (신호→주문 흐름)
  risk/       — RiskManager, CircuitBreaker
scripts/
  train_ml.py — ML 학습 CLI
tests/        — 단위/통합 테스트 (294 passed)
models/       — 학습된 모델 저장 (.pkl / .pt)
config/       — 설정 파일
.claude-state/ — 작업 상태 파일
```

---

## 12. 테스트

```bash
# 전체 테스트
~/Library/Python/3.9/bin/pytest tests/ -q

# 특정 모듈
~/Library/Python/3.9/bin/pytest tests/test_backtest_engine.py -v
~/Library/Python/3.9/bin/pytest tests/test_lstm_strategy.py -v

# 결과: 294 passed, 11 skipped
# skipped: scikit-learn / torch 미설치 시 자동 스킵
```

---

## 13. 트러블슈팅

### API 연결 실패
```
ConnectionError: binance ...
```
→ `.env`의 API 키 확인. 샌드박스 테스트: `EXCHANGE_SANDBOX=true`

### ML 모델 없음 (HOLD만 반환)
```
MLRFStrategy: 모델 없음 — HOLD fallback
```
→ `python3 scripts/train_ml.py --demo --model rf` 실행

### sklearn 미설치 (테스트 스킵)
```
SKIPPED [sklearn not installed]
```
→ `pip install scikit-learn` 후 재실행

### torch 미설치 (numpy fallback)
```
LSTMSignalGenerator: torch=False
```
→ 정상 동작 (numpy 모멘텀 fallback). PyTorch 원하면 `pip install torch`

### 모든 전략 FAIL (백테스트)
```
donchian_breakout: 거래 없음
```
→ MockExchangeConnector는 합성 데이터 사용. 실제 데이터에서 재검증 필요.
→ `funding_rate`는 펀딩비 데이터 주입 필요, `pair_trading`은 ETH 데이터 필요.

### WebSocket 연결 끊김
- 자동 재연결 (MAX_RETRY=5, 지수 백오프)
- 최종 실패 시 REST fallback 자동 전환

---

## 변경 이력

| Phase | 내용 |
|---|---|
| 인프라 | BotOrchestrator, BacktestEngine, RiskManager, Dashboard, Telegram |
| Phase A | FundingRate, ResidualMeanReversion, PairTrading 전략 |
| Phase B | SentimentFetcher, OnchainFetcher, NewsMonitor, MarketContext |
| Phase C | FeatureBuilder, WalkForwardTrainer, MLRFStrategy, LLMAnalyst, auto-tournament |
| Phase D | MultiLLMEnsemble, BinanceWebSocket, WalkForwardOptimizer, LSTM, OrderFlow |
| 추가 | RsiDivergence, BbSqueeze, scripts/train_ml.py |
