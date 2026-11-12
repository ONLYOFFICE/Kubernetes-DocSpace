"""Waiting for the portal to start answering."""
import time

import requests

from support import endpoints
from support.client import preview
from support.constants import HTTP_OK, Field

ATTEMPT_TIMEOUT = 10  # seconds, one poll must not hang for the whole wait
REASON_PREVIEW = 200  # characters of the last answer shown when the wait runs out


def wait_until_ready(portal, timeout, interval):
    """Poll the anonymous settings until the portal answers with JSON.

    A portal that is still starting answers 502 or refuses the connection; once the
    time is up the last such answer goes into the error, so a slow start is told
    apart from a broken one.
    """
    deadline = time.monotonic() + timeout
    reason = "no attempt was made"
    while True:
        try:
            response = portal.get(endpoints.SETTINGS, timeout=ATTEMPT_TIMEOUT)
            if response.status_code == HTTP_OK and Field.RESPONSE in response.json():
                return
            reason = f"HTTP {response.status_code} {preview(response)}"
        except (requests.RequestException, ValueError) as error:
            reason = f"{type(error).__name__}: {error}"
        if time.monotonic() >= deadline:
            break
        time.sleep(interval)
    raise AssertionError(f"portal is not ready after {timeout} s, last answer: {reason[:REASON_PREVIEW]}")
