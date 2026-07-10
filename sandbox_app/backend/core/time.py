from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


def moscow_now() -> datetime:
    return datetime.now(MOSCOW_TZ)


def moscow_now_iso() -> str:
    return moscow_now().replace(microsecond=0).isoformat()


def moscow_stamp(compact: bool = True) -> str:
    pattern = "%Y%m%d_%H%M%S" if compact else "%Y-%m-%d_%H-%M-%S"
    return moscow_now().strftime(pattern)
