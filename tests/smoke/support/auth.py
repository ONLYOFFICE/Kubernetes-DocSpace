"""First-run wizard and owner login."""
import hashlib
import os

from support import endpoints
from support.client import body_of, expect_ok, preview
from support.config import LICENSE_CONTENT, LICENSE_FILE, PORTAL_EMAIL, PORTAL_PASSWORD, WIZARD_TIMEOUT
from support.constants import HTTP_OK, LICENSE_FILE_NAME, WIZARD_LANGUAGE, WIZARD_TIME_ZONE, Field


def password_hash(settings, password=PORTAL_PASSWORD):
    """Hash the password the way the portal expects (PBKDF2-SHA256, params from settings)."""
    params = settings["passwordHash"]
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), params["salt"].encode(),
        params["iterations"], params["size"] // 8,
    ).hex()


def read_license():
    """License bytes from LICENSE_FILE or LICENSE; None when neither is set."""
    if LICENSE_FILE and os.path.isfile(LICENSE_FILE):
        with open(LICENSE_FILE, "rb") as license_file:
            return license_file.read()
    return LICENSE_CONTENT.encode() if LICENSE_CONTENT else None


def upload_license_if_required(portal, confirm):
    """The Enterprise wizard refuses to finish without a license."""
    required = portal.get(endpoints.LICENSE_REQUIRED, headers=confirm)
    if required.status_code != HTTP_OK or not required.json().get(Field.RESPONSE):
        return
    license_bytes = read_license()
    assert license_bytes, "a license is required: set LICENSE_FILE (path) or LICENSE (content)"
    expect_ok(
        portal.post(
            endpoints.LICENSE_UPLOAD, headers=confirm, files={"Files": (LICENSE_FILE_NAME, license_bytes)},
            timeout=WIZARD_TIMEOUT,
        ),
        "license upload",
    )


def complete_wizard(portal, settings):
    """Create the portal owner. Returns False when the wizard was already completed.

    The wizard token is present in the settings only while the wizard is pending,
    so an already initialized portal is left as it is.
    """
    token = settings.get(Field.WIZARD_TOKEN)
    if not token:
        return False
    confirm = {"confirm": token}
    upload_license_if_required(portal, confirm)

    response = portal.put(
        endpoints.WIZARD_COMPLETE, headers=confirm,
        json={
            "email": PORTAL_EMAIL,
            "PasswordHash": password_hash(settings),
            "lng": WIZARD_LANGUAGE,
            "timeZone": WIZARD_TIME_ZONE,
        },
        timeout=WIZARD_TIMEOUT,
    )
    assert response.status_code == HTTP_OK, f"wizard failed: {preview(response)}"
    assert body_of(response).get(Field.COMPLETED), f"wizard not completed: {preview(response)}"
    return True


def login(portal, settings, password=PORTAL_PASSWORD):
    """Raw authentication reply, so tests can inspect both success and rejection."""
    return portal.post(
        endpoints.AUTHENTICATION,
        json={"userName": PORTAL_EMAIL, "passwordHash": password_hash(settings, password)},
    )


def owner_token(portal, settings):
    """Token of the portal owner."""
    token = expect_ok(login(portal, settings), "login").get(Field.TOKEN)
    assert token, "no token in the login reply"
    return token
