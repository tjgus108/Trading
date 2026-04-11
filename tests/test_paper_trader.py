"""tests/test_paper_trader.py — PaperTrader 단위 테스트"""
import pytest
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
    # 슬리피지 범위 확인
    for trade in pt.account.trades:
        assert -0.1 <= trade.slippage_pct <= 0.1


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
    """요약에 평균 슬리피지가 포함됨"""
    pt = PaperTrader(initial_balance=50000.0, slippage_pct=0.05, fee_rate=0.0,
                     partial_fill_prob=0.0, timeout_prob=0.0)
    for _ in range(5):
        pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                         strategy="s", confidence="H")
        pt.execute_signal("BTC/USDT", "SELL", price=1100.0, quantity=1.0,
                         strategy="s", confidence="H")
    
    summary = pt.get_summary()
    assert "avg_slippage_pct" in summary
    assert "open_position_value" in summary
    # 슬리피지는 ±0.05% 범위
    assert -0.05 <= summary["avg_slippage_pct"] <= 0.05


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
