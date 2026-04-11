"""
Dashboard: 봇 상태를 보여주는 경량 HTTP 서버.
Flask 없이 표준 라이브러리 http.server만 사용한다.

엔드포인트:
  GET /           → HTML 상태 페이지
  GET /status     → JSON 상태
  GET /health     → {"ok": true}

별도 스레드에서 실행하므로 봇 루프를 막지 않는다.
"""

import json
import logging
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class StatusProvider:
    """대시보드가 읽는 상태 데이터 인터페이스."""

    def get_status(self) -> dict:
        raise NotImplementedError


class OrchestratorStatusProvider(StatusProvider):
    """BotOrchestrator에서 상태를 읽는 구현체."""

    def __init__(self, orchestrator):
        self._orch = orchestrator

    def get_status(self) -> dict:
        orch = self._orch
        tracker = orch.tracker

        open_positions = []
        for symbol, pos in tracker._open.items():
            open_positions.append({
                "symbol": pos.symbol,
                "side": pos.side,
                "entry_price": pos.entry_price,
                "size": pos.size,
                "stop_loss": pos.stop_loss,
                "take_profit": pos.take_profit,
                "opened_at": pos.opened_at,
            })

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "strategy": orch.cfg.strategy,
            "symbol": orch.cfg.trading.symbol,
            "timeframe": orch.cfg.trading.timeframe,
            "dry_run": getattr(orch, "_dry_run", True),
            "cycle_count": orch._cycle_count,
            "cumulative_pnl": sum(t.pnl for t in tracker._history),
            "open_positions": open_positions,
            "today_pnl": tracker.today_pnl(),
            "daily_summary": tracker.daily_summary(),
            "circuit_breaker": {
                "daily_loss": getattr(
                    orch._risk_manager.circuit_breaker, "_daily_loss", 0
                ) if orch._risk_manager and orch._risk_manager.circuit_breaker else 0,
                "consecutive_losses": getattr(
                    orch._risk_manager.circuit_breaker, "_consecutive_losses", 0
                ) if orch._risk_manager and orch._risk_manager.circuit_breaker else 0,
            },
            "regime": getattr(orch, "_last_regime", None),
            "last_tournament_winner": getattr(orch, "_last_tournament_winner", None),
            "impl_shortfall_avg_bps": (
                sum(orch._impl_shortfall_samples) / len(orch._impl_shortfall_samples)
                if getattr(orch, "_impl_shortfall_samples", None)
                else None
            ),
        }


class MultiStatusProvider(StatusProvider):
    """MultiBot에서 여러 봇 상태를 집계."""

    def __init__(self, multi_bot):
        self._multi = multi_bot

    def get_status(self) -> dict:
        bots = []
        for symbol, orch in self._multi._bots.items():
            provider = OrchestratorStatusProvider(orch)
            bots.append(provider.get_status())

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": "multi",
            "bot_count": len(bots),
            "total_exposure": self._multi.total_exposure(),
            "bots": bots,
        }


