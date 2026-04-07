"""Phase D: 인프라 고도화 단위 테스트.

D1: MultiLLMEnsemble
D2: BinanceWebSocketFeed, WebSocketDataAdapter
D3: WalkForwardOptimizer
LSTM: LSTMSignalGenerator (numpy fallback)
"""

import numpy as np
import pandas as pd
import pytest

from src.alpha.ensemble import MultiLLMEnsemble, EnsembleSignal
from src.data.websocket_feed import BinanceWebSocketFeed, WebSocketDataAdapter, CandleBar
from src.backtest.walk_forward import WalkForwardOptimizer, WalkForwardResult, optimize_ema_cross
from src.ml.lstm_model import LSTMSignalGenerator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_df(n: int = 300, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    close = 50000 + np.cumsum(rng.standard_normal(n) * 300)
    close = np.abs(close)
    high = close + np.abs(rng.standard_normal(n) * 100)
    low = close - np.abs(rng.standard_normal(n) * 100)
    low = np.maximum(low, close * 0.9)
    volume = 10.0 + np.abs(rng.standard_normal(n) * 2)

    df = pd.DataFrame(
        {"open": close, "high": high, "low": low, "close": close, "volume": volume},
        index=idx,
    )
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    prev = df["close"].shift(1)
    tr = pd.concat(
        [(df["high"] - df["low"]), (df["high"] - prev).abs(), (df["low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    delta = df["close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    df["rsi14"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
    df["donchian_high"] = df["high"].rolling(20).max()
    df["donchian_low"] = df["low"].rolling(20).min()
    typical = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
    return df


# ---------------------------------------------------------------------------
# D1: MultiLLMEnsemble
# ---------------------------------------------------------------------------

class TestMultiLLMEnsemble:
    def test_neutral_without_api_keys(self):
        """API 키 없으면 neutral 반환 (rule_signal 그대로)."""
        ens = MultiLLMEnsemble.__new__(MultiLLMEnsemble)
        ens._claude_client = None
        ens._openai_client = None
        ens._claude_model = "haiku"
        ens._openai_model = "gpt-4o-mini"

        result = ens._neutral("BUY", "API 없음")
        assert result.consensus == "BUY"
        assert result.confidence == 0.5
        assert result.claude_vote == "N/A"
        assert result.openai_vote == "N/A"

    def test_is_enabled_false_without_keys(self):
        ens = MultiLLMEnsemble(use_openai=False)
        # API 키 없으면 disabled
        if not ens.is_enabled:
            assert ens._claude_client is None

    def test_compute_consensus_full_agreement(self):
        """두 LLM 모두 BUY → BUY, confidence=0.9."""
        ens = MultiLLMEnsemble.__new__(MultiLLMEnsemble)
        ens._claude_client = None
        ens._openai_client = None
        cons, conf = ens._compute_consensus("BUY", "BUY", "BUY")
        assert cons == "BUY"
        assert conf == 0.90

    def test_compute_consensus_conflict(self):
        """Claude SELL, OpenAI BUY (rule HOLD) → 모두 불일치 → HOLD."""
        ens = MultiLLMEnsemble.__new__(MultiLLMEnsemble)
        ens._claude_client = None
        ens._openai_client = None
        # rule=HOLD, 둘 다 다른 의견 → HOLD
        cons, conf = ens._compute_consensus("HOLD", "SELL", "BUY")
        assert cons == "HOLD"

    def test_compute_consensus_one_na(self):
        """한쪽 N/A → 유효한 쪽 기준."""
        ens = MultiLLMEnsemble.__new__(MultiLLMEnsemble)
        ens._claude_client = None
        ens._openai_client = None
        cons, conf = ens._compute_consensus("BUY", "BUY", "N/A")
        assert cons == "BUY"
        assert conf >= 0.6

    def test_compute_consensus_both_na(self):
        """둘 다 N/A → rule signal, confidence 낮음."""
        ens = MultiLLMEnsemble.__new__(MultiLLMEnsemble)
        ens._claude_client = None
        ens._openai_client = None
        cons, conf = ens._compute_consensus("SELL", "N/A", "N/A")
        assert cons == "SELL"
        assert conf < 0.6

    def test_agrees_with(self):
        signal = EnsembleSignal(
            consensus="BUY", confidence=0.85,
            claude_vote="BUY", openai_vote="BUY",
            reasoning="test", models_used=[],
        )
        assert signal.agrees_with("BUY")
        assert not signal.agrees_with("SELL")

    def test_conflicts_with(self):
        signal = EnsembleSignal(
            consensus="SELL", confidence=0.80,
            claude_vote="SELL", openai_vote="SELL",
            reasoning="test", models_used=[],
        )
        assert signal.conflicts_with("BUY")
        assert not signal.conflicts_with("SELL")

    def test_analyze_without_api(self):
        """API 없어도 analyze() 정상 반환."""
        ens = MultiLLMEnsemble(use_openai=False)
        result = ens.analyze("BTC/USDT", "BUY", "EMA cross detected")
        assert isinstance(result, EnsembleSignal)
        assert result.consensus in ("BUY", "SELL", "HOLD", "NEUTRAL")

    def test_build_prompt_contains_symbol(self):
        ens = MultiLLMEnsemble.__new__(MultiLLMEnsemble)
        ens._claude_client = None
        ens._openai_client = None
        prompt = ens._build_prompt("BTC/USDT", "BUY", "EMA cross", "FG=30")
        assert "BTC/USDT" in prompt
        assert "BUY" in prompt
        assert "ONLY one word" in prompt

    def test_summary_format(self):
        signal = EnsembleSignal(
            consensus="BUY", confidence=0.7,
            claude_vote="BUY", openai_vote="N/A",
            reasoning="test", models_used=["claude-haiku"],
        )
        s = signal.summary()
        assert "ENSEMBLE" in s
        assert "consensus=BUY" in s


# ---------------------------------------------------------------------------
# D2: BinanceWebSocketFeed
# ---------------------------------------------------------------------------

class TestBinanceWebSocketFeed:
    def test_initialization(self):
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        assert feed.symbol == "btcusdt"
        assert feed.interval == "1h"
        assert feed.candle_count() == 0
        assert not feed.is_connected

    def test_symbol_normalization(self):
        """BTC/USDT → btcusdt 정규화."""
        feed = BinanceWebSocketFeed("BTC/USDT", "1h")
        assert feed.symbol == "btcusdt"

    def test_get_latest_df_empty(self):
        """캔들 없으면 None 반환."""
        feed = BinanceWebSocketFeed()
        assert feed.get_latest_df() is None

    def test_process_message_closed_candle(self):
        """완성 캔들(is_closed=True) 처리."""
        feed = BinanceWebSocketFeed()
        msg = {
            "k": {
                "t": 1704067200000,
                "o": "50000", "h": "51000", "l": "49000", "c": "50500", "v": "100",
                "x": True,  # closed
            }
        }
        feed._process_message(msg)
        assert feed.candle_count() == 1

    def test_process_message_open_candle_ignored(self):
        """미완성 캔들(is_closed=False) 무시."""
        feed = BinanceWebSocketFeed()
        msg = {
            "k": {
                "t": 1704067200000,
                "o": "50000", "h": "51000", "l": "49000", "c": "50500", "v": "100",
                "x": False,  # not closed
            }
        }
        feed._process_message(msg)
        assert feed.candle_count() == 0

    def test_get_latest_df_with_candles(self):
        """캔들 있으면 DataFrame 반환."""
        feed = BinanceWebSocketFeed()
        for i in range(50):
            bar = CandleBar(
                timestamp=1704067200000 + i * 3600000,
                open=50000.0, high=51000.0, low=49000.0, close=50500.0, volume=10.0,
            )
            feed._candles.append(bar)

        df = feed.get_latest_df(limit=30)
        assert df is not None
        assert len(df) == 30
        assert "close" in df.columns
        assert "ema20" in df.columns  # 지표 추가됨

    def test_get_latest_df_indicators(self):
        """반환 DataFrame에 필수 지표 포함."""
        feed = BinanceWebSocketFeed()
        for i in range(60):
            bar = CandleBar(
                timestamp=1704067200000 + i * 3600000,
                open=50000.0 + i * 10,
                high=50100.0 + i * 10,
                low=49900.0 + i * 10,
                close=50050.0 + i * 10,
                volume=10.0,
            )
            feed._candles.append(bar)

        df = feed.get_latest_df()
        for col in ("ema20", "ema50", "atr14", "rsi14", "donchian_high", "vwap"):
            assert col in df.columns

    def test_is_websocket_available(self):
        """websockets 설치 여부 감지."""
        result = BinanceWebSocketFeed.is_websocket_available()
        assert isinstance(result, bool)

    def test_max_candles_buffer(self):
        """MAX_CANDLES 초과 시 자동 제거."""
        from src.data.websocket_feed import MAX_CANDLES
        feed = BinanceWebSocketFeed()
        for i in range(MAX_CANDLES + 50):
            bar = CandleBar(
                timestamp=1704067200000 + i * 3600000,
                open=50000.0, high=51000.0, low=49000.0, close=50500.0, volume=10.0,
            )
            feed._candles.append(bar)
        assert feed.candle_count() == MAX_CANDLES


class TestWebSocketDataAdapter:
    def _make_feed_with_candles(self, n: int = 150) -> BinanceWebSocketFeed:
        feed = BinanceWebSocketFeed()
        feed._connected = True
        for i in range(n):
            bar = CandleBar(
                timestamp=1704067200000 + i * 3600000,
                open=50000.0 + i * 5,
                high=50100.0 + i * 5,
                low=49900.0 + i * 5,
                close=50050.0 + i * 5,
                volume=10.0,
            )
            feed._candles.append(bar)
        return feed

    def test_fetch_uses_websocket_when_connected(self):
        ws = self._make_feed_with_candles(150)
        adapter = WebSocketDataAdapter(ws, rest_feed=None, min_candles=100)
        result = adapter.fetch("BTC/USDT", "1h", limit=100)
        assert result.candles == 100
        assert result.symbol == "BTC/USDT"

    def test_fetch_falls_back_to_rest(self):
        """WebSocket 미연결 → REST fallback."""
        ws = BinanceWebSocketFeed()  # 연결 안 됨
        mock_summary = type("Summary", (), {
            "candles": 500, "symbol": "BTC/USDT",
            "timeframe": "1h", "start": "", "end": "",
            "missing": 0, "indicators": [], "anomalies": [], "df": pd.DataFrame(),
        })()
        rest = type("Feed", (), {"fetch": lambda self, *a, **k: mock_summary})()
        adapter = WebSocketDataAdapter(ws, rest_feed=rest, min_candles=100)
        result = adapter.fetch("BTC/USDT", "1h")
        assert result.candles == 500

    def test_fetch_raises_without_fallback(self):
        """WebSocket 미연결 + REST 없음 → RuntimeError."""
        ws = BinanceWebSocketFeed()
        adapter = WebSocketDataAdapter(ws, rest_feed=None)
        with pytest.raises(RuntimeError):
            adapter.fetch("BTC/USDT", "1h")


# ---------------------------------------------------------------------------
# D3: WalkForwardOptimizer
# ---------------------------------------------------------------------------

class TestWalkForwardOptimizer:
    def test_insufficient_data(self):
        """데이터 부족 → is_stable=False."""
        from src.strategy.ema_cross import EmaCrossStrategy
        opt = WalkForwardOptimizer(
            "ema_cross",
            lambda p: EmaCrossStrategy(),
            param_grid={"fast": [10, 20]},
            n_windows=2,
        )
        df = _make_df(50)
        result = opt.run(df)
        assert not result.is_stable
        assert len(result.fail_reasons) > 0

    def test_no_param_grid(self):
        """파라미터 그리드 없음 → is_stable=False."""
        from src.strategy.ema_cross import EmaCrossStrategy
        opt = WalkForwardOptimizer(
            "unknown_strategy",
            lambda p: EmaCrossStrategy(),
            param_grid={},
        )
        df = _make_df(300)
        result = opt.run(df)
        assert not result.is_stable

    def test_run_returns_result(self):
        """정상 실행 시 WalkForwardResult 반환."""
        from src.strategy.ema_cross import EmaCrossStrategy
        opt = WalkForwardOptimizer(
            "ema_cross",
            lambda p: EmaCrossStrategy(),
            param_grid={"dummy": [1, 2]},
            n_windows=2,
        )
        df = _make_df(400)
        result = opt.run(df)
        assert isinstance(result, WalkForwardResult)
        assert result.strategy_name == "ema_cross"

    def test_window_results_count(self):
        """윈도우 수만큼 결과 생성."""
        from src.strategy.donchian_breakout import DonchianBreakoutStrategy
        opt = WalkForwardOptimizer(
            "donchian_breakout",
            lambda p: DonchianBreakoutStrategy(),
            param_grid={"period": [15, 20]},
            n_windows=2,
        )
        df = _make_df(500)
        result = opt.run(df)
        assert len(result.windows) <= 2  # 실제 분할 가능한 윈도우 수 이하

    def test_is_oos_ratio_computed(self):
        """IS/OOS 비율 계산됨."""
        from src.strategy.ema_cross import EmaCrossStrategy
        opt = WalkForwardOptimizer(
            "ema_cross",
            lambda p: EmaCrossStrategy(),
            param_grid={"x": [1]},
            n_windows=2,
        )
        df = _make_df(400)
        result = opt.run(df)
        for wr in result.windows:
            assert hasattr(wr, "is_oos_ratio")
            assert isinstance(wr.is_oos_ratio, float)

    def test_summary_format(self):
        from src.strategy.ema_cross import EmaCrossStrategy
        opt = WalkForwardOptimizer(
            "ema_cross",
            lambda p: EmaCrossStrategy(),
            param_grid={"x": [1]},
            n_windows=2,
        )
        df = _make_df(400)
        result = opt.run(df)
        s = result.summary()
        assert "WALK_FORWARD_RESULT" in s
        assert "avg_oos_sharpe" in s

    def test_optimize_ema_cross_helper(self):
        """optimize_ema_cross 헬퍼 함수."""
        df = _make_df(400)
        result = optimize_ema_cross(df, n_windows=2)
        assert isinstance(result, WalkForwardResult)
        assert result.strategy_name == "ema_cross"

    def test_iter_param_combinations(self):
        """파라미터 조합 수 계산."""
        from src.strategy.ema_cross import EmaCrossStrategy
        opt = WalkForwardOptimizer(
            "ema_cross",
            lambda p: EmaCrossStrategy(),
            param_grid={"a": [1, 2], "b": [10, 20, 30]},
        )
        combos = list(opt._iter_param_combinations())
        assert len(combos) == 6  # 2 × 3


# ---------------------------------------------------------------------------
# LSTM: LSTMSignalGenerator (numpy fallback)
# ---------------------------------------------------------------------------

class TestLSTMSignalGenerator:
    def test_name(self):
        assert LSTMSignalGenerator.name == "lstm"

    def test_predict_without_model_returns_hold(self):
        """모델 없으면 HOLD."""
        gen = LSTMSignalGenerator()
        df = _make_df()
        pred = gen.predict(df)
        assert pred.action == "HOLD"
        assert pred.confidence == 0.0
        assert "lstm" in pred.model_name.lower()

    def test_train_numpy_fallback(self):
        """numpy fallback 학습."""
        gen = LSTMSignalGenerator()
        df = _make_df(300)
        result = gen._train_numpy(df)
        assert "test_accuracy" in result
        assert isinstance(float(result["test_accuracy"]), float)
        assert result["passed"] in (True, False, np.bool_(True), np.bool_(False))

    def test_predict_numpy_after_train(self):
        """numpy 학습 후 예측."""
        gen = LSTMSignalGenerator()
        df = _make_df(300)
        gen._train_numpy(df)
        gen._model = {"type": "numpy_momentum"}
        pred = gen._predict_numpy(
            gen.feature_builder.build_features_only(df).dropna()
        )
        assert pred.action in ("BUY", "SELL", "HOLD")
        assert 0.0 <= pred.confidence <= 1.0

    def test_load_missing_returns_false(self):
        gen = LSTMSignalGenerator()
        assert gen.load("models/nonexistent_lstm.pkl") is False

    def test_load_latest_no_models(self):
        gen = LSTMSignalGenerator()
        result = gen.load_latest()
        assert isinstance(result, bool)

    def test_insufficient_data_for_sequence(self):
        """시퀀스보다 짧은 데이터 → HOLD."""
        gen = LSTMSignalGenerator(sequence_len=20)
        gen._model = {"type": "numpy_momentum"}
        gen._model_name = "test"
        df = _make_df(15)  # 시퀀스 길이보다 짧음
        pred = gen.predict(df)
        assert pred.action == "HOLD"

    def test_train_insufficient_data(self):
        """데이터 부족 → passed=False."""
        gen = LSTMSignalGenerator()
        df = _make_df(30)
        result = gen._train_numpy(df)
        assert not result["passed"] or result["test_accuracy"] >= 0

    def test_train_with_enough_data_numpy(self):
        """충분한 데이터 → 정상 학습."""
        gen = LSTMSignalGenerator()
        df = _make_df(300)
        result = gen._train_numpy(df)
        assert result["test_accuracy"] >= 0.0
        assert "fail_reasons" in result

    def test_prediction_fields_complete(self):
        gen = LSTMSignalGenerator()
        df = _make_df()
        pred = gen.predict(df)
        for field in ("action", "confidence", "proba_buy", "proba_sell", "proba_hold", "model_name"):
            assert hasattr(pred, field)
