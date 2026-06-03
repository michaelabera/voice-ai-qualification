"""
logging_utils.py — Structured JSON logging with automatic PII redaction.

Every log line is JSON (machine-parseable for any log aggregator). A redaction
filter scrubs phone numbers, emails, and any field named like PII before it ever
reaches a handler — so logs are safe to ship off-box.
"""

from __future__ import annotations

import json
import logging
import re
import sys

_PHONE = re.compile(r"\+?\d[\d\-\(\)\s]{7,}\d")
_EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_PII_KEYS = {"phone", "name", "email", "caller_phone", "caller_name"}


def _redact_text(text: str) -> str:
    text = _PHONE.sub("[REDACTED_PHONE]", text)
    text = _EMAIL.sub("[REDACTED_EMAIL]", text)
    return text


def redact(obj):
    """Recursively redact PII from dicts/lists/strings."""
    if isinstance(obj, dict):
        return {
            k: ("[REDACTED]" if k.lower() in _PII_KEYS else redact(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [redact(v) for v in obj]
    if isinstance(obj, str):
        return _redact_text(obj)
    return obj


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "msg": _redact_text(record.getMessage()),
        }
        if hasattr(record, "extra_fields"):
            payload.update(redact(record.extra_fields))
        return json.dumps(payload)


def get_logger(name: str = "voice_ai") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def log_event(logger: logging.Logger, message: str, **fields) -> None:
    """Log a structured event; PII in fields is auto-redacted."""
    record = logger.makeRecord(
        logger.name, logging.INFO, __file__, 0, message, None, None
    )
    record.extra_fields = fields
    logger.handle(record)
