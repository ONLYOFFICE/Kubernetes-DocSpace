"""Run configuration read from the environment.

Environment:
    BASE_URL          portal address reachable from the runner (default http://localhost:8092)
    NAMESPACE         Kubernetes namespace DocSpace is installed in (default "default")
    PORTAL_EMAIL      owner email created by the first-run wizard (default smoke@smoke.com)
    PORTAL_PASSWORD   owner password (default Smoke-Test-2026)
    EXPECTED_VERSION  portal version the install must report, e.g. 3.7.2 (the version test is skipped without it)
    LICENSE_FILE      path to license.lic (the wizard of DocSpace Enterprise requires a license)
    LICENSE           license content, used when LICENSE_FILE is not set
"""
import os

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8092")
NAMESPACE = os.environ.get("NAMESPACE", "default")

PORTAL_EMAIL = os.environ.get("PORTAL_EMAIL", "smoke@smoke.com")
PORTAL_PASSWORD = os.environ.get("PORTAL_PASSWORD", "Smoke-Test-2026")
WRONG_PASSWORD = "wrong-password"

EXPECTED_VERSION = os.environ.get("EXPECTED_VERSION")  # the version test is skipped when not set

LICENSE_FILE = os.environ.get("LICENSE_FILE")
LICENSE_CONTENT = os.environ.get("LICENSE")

REQUEST_TIMEOUT = 30  # seconds, any API call
CONVERSION_TIMEOUT = 180  # seconds, Document Server converts the file synchronously
PORTAL_READY_TIMEOUT = 300  # seconds, how long a slow-starting portal is waited for before the tests
PORTAL_READY_INTERVAL = 5  # seconds between polls of a portal that is not ready yet
WIZARD_TIMEOUT = 120  # seconds, the wizard validates the license through Document Server, which retries when it is down
