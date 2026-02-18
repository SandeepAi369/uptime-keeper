#!/usr/bin/env python3
"""
Uptime Keeper - Self-Healing Ping Script
==========================================
Keeps Render free-tier services alive by sending periodic HTTP pings.
Designed to run via GitHub Actions on a cron schedule.

Features:
  - Secure: reads URL from environment variable (GitHub Secret)
  - Reliable: retry logic with exponential backoff (3 attempts)
  - Observable: structured logging with timestamps, status codes, response times
  - Fail-safe: graceful error handling for all network failure modes
"""

import os
import sys
import time
import logging
from datetime import datetime, timezone

import requests

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 5
REQUEST_TIMEOUT_SECONDS = 60
ENV_VAR_NAME = "RENDER_URL"

# ──────────────────────────────────────────────
# Logging Setup
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("uptime-keeper")


def ping_service(url: str) -> bool:
    """
    Send a GET request to the target URL with retry logic.

    Args:
        url: The service URL to ping.

    Returns:
        True if a successful response (2xx) was received, False otherwise.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        backoff = INITIAL_BACKOFF_SECONDS * (2 ** (attempt - 1))

        try:
            logger.info(
                "Attempt %d/%d — Pinging: %s",
                attempt,
                MAX_RETRIES,
                url,
            )

            start_time = time.monotonic()
            response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
            elapsed_ms = (time.monotonic() - start_time) * 1000

            if response.ok:
                logger.info(
                    "✅ Success | Status: %d | Response Time: %.0f ms",
                    response.status_code,
                    elapsed_ms,
                )
                return True
            else:
                logger.warning(
                    "⚠️  Unexpected Status | Code: %d | Response Time: %.0f ms",
                    response.status_code,
                    elapsed_ms,
                )

        except requests.exceptions.ConnectionError:
            logger.error(
                "🔌 Connection Error on attempt %d/%d — server may be down.",
                attempt,
                MAX_RETRIES,
            )
        except requests.exceptions.Timeout:
            logger.error(
                "⏱️  Timeout on attempt %d/%d — no response within %ds.",
                attempt,
                MAX_RETRIES,
                REQUEST_TIMEOUT_SECONDS,
            )
        except requests.exceptions.RequestException as exc:
            logger.error(
                "❌ Request Failed on attempt %d/%d — %s",
                attempt,
                MAX_RETRIES,
                exc,
            )

        if attempt < MAX_RETRIES:
            logger.info("⏳ Retrying in %d seconds...", backoff)
            time.sleep(backoff)

    return False


def main() -> None:
    """Entry point — fetch URL from env, ping, and report."""
    logger.info("═" * 55)
    logger.info(
        "🚀  Uptime Keeper  |  Run started at %s UTC",
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    )
    logger.info("═" * 55)

    url = os.environ.get(ENV_VAR_NAME)

    if not url:
        logger.critical(
            "🚫 Environment variable '%s' is not set! "
            "Add it as a GitHub Secret and map it in the workflow.",
            ENV_VAR_NAME,
        )
        sys.exit(1)

    # Ensure the URL has a scheme
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
        logger.info("ℹ️  No scheme detected — prepended https:// → %s", url)

    success = ping_service(url)

    logger.info("═" * 55)
    if success:
        logger.info("🎉 Service is alive and responding!")
    else:
        logger.error(
            "💀 All %d ping attempts failed. Service may be unreachable.",
            MAX_RETRIES,
        )
        sys.exit(1)
    logger.info("═" * 55)


if __name__ == "__main__":
    main()
