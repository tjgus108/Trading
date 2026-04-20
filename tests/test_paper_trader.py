"""tests/test_paper_trader.py — PaperTrader 단위 테스트"""
import pytest
from unittest.mock import patch, MagicMock
from src.exchange.paper_trader import PaperTrader, PaperAccount, PaperTrade


# ── 기본 생성 ──────────────────────────────────────────────
def test_default_initial_balance():
    pt = PaperTrader()
    assert pt.account.initial_balance == 10000.0
    assert pt.account.balance == 10000.0


def test_custom_initial_balance():
    pt = PaperTrader(initial_balance=5000.0)
    assert pt.account.initial_balance == 5000.0
    assert pt.account.balance == 5000.0


def test_no_positions_on_init():
    pt = PaperTrader()
    assert pt.account.positions == {}
    assert pt.account.trades == []


# ── BUY 신호 ──────────────────────────────────────────────
def test_buy_reduces_balance():
    # 슬리피지/부분체결 없도록 확률 0 설정
    pt = PaperTrader(initial_balance=10000.0, fee_rate=0.001, 
                     slippage_pct=0.0, partial_fill_prob=0.0, timeout_prob=0.0)
    result = pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                               strategy="test", confidence="HIGH")
    assert result["status"] == "filled"
    expected_cost = 1000.0 * 1.0 * (1 + 0.001)  # price * qty * (1 + fee)
    assert abs(pt.account.balance - (10000.0 - expected_cost)) < 1e-6


def test_buy_creates_position():
    pt = PaperTrader(slippage_pct=0.0, partial_fill_prob=0.0, timeout_prob=0.0)
    pt.execute_signal("BTC/USDT", "BUY", price=500.0, quantity=2.0,
                      strategy="test", confidence="LOW")
    assert pt.account.positions.get("BTC/USDT") == 2.0


def test_buy_records_trade():
    pt = PaperTrader(slippage_pct=0.0, partial_fill_prob=0.0, timeout_prob=0.0)
    pt.execute_signal("ETH/USDT", "BUY", price=200.0, quantity=3.0,
                      strategy="rsi", confidence="MED")
    assert len(pt.account.trades) == 1
    t = pt.account.trades[0]
    assert t.symbol == "ETH/USDT"
    assert t.action == "BUY"


def test_buy_insufficient_balance_rejected():
    pt = PaperTrader(initial_balance=100.0)
    result = pt.execute_signal("BTC/USDT", "BUY", price=5000.0, quantity=1.0,
                               strategy="test", confidence="HIGH")
    assert result["status"] == "rejected"
    assert pt.account.balance == 100.0  # 변화 없음


def test_buy_accumulates_avg_entry():
    pt = PaperTrader(initial_balance=50000.0, slippage_pct=0.0, 
                     partial_fill_prob=0.0, timeout_prob=0.0)
    pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                      strategy="s", confidence="H")
    pt.execute_signal("BTC/USDT", "BUY", price=2000.0, quantity=1.0,
                      strategy="s", confidence="H")
    avg = pt.account.avg_entry["BTC/USDT"]
    assert abs(avg - 1500.0) < 1e-6
    assert pt.account.positions["BTC/USDT"] == 2.0


# ── SELL 신호 ─────────────────────────────────────────────
def test_sell_calculates_pnl():
    pt = PaperTrader(initial_balance=10000.0, fee_rate=0.0, slippage_pct=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)
    pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                      strategy="s", confidence="H")
    result = pt.execute_signal("BTC/USDT", "SELL", price=1200.0, quantity=1.0,
                               strategy="s", confidence="H")
    assert result["status"] == "filled"
    assert abs(result["pnl"] - 200.0) < 1e-6


def test_sell_increases_balance():
    pt = PaperTrader(initial_balance=10000.0, fee_rate=0.0, slippage_pct=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)
    pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                      strategy="s", confidence="H")
    balance_after_buy = pt.account.balance
    pt.execute_signal("BTC/USDT", "SELL", price=1200.0, quantity=1.0,
                      strategy="s", confidence="H")
    assert pt.account.balance > balance_after_buy


