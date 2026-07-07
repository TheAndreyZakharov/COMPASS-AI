from __future__ import annotations

import logging

from sandbox_app.backend.core.paths import LOGS_DIR


def configure_logging() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )