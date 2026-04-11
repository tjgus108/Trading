# Paper Trading 모드 활성화 가이드

## 개요
Paper Trading은 실제 거래소 API 호출 없이 모의거래를 수행하는 모드입니다.
슬리피지, 부분체결, 타임아웃 시뮬레이션을 포함하여 현실적인 거래 환경을 모방합니다.

## 현재 구현 상태

### 1. PaperTrader 클래스 (`src/exchange/paper_trader.py`)
- **포지션 관리**: BUY/SELL 신호를 처리하고 평균진입가 계산
- **잔액 관리**: 수수료(fee)를 고려한 잔액 업데이트
- **슬리피지 시뮬레이션**: ±slippage_pct 범위 내 임의 변동 적용
- **부분체결**: partial_fill_prob 확률로 50~80% 만 채워짐
- **타임아웃**: timeout_prob 확률로 주문 타임아웃 시뮬레이션
- **성과 요약**: P&L, 승률, 평균 슬리피지 등 통계 제공

### 2. PaperConnector 클래스 (`src/exchange/paper_connector.py`)
- ExchangeConnector 인터페이스 호환
- orchestrator/pipeline과 통합 가능
- `create_order()` → PaperTrader.execute_signal() 매핑
- `fetch_balance()` → 현재 계좌 잔액 반환

### 3. 테스트 커버리지 (`tests/test_paper_trader.py`)
- 기본 기능: 생성, BUY/SELL, 잔액 관리 (16개 테스트)
- 고급 기능: 슬리피지, 부분체결, 타임아웃, 리셋 (6개 테스트)
- **전체 22개 테스트 통과**

## 사용 방법

### 방법 1: Orchestrator에서 PaperConnector 사용 (권장)

```python
from src.orchestrator import Orchestrator
from src.config import AppConfig
from src.exchange.paper_connector import PaperConnector

cfg = AppConfig.from_yaml("config/config.yaml")
orch = Orchestrator(cfg)

# demo=True 시 MockExchangeConnector 대신 PaperConnector 사용
# (현재는 demo=True → MockExchangeConnector이므로 수정 필요)
orch._connect(mock=False)  # 실제 connector 초기화
# orch._connector = PaperConnector(symbol=cfg.trading.symbol)  # 수동 교체
```

### 방법 2: 직접 PaperTrader 사용

```python
from src.exchange.paper_trader import PaperTrader

# 초기화 (매개변수는 모두 선택사항)
pt = PaperTrader(
    initial_balance=10000.0,      # 초기 잔액 (기본값 10000)
    fee_rate=0.001,               # 거래 수수료 (기본값 0.1%)
    slippage_pct=0.05,            # 슬리피지 범위 (기본값 ±0.05%)
    partial_fill_prob=0.05,       # 부분체결 확률 (기본값 5%)
    timeout_prob=0.01,            # 타임아웃 확률 (기본값 1%)
)

# 신호 실행
result = pt.execute_signal(
    symbol="BTC/USDT",
    action="BUY",                 # 또는 "SELL"
    price=45000.0,                # 진입/청산 가격
    quantity=0.1,                 # 수량
    strategy="breakout",          # 전략명
    confidence="HIGH",            # 신뢰도
)

# 결과 확인
print(result)
# {
#   "status": "filled",              # 또는 "partial", "timeout", "rejected", "error"
#   "symbol": "BTC/USDT",
#   "action": "BUY",
#   "requested_price": 45000.0,
#   "actual_price": 44977.5,         # 슬리피지 적용
#   "requested_quantity": 0.1,
#   "actual_quantity": 0.1,
#   "fee": 4.5,
#   "pnl": 0.0,                      # BUY는 0, SELL은 실현손익
#   "slippage_pct": -0.05,           # 음수면 유리, 양수면 불리
#   "balance": 9955.5,               # 업데이트된 잔액
# }

# 성과 요약
summary = pt.get_summary()
print(summary)
# {
#   "initial_balance": 10000.0,
#   "current_balance": 9955.5,
#   "total_pnl": -44.5,
#   "total_return_pct": -0.4450,
#   "trade_count": 1,
#   "sell_count": 0,
#   "win_rate": 0.0,
#   "avg_slippage_pct": -0.05,
#   "open_positions": {"BTC/USDT": 0.1},
#   "open_position_value": 4500.0,
# }

# 계좌 초기화 (테스트용)
pt.reset()
```

### 방법 3: Config 파일을 통한 설정 (향후)

현재 config.yaml는 `dry_run` 옵션만 있으나, 다음과 같이 확장 가능:

```yaml
exchange:
  name: bybit
  sandbox: false
  paper_trading: true  # 신규: paper trading 활성화
  paper_trading_config:  # 신규: 옵션
    initial_balance: 10000.0
    slippage_pct: 0.05
    partial_fill_prob: 0.05
    timeout_prob: 0.01
```

## Orchestrator 통합 체크리스트

### 현재 상태
- `orchestrator._connect(mock=False)` → ExchangeConnector (실거래 또는 sandbox)
- `orchestrator._connect(mock=True)` → MockExchangeConnector (데이터 없이 더미)

### 향상 사항 (향후 PR)
- [ ] Config에 `paper_trading` 플래그 추가
- [ ] Orchestrator 초기화 로직에서:
  ```python
  if cfg.exchange.paper_trading:
      self._connector = PaperConnector(...)
  elif cfg.exchange.mock:
      self._connector = MockExchangeConnector(...)
  else:
      self._connector = ExchangeConnector(...)
  ```
- [ ] `dry_run=True`와 `paper_trading=True` 구분
  - `dry_run=True` + `paper_trading=False`: 신호 출력만 (주문 미제출)
  - `dry_run=False` + `paper_trading=True`: 모의거래 실행 (주문 시뮬레이션)

## 성능 비교

### 기존 dry_run=True (신호 출력만)
- 장점: 가장 빠름, 실제 P&L 미계산
- 단점: 실제 매매 환경과 차이, 수수료/슬리피지 미반영

### Paper Trading (모의거래)
- 장점: 현실적인 P&L 계산, 슬리피지/부분체결 반영
- 단점: dry_run보다 느림 (계산 필요)

### 실거래 (실제 API)
- 장점: 실제 수익 가능
- 단점: 최고 위험, 버그 가능성 높음

## 테스트 실행

```bash
# 모든 paper_trader 테스트
python -m pytest tests/test_paper_trader.py -v

# 특정 테스트만
python -m pytest tests/test_paper_trader.py::test_slippage_recorded_in_trade -v

# 전체 테스트 (paper_trader 포함)
python -m pytest tests/ -v
```

## 향후 개선사항

1. **호가창 깊이 기반 슬리피지**: Order Book 깊이에 따라 동적으로 슬리피지 계산
2. **부분체결 재시도**: 타임아웃 후 미체결 수량 자동 재제출
3. **마켓 데이터 연동**: 현재가를 실제 시세 데이터에서 가져오기
4. **거래 비용 분석**: 누적 수수료 및 슬리피지 통계
5. **포지션 추적 통합**: PositionTracker와 PaperTrader 연동

## 참고사항

- 모의거래는 **시뮬레이션**이므로 실제 시장 환경과 완벽히 동일하지 않습니다.
- 슬리피지, 부분체결 등의 확률/범위는 `__init__` 매개변수로 조정 가능합니다.
- 모든 거래는 `self.account.trades` 리스트에 기록되므로 나중에 분석 가능합니다.