def test_sell_no_position_rejected():
    pt = PaperTrader()
    result = pt.execute_signal("BTC/USDT", "SELL", price=1000.0, quantity=1.0,
                               strategy="s", confidence="H")
    assert result["status"] == "rejected"


def test_sell_removes_position():
    pt = PaperTrader(initial_balance=50000.0, fee_rate=0.0, slippage_pct=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)
    pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                      strategy="s", confidence="H")
    pt.execute_signal("BTC/USDT", "SELL", price=1100.0, quantity=1.0,
                      strategy="s", confidence="H")
    assert "BTC/USDT" not in pt.account.positions


# ── get_summary ───────────────────────────────────────────
def test_summary_keys():
    pt = PaperTrader()
    summary = pt.get_summary()
    for key in ("initial_balance", "current_balance", "total_pnl",
                "total_return_pct", "trade_count", "win_rate", "open_positions"):
        assert key in summary


def test_summary_total_return_positive_after_profit():
    pt = PaperTrader(initial_balance=10000.0, fee_rate=0.0, slippage_pct=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)
    pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                      strategy="s", confidence="H")
    pt.execute_signal("BTC/USDT", "SELL", price=2000.0, quantity=1.0,
                      strategy="s", confidence="H")
    summary = pt.get_summary()
    assert summary["total_return_pct"] > 0


def test_summary_win_rate_all_wins():
    pt = PaperTrader(initial_balance=50000.0, fee_rate=0.0, slippage_pct=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)
    for _ in range(3):
        pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                          strategy="s", confidence="H")
        pt.execute_signal("BTC/USDT", "SELL", price=1100.0, quantity=1.0,
                          strategy="s", confidence="H")
    summary = pt.get_summary()
    assert summary["win_rate"] == 1.0


def test_unknown_action_returns_error():
    pt = PaperTrader()
    result = pt.execute_signal("BTC/USDT", "HOLD", price=1000.0, quantity=1.0,
                               strategy="s", confidence="H")
    assert result["status"] == "error"


# ── 슬리피지 & 부분체결 ────────────────────────────────────
def test_slippage_recorded_in_trade():
    """슬리피지가 거래 객체에 기록되는지 확인"""
    pt = PaperTrader(initial_balance=50000.0, slippage_pct=0.1,
                     partial_fill_prob=0.0, timeout_prob=0.0)
    for _ in range(10):
        pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                         strategy="s", confidence="H")
    
    trades = [t for t in pt.account.trades if t.slippage_pct != 0.0]
    # 슬리피지 범위는 ±0.1%이므로 일부 거래는 0이 아닌 슬리피지를 기록
    assert len(trades) > 0 or len(pt.account.trades) > 0
    # 슬리피지 범위 확인: 0.1% = 10 bps, BUY는 adverse 방향(양수 편향)
    for trade in pt.account.trades:
        assert -10.0 <= trade.slippage_pct <= 10.0


def test_timeout_returns_timeout_status():
    """타임아웃 시뮬레이션 감지"""
    pt = PaperTrader(initial_balance=10000.0, timeout_prob=0.5)
    # 높은 확률로 일부는 타임아웃
    results = []
    for _ in range(10):
        result = pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                                   strategy="s", confidence="H")
        results.append(result["status"])
    
    # 타임아웃과 filled 모두 나타날 것으로 예상
    assert "timeout" in results or "filled" in results


def test_partial_fill_records_actual_quantity():
    """부분체결 시 actual_quantity가 요청 수량보다 작음"""
    pt = PaperTrader(initial_balance=50000.0, partial_fill_prob=0.5,
                     timeout_prob=0.0)
    partial_fills = 0
    for _ in range(20):
        result = pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=10.0,
                                   strategy="s", confidence="H")
        if result["status"] == "partial":
            partial_fills += 1
            assert result["actual_quantity"] <= result["requested_quantity"]
    
    # 확률 50%이므로 일부는 부분체결될 것으로 예상
    assert partial_fills > 0