def _make_handler(provider: StatusProvider):
    """클로저로 StatusProvider를 캡처한 핸들러 클래스 생성."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self._send_json({"ok": True})
            elif self.path == "/status":
                self._send_json(provider.get_status())
            elif self.path == "/" or self.path == "/index.html":
                self._send_html(provider.get_status())
            else:
                self.send_response(404)
                self.end_headers()

        def _send_json(self, data: dict):
            body = json.dumps(data, indent=2).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, data: dict):
            html = _render_html(data)
            body = html.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            logger.debug("Dashboard: " + fmt, *args)

    return Handler


def _render_html(data: dict) -> str:
    ts = data.get("timestamp", "")
    strategy = data.get("strategy", data.get("mode", ""))
    symbol = data.get("symbol", "multi")
    pnl = data.get("today_pnl", 0)
    pnl_color = "green" if pnl >= 0 else "red"
    cycles = data.get("cycle_count", 0)
    cumulative_pnl = data.get("cumulative_pnl", 0)
    cum_pnl_color = "green" if cumulative_pnl >= 0 else "red"
    _milestones = [(70, '#7b2ff7', '#fff', 'CYCLE 70 MILESTONE'),
                   (60, '#00b4d8', '#111', 'CYCLE 60 MILESTONE'),
                   (50, '#c8a800', '#111', 'CYCLE 50 MILESTONE')]
    milestone_html = ''.join(
        f" <span class='badge' style='background:{bg};color:{fg}'>{label}</span>"
        for threshold, bg, fg, label in _milestones
        if cycles >= threshold
    )
    dry_run = data.get("dry_run", True)
    mode_badge = "DRY RUN" if dry_run else "LIVE"
    mode_color = "gray" if dry_run else "red"

    positions_html = ""
    for pos in data.get("open_positions", []):
        positions_html += (
            f"<tr><td>{pos['symbol']}</td><td>{pos['side']}</td>"
            f"<td>{pos['entry_price']:.2f}</td><td>{pos['size']:.6f}</td>"
            f"<td>{pos['stop_loss']:.2f}</td><td>{pos['take_profit']:.2f}</td>"
            f"<td>{pos['opened_at'][:19]}</td></tr>"
        )
    if not positions_html:
        positions_html = '<tr><td colspan="7" style="text-align:center">No open positions</td></tr>'

    cb = data.get("circuit_breaker", {})
    daily_loss_pct = cb.get("daily_loss", 0) * 100
    consec = cb.get("consecutive_losses", 0)
    regime = data.get("regime") or "—"
    tournament_winner = data.get("last_tournament_winner") or "—"
    regime_color_map = {"bull": "#4caf50", "bear": "#f44336", "sideways": "#ff9800"}
    regime_color = regime_color_map.get(regime, "#aaa")
    daily_summary = data.get("daily_summary", "")
    sf_raw = data.get("impl_shortfall_avg_bps")
    sf_str = f"{sf_raw:+.2f} bps" if sf_raw is not None else "—"
    sf_color = "#aaa" if sf_raw is None else ("#f44336" if sf_raw > 5 else ("#ff9800" if sf_raw > 1 else "#4caf50"))

    daily_summary_html = (f'<p style="color:#aaa;font-size:13px">{daily_summary}</p>'
                          if daily_summary else "")
    # 멀티 봇 섹션
    bots_html = ""
    for bot in data.get("bots", []):
        bot_pnl = bot.get("today_pnl", 0)
        c = "green" if bot_pnl >= 0 else "red"
        bots_html += (
            f"<tr><td>{bot.get('symbol')}</td><td>{bot.get('strategy')}</td>"
            f"<td style='color:{c}'>{bot_pnl:+.2f}</td>"
            f"<td>{len(bot.get('open_positions', []))}</td>"
            f"<td>{bot.get('cycle_count', 0)}</td></tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="30">
<title>Trading Bot</title>
<style>
  body {{ font-family: monospace; background: #111; color: #eee; padding: 20px; }}
  h2 {{ color: #aaa; }}
  .badge {{ display:inline-block; padding:2px 8px; border-radius:4px; font-size:12px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
  th, td {{ border: 1px solid #333; padding: 6px 10px; text-align: left; }}
  th {{ background: #222; }}
  .stat {{ display:inline-block; margin: 0 20px 10px 0; }}
  .label {{ color: #888; font-size: 12px; }}
  .value {{ font-size: 20px; font-weight: bold; }}
</style>
</head>
<body>
<h1>Trading Bot
  <span class="badge" style="background:{mode_color}">{mode_badge}</span>
</h1>
<p style="color:#666">Updated: {ts[:19]} UTC &nbsp;|&nbsp; Auto-refresh: 30s</p>

<div>
  <div class="stat"><div class="label">Strategy</div><div class="value">{strategy}</div></div>
  <div class="stat"><div class="label">Symbol</div><div class="value">{symbol}</div></div>
  <div class="stat"><div class="label">Today P&L</div>
    <div class="value" style="color:{pnl_color}">{pnl:+.2f} USDT</div></div>
  <div class="stat"><div class="label">Cycles</div><div class="value">{cycles}{milestone_html}</div></div>
  <div class="stat"><div class="label">Cumulative P&amp;L</div>
    <div class="value" style="color:{cum_pnl_color}">{cumulative_pnl:+.2f} USDT</div></div>
  <div class="stat"><div class="label">Daily Loss</div>
    <div class="value">{daily_loss_pct:.1f}%</div></div>
  <div class="stat"><div class="label">Consec Losses</div>
    <div class="value">{consec}</div></div>
  <div class="stat"><div class="label">Market Regime</div>
    <div class="value" style="color:{regime_color}">{regime}</div></div>
  <div class="stat"><div class="label">Tournament Winner</div>
    <div class="value">{tournament_winner}</div></div>
  <div class="stat"><div class="label">Impl Shortfall (avg)</div>
    <div class="value" style="color:{sf_color}">{sf_str}</div></div>
</div>

{daily_summary_html}<h2>Open Positions</h2>
<table>
  <tr><th>Symbol</th><th>Side</th><th>Entry</th><th>Size</th>
      <th>Stop Loss</th><th>Take Profit</th><th>Opened</th></tr>
  {positions_html}
</table>

{"<h2>Bots</h2><table><tr><th>Symbol</th><th>Strategy</th><th>P&L</th><th>Positions</th><th>Cycles</th></tr>" + bots_html + "</table>" if bots_html else ""}

<p style="color:#555; font-size:11px">
  <a href="/status" style="color:#555">JSON</a> &nbsp;|&nbsp;
  <a href="/health" style="color:#555">health</a>
</p>
</body>
</html>"""


class Dashboard:
    """HTTP 대시보드 서버. 별도 스레드에서 실행."""

    def __init__(self, provider: StatusProvider, host: str = "0.0.0.0", port: int = 8080):
        self._provider = provider
        self._host = host
        self._port = port
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        handler = _make_handler(self._provider)
        self._server = HTTPServer((self._host, self._port), handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        logger.info("Dashboard running at http://%s:%d", self._host, self._port)

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
            logger.info("Dashboard stopped")
