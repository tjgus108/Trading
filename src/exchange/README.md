# src/exchange — 실행 레이어

거래소 연결, 주문 실행, 모의거래를 담당하는 모듈.

---

## 파일 구조

| 파일 | 클래스 | 역할 |
|------|--------|------|
| `connector.py` | `ExchangeConnector` | ccxt 기반 실거래소 연결 |
| `paper_trader.py` | `PaperTrader`, `PaperTrade`, `PaperAccount` | 모의거래 엔진 |
| `paper_connector.py` | `PaperConnector` | PaperTrader를 ExchangeConnector 인터페이스로 래핑 |
| `mock_connector.py` | `MockExchangeConnector` | API 키 없이 가짜 데이터로 파이프라인 테스트 |
| `twap.py` | `TWAPExecutor`, `TWAPResult` | TWAP 분할 주문 실행 알고리즘 |

---

## 클래스 요약

### ExchangeConnector (`connector.py`)
ccxt 기반 실제 거래소 연결 레이어. 모든 거래소 접근은 이 클래스를 경유한다.

- `connect()` — API 키 로드, 샌드박스 설정, 마켓 로드 후 `check_api_permissions()` 자동 실행
- `check_api_permissions()` — 출금 권한 감지 시 CRITICAL 로그 경고
- `create_order(symbol, side, amount, order_type, price)` — market / limit 주문
- `wait_for_fill(order_id, symbol, timeout=60)` — 체결 대기; 타임아웃 시 자동 취소

### PaperTrader (`paper_trader.py`)
실제 API 없이 신호를 기록하고 가상 P&L을 추적하는 모의거래 엔진.

- 슬리피지: `±slippage_pct` 범위 내 랜덤 변동 (기본 ±0.05%)
- 부분체결: `partial_fill_prob` 확률로 50~80% 체결 (기본 5%)
- 타임아웃: `timeout_prob` 확률로 주문 취소 (기본 1%)
- `execute_signal()` — BUY/SELL 실행, 반환: `filled | partial | timeout | rejected | error`
- `get_summary()` — `total_return%`, `win_rate`, `avg_slippage_pct` 등 성과 요약

### PaperConnector (`paper_connector.py`)
PaperTrader를 ExchangeConnector와 동일한 인터페이스로 제공하는 어댑터.

- `create_order()` → 내부적으로 `PaperTrader.execute_signal()` 호출
- `wait_for_fill()` → 즉시 반환 (no-op)
- `get_paper_summary()` → 모의거래 성과 조회
- timeout/rejected → CCXT 호환 포맷(`canceled`)으로 변환

### MockExchangeConnector (`mock_connector.py`)
API 키 없이 `--demo` 모드에서 전체 파이프라인을 실행할 때 사용.

- `fetch_ohlcv()` — 약한 상승 트렌드 + 랜덤 노이즈로 캔들 생성
- `create_order()` — 가짜 체결, 내부 잔액 업데이트
- ExchangeConnector와 동일한 인터페이스 (connect/fetch_balance/fetch_order/cancel_order 등)

### TWAPExecutor (`twap.py`)
대형 주문을 `n_slices`개로 균등 분할해 `interval_seconds` 간격으로 체결. 슬리피지 최소화 목적.

- `execute(connector, symbol, side, total_qty, price_limit)` → `TWAPResult`
- `dry_run=True` 시 실제 주문 없이 시뮬레이션 (±0.05% 슬리피지, 20% 부분체결 확률)
- `estimate_slippage()` — Almgren-Chriss 간소화: `0.1 × (qty/daily_volume)^0.5`
- `TWAPResult` 필드: `slices_executed`, `avg_price`, `filled_qty`, `partial_fills`, `timeout_occurred`

---

## 사용 패턴

```python
# 실거래
conn = ExchangeConnector("binance", sandbox=True)
conn.connect()
order = conn.create_order("BTC/USDT", "buy", 0.001)

# 모의거래
paper = PaperConnector("BTC/USDT", initial_balance=10000.0)
paper.connect()
order = paper.create_order("BTC/USDT", "buy", 0.001, price=65000.0)

# TWAP
executor = TWAPExecutor(n_slices=5, interval_seconds=60, dry_run=False)
result = executor.execute(conn, "BTC/USDT", "buy", total_qty=0.05)
```