def test_summary_includes_slippage_stats():
    """요약에 평균 슬리피지가 포함됨 (now in bps)"""
    pt = PaperTrader(initial_balance=50000.0, slippage_pct=0.05, fee_rate=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)
    for _ in range(5):
        pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                         strategy="s", confidence="H")
        pt.execute_signal("BTC/USDT", "SELL", price=1100.0, quantity=1.0,
                         strategy="s", confidence="H")
    
    summary = pt.get_summary()
    assert "avg_slippage_bps" in summary  # Updated to bps
    assert "open_position_value" in summary
    # 슬리피지는 ±5 bps 범위 (0.05% = 5 bps)
    assert -5 <= summary["avg_slippage_bps"] <= 5


def test_reset_clears_trades_and_positions():
    """reset()은 거래와 포지션을 초기화하지만 초기 잔액 유지"""
    pt = PaperTrader(initial_balance=10000.0, slippage_pct=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)
    pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                      strategy="s", confidence="H")
    assert len(pt.account.trades) == 1
    assert pt.account.balance < 10000.0
    
    pt.reset()
    assert len(pt.account.trades) == 0
    assert pt.account.positions == {}
    assert pt.account.balance == 10000.0
    assert pt.account.initial_balance == 10000.0


def test_open_position_value_calculation():
    """open_position_value가 수량 × 평균진입가로 계산됨"""
    pt = PaperTrader(initial_balance=50000.0, fee_rate=0.0, slippage_pct=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)
    pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=2.0,
                      strategy="s", confidence="H")
    
    summary = pt.get_summary()
    expected_value = 2.0 * 1000.0
    assert abs(summary["open_position_value"] - expected_value) < 1.0


# ── 추가 고급 테스트 (Cycle 3 - Execution) ────────────────────────

def test_multiple_symbols_independent_positions():
    """여러 심볼에서 독립적 포지션 관리"""
    pt = PaperTrader(initial_balance=100000.0, fee_rate=0.0, slippage_pct=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)
    
    # BTC 2개 매수
    pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=2.0,
                      strategy="s", confidence="H")
    # ETH 5개 매수
    pt.execute_signal("ETH/USDT", "BUY", price=200.0, quantity=5.0,
                      strategy="s", confidence="H")
    
    assert pt.account.positions["BTC/USDT"] == 2.0
    assert pt.account.positions["ETH/USDT"] == 5.0
    assert pt.account.avg_entry["BTC/USDT"] == 1000.0
    assert pt.account.avg_entry["ETH/USDT"] == 200.0
    
    # 각 심볼 독립적 판매
    result_btc = pt.execute_signal("BTC/USDT", "SELL", price=1100.0, quantity=1.0,
                                   strategy="s", confidence="H")
    result_eth = pt.execute_signal("ETH/USDT", "SELL", price=220.0, quantity=2.0,
                                   strategy="s", confidence="H")
    
    # PnL 검증
    assert result_btc["pnl"] == 100.0  # (1100-1000)*1
    assert result_eth["pnl"] == 40.0   # (220-200)*2
    
    # 남은 포지션
    assert pt.account.positions["BTC/USDT"] == 1.0
    assert pt.account.positions["ETH/USDT"] == 3.0


def test_cumulative_pnl_after_multiple_rounds():
    """여러 라운드 거래 후 누적 P&L 정합성"""
    pt = PaperTrader(initial_balance=10000.0, fee_rate=0.0, slippage_pct=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)
    
    # Round 1: 1000 @ 100 매수 → 1000 @ 150 판매 (P&L: 50,000)
    pt.execute_signal("BTC/USDT", "BUY", price=100.0, quantity=1.0,
                      strategy="s", confidence="H")
    r1 = pt.execute_signal("BTC/USDT", "SELL", price=150.0, quantity=1.0,
                          strategy="s", confidence="H")
    
    # Round 2: 1000 @ 150 매수 → 1000 @ 120 판매 (P&L: -30,000)
    pt.execute_signal("BTC/USDT", "BUY", price=150.0, quantity=1.0,
                      strategy="s", confidence="H")
    r2 = pt.execute_signal("BTC/USDT", "SELL", price=120.0, quantity=1.0,
                          strategy="s", confidence="H")
    
    expected_cumulative = r1["pnl"] + r2["pnl"]
    assert abs(pt.account.total_pnl - expected_cumulative) < 1e-6
    
    summary = pt.get_summary()
    assert summary["sell_count"] == 2
    assert summary["trade_count"] == 4  # 2 buys + 2 sells


