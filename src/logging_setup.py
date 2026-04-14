"""
로깅 설정: 파일 + 콘솔 동시 출력.
logs/ 디렉토리는 .gitignore에 포함된다.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import List


def setup_logging(level: str = "INFO", log_file: str = "logs/trading.log") -> None:
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # RotatingFileHandler: 10MB per file, 5 backups (총 ~50MB)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8",
    )

    handlers: List[logging.Handler] = [
        logging.StreamHandler(),
        file_handler,
    ]

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=fmt,
        datefmt=datefmt,
        handlers=handlers,
    )

    # 외부 라이브러리 노이즈 줄이기
    logging.getLogger("ccxt").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
