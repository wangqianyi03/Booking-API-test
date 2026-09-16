"""日志：控制台 + 文件双输出，请求日志会脱敏 password / token。"""

import logging
import sys
from datetime import datetime
from pathlib import Path

_LOGGER_NAME = "booking_test"
_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"


def get_logger() -> logging.Logger:
    return logging.getLogger(_LOGGER_NAME)


def setup_logger(log_dir: Path, level: str = "INFO") -> logging.Logger:
    logger = get_logger()
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level, logging.INFO))
    logger.propagate = False

    formatter = logging.Formatter(_FORMAT, datefmt=_DATEFMT)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    log_dir.mkdir(parents=True, exist_ok=True)
    logfile = log_dir / f"api_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(logfile, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("日志已初始化，输出文件: %s", logfile)
    return logger


SENSITIVE_KEYS = {"password", "token", "authorization", "cookie"}


def mask_sensitive(data: object) -> object:   #递归脱敏
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if str(key).lower() in SENSITIVE_KEYS:
                masked[key] = "***"
            else:
                masked[key] = mask_sensitive(value)
        return masked
    if isinstance(data, list):
        return [mask_sensitive(item) for item in data]
    return data