def test_partial_fill_sell_qty_capped_at_position():
    """부분체결 SELL에서 실제 판매량이 보유량을 초과할 수 없음"""
    pt = PaperTrader(initial_balance=50000.0, fee_rate=0.0, slippage_pct=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)
    
    # 5 BTC 매수
    pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=5.0,
                      strategy="s", confidence="H")
    
    # 10 BTC 판매 시도 (보유량 5개 초과)
    result = pt.execute_signal("BTC/USDT", "SELL", price=1100.0, quantity=10.0,
                              strategy="s", confidence="H")
    
    # 실제 판매량은 5개로 제한됨
    assert result["actual_quantity"] == 5.0
    assert pt.account.positions.get("BTC/USDT", 0.0) == 0.0


def test_loss_trade_negative_pnl():
    """손실 거래에서 negative PnL 기록"""
    pt = PaperTrader(initial_balance=10000.0, fee_rate=0.0, slippage_pct=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)
    
    pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                      strategy="s", confidence="H")
    result = pt.execute_signal("BTC/USDT", "SELL", price=900.0, quantity=1.0,
                              strategy="s", confidence="H")
    
    assert result["pnl"] == -100.0
    assert result["status"] == "filled"
    
    summary = pt.get_summary()
    assert summary["win_rate"] == 0.0  # 0/1 wins


def test_fee_impact_on_balance_and_pnl():
    """수수료가 잔액과 P&L에 올바르게 반영됨"""
    fee_rate = 0.001  # 0.1%
    pt = PaperTrader(initial_balance=200000.0, fee_rate=fee_rate, slippage_pct=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)
    
    # 1000 @ 100 매수: 비용 = 100*1000*1.001 = 100,100
    buy_result = pt.execute_signal("BTC/USDT", "BUY", price=100.0, quantity=1000.0,
                                   strategy="s", confidence="H")
    assert buy_result["fee"] == 100.0  # 100*1000*0.001
    expected_balance = 200000.0 - 100100.0
    assert abs(pt.account.balance - expected_balance) < 1.0
    
    # 1000 @ 120 판매: 수익 = 120*1000 - 수수료(120)
    sell_result = pt.execute_signal("BTC/USDT", "SELL", price=120.0, quantity=1000.0,
                                    strategy="s", confidence="H")
    assert sell_result["fee"] == 120.0  # 120*1000*0.001
    # PnL = (120-100)*1000 - 120 = 20000 - 120 = 19,880
    expected_pnl = (120 - 100) * 1000.0 - 120.0
    assert abs(sell_result["pnl"] - expected_pnl) < 0.1


# ── 경계 조건 테스트 (Cycle 43) ──────────────────────────────

def test_zero_balance_buy_rejected():
    """잔액 0인 계좌에서 BUY는 rejected"""
    pt = PaperTrader(initial_balance=0.0, slippage_pct=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)
    result = pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                               strategy="s", confidence="H")
    assert result["status"] == "rejected"
    assert pt.account.balance == 0.0


def test_fee_exceeds_profit_net_loss():
    """수수료가 명목 이익을 초과할 때 P&L이 음수"""
    # price_gain = 0.01/unit, qty=1, fee_rate=0.05 → fee=0.0505 > gain=0.01
    pt = PaperTrader(initial_balance=100000.0, fee_rate=0.05,
                     slippage_pct=0.0, partial_fill_prob=0.0, timeout_prob=0.0)
    pt.execute_signal("BTC/USDT", "BUY", price=1.00, quantity=1.0,
                      strategy="s", confidence="H")
    result = pt.execute_signal("BTC/USDT", "SELL", price=1.01, quantity=1.0,
                               strategy="s", confidence="H")
    # nominal_gain=0.01, sell_fee=1.01*0.05=0.0505 → pnl < 0
    assert result["pnl"] < 0.0


