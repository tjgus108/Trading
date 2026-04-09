"""
StrategyPerformanceTracker 단위 테스트 (12개).
"""
import pytest
from src.analytics.strategy_tracker import StrategyMetrics, StrategyPerformanceTracker


# 1. 생성
def test_tracker_init():
    tracker = StrategyPerformanceTracker()
    assert tracker._metrics == {}


# 2. record_trade() 후 metrics 업데이트 확인
def test_record_trade_updates_metrics():
    tracker = StrategyPerformanceTracker()
    tracker.record_trade("rsi", pnl=100.0, is_win=True)
    m = tracker._metrics["rsi"]
    assert m.total_trades == 1
    assert m.total_pnl == 100.0
    assert m.winning_trades == 1


# 3. win_rate 계산 검증
def test_win_rate():
    tracker = StrategyPerformanceTracker()
    tracker.record_trade("macd", pnl=50.0, is_win=True)
    tracker.record_trade("macd", pnl=-20.0, is_win=False)
    tracker.record_trade("macd", pnl=30.0, is_win=True)
    assert tracker._metrics["macd"].win_rate == pytest.approx(2 / 3)


# 4. avg_pnl_per_trade 계산
def test_avg_pnl_per_trade():
    tracker = StrategyPerformanceTracker()
    tracker.record_trade("bb", pnl=60.0, is_win=True)
    tracker.record_trade("bb", pnl=-10.0, is_win=False)
    assert tracker._metrics["bb"].avg_pnl_per_trade == pytest.approx(25.0)


# 5. get_ranking() 반환 타입 확인
def test_get_ranking_returns_list_of_metrics():
    tracker = StrategyPerformanceTracker()
    tracker.record_trade("a", pnl=10.0, is_win=True)
    ranking = tracker.get_ranking()
    assert isinstance(ranking, list)
    assert all(isinstance(m, StrategyMetrics) for m in ranking)


# 6. get_top_n(3) 정상 작동
def test_get_top_n():
    tracker = StrategyPerformanceTracker()
    for name, pnl in [("a", 100), ("b", 200), ("c", 50), ("d", 300), ("e", 150)]:
        tracker.record_trade(name, pnl=pnl, is_win=True)
    top3 = tracker.get_top_n(3)
    assert len(top3) == 3
    assert top3[0].name == "d"
    assert top3[1].name == "b"
    assert top3[2].name == "e"


# 7. get_bottom_n(3) 정상 작동
def test_get_bottom_n():
    tracker = StrategyPerformanceTracker()
    for name, pnl in [("a", 100), ("b", 200), ("c", 50), ("d", 300), ("e", 150)]:
        tracker.record_trade(name, pnl=pnl, is_win=True)
    bottom3 = tracker.get_bottom_n(3)
    assert len(bottom3) == 3
    assert bottom3[-1].name == "c"


# 8. 여러 전략 기록 후 순위 정확성
def test_ranking_order_correctness():
    tracker = StrategyPerformanceTracker()
    tracker.record_trade("low", pnl=-50.0, is_win=False)
    tracker.record_trade("mid", pnl=0.0, is_win=False)
    tracker.record_trade("high", pnl=200.0, is_win=True)
    ranking = tracker.get_ranking(sort_by="total_pnl")
    assert [m.name for m in ranking] == ["high", "mid", "low"]


# 9. total_trades 0일 때 win_rate = 0
def test_win_rate_zero_trades():
    m = StrategyMetrics(name="empty")
    assert m.win_rate == 0.0
    assert m.avg_pnl_per_trade == 0.0


# 10. to_dict() / from_dict() 직렬화 검증
def test_serialization_roundtrip():
    tracker = StrategyPerformanceTracker()
    tracker.record_trade("rsi", pnl=100.0, is_win=True)
    tracker.record_trade("rsi", pnl=-30.0, is_win=False)
    tracker.record_trade("macd", pnl=50.0, is_win=True)

    d = tracker.to_dict()

    tracker2 = StrategyPerformanceTracker()
    tracker2.from_dict(d)

    assert tracker2._metrics["rsi"].total_trades == 2
    assert tracker2._metrics["rsi"].total_pnl == pytest.approx(70.0)
    assert tracker2._metrics["macd"].winning_trades == 1


# 11. sort_by='win_rate' 옵션 동작
def test_ranking_by_win_rate():
    tracker = StrategyPerformanceTracker()
    # strategy_a: 3 wins / 3 trades = 1.0
    for _ in range(3):
        tracker.record_trade("strategy_a", pnl=10.0, is_win=True)
    # strategy_b: 1 win / 3 trades = 0.333
    tracker.record_trade("strategy_b", pnl=10.0, is_win=True)
    tracker.record_trade("strategy_b", pnl=-5.0, is_win=False)
    tracker.record_trade("strategy_b", pnl=-5.0, is_win=False)
    ranking = tracker.get_ranking(sort_by="win_rate")
    assert ranking[0].name == "strategy_a"
    assert ranking[-1].name == "strategy_b"


# 12. sort_by='avg_pnl_per_trade' 옵션 동작
def test_ranking_by_avg_pnl():
    tracker = StrategyPerformanceTracker()
    tracker.record_trade("low_avg", pnl=10.0, is_win=True)
    tracker.record_trade("low_avg", pnl=10.0, is_win=True)   # avg=10
    tracker.record_trade("high_avg", pnl=100.0, is_win=True)  # avg=100
    ranking = tracker.get_ranking(sort_by="avg_pnl_per_trade")
    assert ranking[0].name == "high_avg"
    assert ranking[-1].name == "low_avg"
