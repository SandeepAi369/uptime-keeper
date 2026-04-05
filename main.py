#!/usr/bin/env python3
"""
Uptime Keeper - Multi-Service Ping Script
==========================================
Keeps free-tier services alive by sending periodic HTTP pings.
Designed to run via GitHub Actions on a cron schedule.

Supports multiple services:
  - RENDER_URL: Render free-tier backend
  - HF_SPACE_URL: HuggingFace Space (search engine)
  - Any additional *_URL env vars

Features:
  - Multi-target: pings all configured services independently
  - Reliable: retry logic with backoff (3 attempts per service)
  - Observable: structured logging with timestamps and response times
  - Fail-safe: one service failing doesn't block others
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
FIXED_BACKOFF_SECONDS = 10
REQUEST_TIMEOUT_SECONDS = 30

# All env vars that contain URLs to ping
URL_ENV_VARS = ["RENDER_URL", "HF_SPACE_URL"]

# ──────────────────────────────────────────────
# Logging Setup
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("uptime-keeper")


def ping_service(name: str, url: str) -> bool:
    """
    Send a GET request to the target URL with retry logic.

    Args:
        name: Human-readable service name for logging.
        url: The service URL to ping.

    Returns:
        True if a successful response (2xx) was received, False otherwise.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(
                "[%s] Attempt %d/%d — Pinging: %s",
                name, attempt, MAX_RETRIES, url,
            )

            start_time = time.monotonic()
            response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
            elapsed_ms = (time.monotonic() - start_time) * 1000

            if response.ok:
                logger.info(
                    "[%s] ✅ UP | Status: %d | Time: %.0f ms",
                    name, response.status_code, elapsed_ms,
                )
                return True
            else:
                logger.warning(
                    "[%s] ⚠️  Status: %d | Time: %.0f ms",
                    name, response.status_code, elapsed_ms,
                )

        except requests.exceptions.ConnectionError:
            logger.error("[%s] 🔌 Connection Error (attempt %d)", name, attempt)
        except requests.exceptions.Timeout:
            logger.error("[%s] ⏱️  Timeout (attempt %d)", name, attempt)
        except requests.exceptions.RequestException as exc:
            logger.error("[%s] ❌ Error (attempt %d): %s", name, attempt, exc)

        if attempt < MAX_RETRIES:
            logger.info("[%s] ⏳ Retry in %ds...", name, FIXED_BACKOFF_SECONDS)
            time.sleep(FIXED_BACKOFF_SECONDS)

    return False


def main() -> None:
    """Entry point — ping all configured services."""
    logger.info("═" * 55)
    logger.info(
        "🚀  Uptime Keeper  |  %s UTC",
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    )
    logger.info("═" * 55)

    # Collect all configured URLs
    targets = {}
    for var in URL_ENV_VARS:
        url = os.environ.get(var, "").strip()
        if url:
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"
            targets[var] = url

    if not targets:
        logger.critical("🚫 No URLs configured! Set at least one: %s", URL_ENV_VARS)
        sys.exit(1)

    logger.info("📡 Targets: %d services", len(targets))
    for name, url in targets.items():
        logger.info("  → %s: %s", name, url)

    # Ping each service independently
    results = {}
    for name, url in targets.items():
        logger.info("─" * 45)
        results[name] = ping_service(name, url)

    # Summary
    logger.info("═" * 55)
    all_ok = True
    for name, ok in results.items():
        status = "✅ UP" if ok else "💀 DOWN"
        logger.info("  %s: %s", name, status)
        if not ok:
            all_ok = False

    if all_ok:
        logger.info("🎉 All services alive!")
    else:
        logger.error("⚠️  Some services are down!")
        # Don't exit(1) — partial success is still useful
    logger.info("═" * 55)


if __name__ == "__main__":
    main()