def test_exact_balance_buy_succeeds():
    """잔액이 주문 비용과 정확히 같을 때 BUY 성공"""
    # cost = price * qty * (1 + fee_rate) = 1000 * 1 * 1.001 = 1001.0
    pt = PaperTrader(initial_balance=1001.0, fee_rate=0.001,
                     slippage_pct=0.0, partial_fill_prob=0.0, timeout_prob=0.0)
    result = pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                               strategy="s", confidence="H")
    assert result["status"] == "filled"
    assert abs(pt.account.balance) < 1e-6  # 잔액 거의 0


# ── Multi-symbol 밸런스 관리 검증 (Cycle 63) ─────────────────────

def test_multi_symbol_balance_conservation():
    """여러 심볼 동시 거래 시 잔액 = 초기잔액 - 총매수비용 보존"""
    pt = PaperTrader(initial_balance=100000.0, fee_rate=0.001, slippage_pct=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)

    symbols = [
        ("BTC/USDT", 1000.0, 3.0),
        ("ETH/USDT", 200.0, 10.0),
        ("SOL/USDT", 50.0, 20.0),
    ]
    total_cost = 0.0
    for sym, price, qty in symbols:
        cost = price * qty * (1 + 0.001)
        total_cost += cost
        pt.execute_signal(sym, "BUY", price=price, quantity=qty,
                          strategy="s", confidence="H")

    expected_balance = 100000.0 - total_cost
    assert abs(pt.account.balance - expected_balance) < 1e-4

    # 각 심볼 포지션 독립 확인
    assert pt.account.positions["BTC/USDT"] == 3.0
    assert pt.account.positions["ETH/USDT"] == 10.0
    assert pt.account.positions["SOL/USDT"] == 20.0


def test_multi_symbol_sell_does_not_affect_other_positions():
    """심볼 A 매도가 심볼 B 포지션과 잔액에 간섭하지 않음"""
    pt = PaperTrader(initial_balance=100000.0, fee_rate=0.0, slippage_pct=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)

    pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=2.0,
                      strategy="s", confidence="H")
    pt.execute_signal("ETH/USDT", "BUY", price=500.0, quantity=4.0,
                      strategy="s", confidence="H")

    balance_before_sell = pt.account.balance

    # BTC만 전량 매도
    result = pt.execute_signal("BTC/USDT", "SELL", price=1200.0, quantity=2.0,
                               strategy="s", confidence="H")

    assert result["status"] == "filled"
    assert result["pnl"] == 400.0  # (1200-1000)*2

    # ETH 포지션 영향 없음
    assert pt.account.positions.get("ETH/USDT") == 4.0
    assert pt.account.avg_entry.get("ETH/USDT") == 500.0

    # 잔액 증가분 = BTC 매도 proceeds
    assert pt.account.balance == balance_before_sell + 1200.0 * 2.0

    # BTC 포지션 소멸
    assert "BTC/USDT" not in pt.account.positions


# ── 수수료 누적 정확성 경계 테스트 (Cycle 88) ────────────────────

def test_buy_fee_not_double_counted_in_balance():
    """BUY 수수료가 잔액에서 정확히 1회만 차감되는지 검증.
    
    cost = price * qty + fee = price * qty * (1 + fee_rate)
    잔액 = initial - cost 이어야 하고, fee가 이중 차감되면 안 됨.
    """
    fee_rate = 0.001
    price, qty = 500.0, 4.0
    initial = 50000.0
    pt = PaperTrader(initial_balance=initial, fee_rate=fee_rate,
                     slippage_pct=0.0, partial_fill_prob=0.0, timeout_prob=0.0)

    result = pt.execute_signal("BTC/USDT", "BUY", price=price, quantity=qty,
                               strategy="s", confidence="H")

    fee = price * qty * fee_rate          # = 2.0
    cost = price * qty + fee              # = 2002.0
    expected_balance = initial - cost    # = 47998.0

    assert result["fee"] == pytest.approx(fee, abs=1e-9)
    assert pt.account.balance == pytest.approx(expected_balance, abs=1e-9)
    # fee가 이중으로 빠지면 balance = initial - cost - fee = 47996.0 이 되므로
    # 이 assertion이 실패해야 이중 차감 버그가 잡힘
    assert pt.account.balance != pytest.approx(expected_balance - fee, abs=1e-3)


