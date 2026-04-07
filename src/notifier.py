"""
TelegramNotifier: sends pipeline results and alerts via Telegram Bot API.
Uses requests directly — no python-telegram-bot dependency.
Notification failures never raise; they are logged and silently skipped.
"""

import logging
import os
from typing import Optional

import requests

from src.pipeline.runner import PipelineResult

logger = logging.getLogger(__name__)

_TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


class TelegramNotifier:
    """
    Sends messages to a Telegram chat.

    Token and chat_id are resolved in this order:
      1. Constructor arguments (passed from TelegramConfig)
      2. Environment variables TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID

    If no token is available, all notify_* methods silently do nothing.
    """

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        enabled: bool = True,
    ) -> None:
        self._token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self._chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")
        self._enabled = enabled and bool(self._token) and bool(self._chat_id)

        if enabled and not self._enabled:
            logger.debug(
                "TelegramNotifier: no token/chat_id configured — notifications disabled"
            )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def notify_pipeline(self, result: PipelineResult) -> None:
        """Send a summary of a completed pipeline run."""
        if not self._enabled:
            return
        message = _format_pipeline(result)
        self._send(message)

    def notify_error(self, message: str) -> None:
        """Send a plain error alert."""
        if not self._enabled:
            return
        text = f"[ERROR] {message}"
        self._send(text)

    def notify_startup(self, strategy: str, symbol: str, dry_run: bool) -> None:
        """Send a startup notification."""
        if not self._enabled:
            return
        mode = "DRY RUN" if dry_run else "LIVE"
        text = (
            f"[STARTUP] Trading bot started\n"
            f"Strategy: {strategy}\n"
            f"Symbol:   {symbol}\n"
            f"Mode:     {mode}"
        )
        self._send(text)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _send(self, text: str) -> None:
        """POST a message to the Telegram Bot API. Never raises."""
        url = _TELEGRAM_API.format(token=self._token)
        payload = {
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": "HTML",
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            if not resp.ok:
                logger.warning(
                    "Telegram send failed (%s): %s", resp.status_code, resp.text[:200]
                )
        except requests.RequestException as exc:
            logger.warning("Telegram send error: %s", exc)


# ------------------------------------------------------------------
# Message formatters
# ------------------------------------------------------------------


def _format_pipeline(result: PipelineResult) -> str:
    """Build a concise, emoji-free plain-text summary of a PipelineResult."""
    lines = [
        f"[PIPELINE] {result.timestamp}",
        f"Symbol:   {result.symbol}",
        f"Step:     {result.pipeline_step}",
        f"Status:   {result.status}",
    ]

    if result.signal:
        sig = result.signal
        lines.append(
            f"Signal:   {sig.action.value} @ {sig.entry_price:.2f}"
            f"  ({sig.confidence.value})"
        )

    if result.risk:
        risk = result.risk
        risk_line = f"Risk:     {risk.status.value}"
        if risk.reason:
            risk_line += f" — {risk.reason}"
        lines.append(risk_line)
        if risk.position_size is not None:
            lines.append(
                f"  size={risk.position_size:.4f}"
                f"  SL={risk.stop_loss}"
                f"  TP={risk.take_profit}"
            )

    if result.execution:
        exec_status = result.execution.get("status", "UNKNOWN")
        lines.append(f"Exec:     {exec_status}")
        if result.execution.get("order_id"):
            lines.append(f"  order_id={result.execution['order_id']}")

    if result.notes:
        lines.append(f"Notes:    {' | '.join(result.notes)}")

    if result.error:
        lines.append(f"Error:    {result.error}")

    return "\n".join(lines)