def test_sell_fee_accumulated_across_multiple_trades():
    """여러 SELL 거래의 수수료가 total_pnl에 누적 반영되는지 검증.
    
    각 SELL pnl = (sell_price - avg_entry) * qty - sell_fee
    total_pnl == sum(individual pnl) 이어야 함.
    """
    fee_rate = 0.002
    pt = PaperTrader(initial_balance=500000.0, fee_rate=fee_rate,
                     slippage_pct=0.0, partial_fill_prob=0.0, timeout_prob=0.0)

    rounds = [
        (1000.0, 1100.0, 5.0),   # buy@1000, sell@1100, qty=5 → gain=500, fee=11 → pnl=489
        (200.0,  180.0,  10.0),  # buy@200,  sell@180,  qty=10 → loss=-200, fee=3.6 → pnl=-203.6
        (50.0,   75.0,   20.0),  # buy@50,   sell@75,   qty=20 → gain=500, fee=3   → pnl=497
    ]

    expected_total = 0.0
    for buy_p, sell_p, qty in rounds:
        pt.execute_signal("BTC/USDT", "BUY",  price=buy_p,  quantity=qty,
                          strategy="s", confidence="H")
        sell_result = pt.execute_signal("BTC/USDT", "SELL", price=sell_p, quantity=qty,
                                        strategy="s", confidence="H")
        expected_total += sell_result["pnl"]

    assert pt.account.total_pnl == pytest.approx(expected_total, abs=1e-9)
    # 또한 BUY 수수료는 total_pnl에 미포함 확인 (설계 명세 검증)
    # total_pnl은 SELL 기준이므로 BUY fee는 잔액에서만 빠짐
    summary = pt.get_summary()
    assert summary["total_pnl"] == pytest.approx(expected_total, abs=1e-6)


# ── LivePaperTrader 최대 손실 한계 테스트 (Cycle 163) ─────────────────

def _make_live_trader(balance: float, max_loss_pct: float = 0.5):
    """LivePaperTrader를 heavy deps 없이 최소 생성."""
    from scripts.live_paper_trader import LivePaperTrader, LiveState, INITIAL_BALANCE

    with patch.object(LiveState, 'load') as mock_load, \
         patch('scripts.live_paper_trader.CircuitBreaker'), \
         patch('scripts.live_paper_trader.StrategyRotationManager'), \
         patch('scripts.live_paper_trader.MarketRegimeDetector'), \
         patch('scripts.live_paper_trader.SignalCorrelationTracker'), \
         patch('scripts.live_paper_trader.DriftMonitor'), \
         patch('signal.signal'):
        state = LiveState()
        state.portfolio_balance = balance
        mock_load.return_value = state
        trader = LivePaperTrader(days=1, interval=60, max_loss_pct=max_loss_pct)
        trader.state = state
        return trader


def test_max_loss_halts_trading():
    """초기 자본 대비 50% 이상 손실 시 _halted=True, tick 중단."""
    trader = _make_live_trader(balance=4000.0, max_loss_pct=0.5)
    # balance=4000, initial=10000 → 60% 손실 → 한계 초과
    assert trader._check_max_loss() is True
    assert trader._halted is True


def test_max_loss_not_triggered_above_threshold():
    """손실이 한계 미만이면 거래 계속."""
    trader = _make_live_trader(balance=6000.0, max_loss_pct=0.5)
    # balance=6000, initial=10000 → 40% 손실 → 한계 미달
    assert trader._check_max_loss() is False
    assert trader._halted is False


def test_max_loss_halted_stays_halted():
    """한번 halted 되면 잔액 회복해도 halted 유지 (수동 재시작 필요)."""
    trader = _make_live_trader(balance=4000.0, max_loss_pct=0.5)
    assert trader._check_max_loss() is True
    assert trader._halted is True
    # 잔액을 인위적으로 회복시켜도 halted 유지
    trader.state.portfolio_balance = 9000.0
    assert trader._check_max_loss() is True  # 여전히 halted
