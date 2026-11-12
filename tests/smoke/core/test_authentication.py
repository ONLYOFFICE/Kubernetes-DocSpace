"""First-run wizard and owner authentication."""
from support import endpoints
from support.auth import login
from support.client import body_of, preview
from support.config import PORTAL_EMAIL, WRONG_PASSWORD
from support.constants import HTTP_OK, HTTP_REJECTED, Field


def test_wizard_creates_the_portal_owner(wizard_completed, portal):
    """After the wizard the anonymous settings no longer expose a wizard token."""
    settings = body_of(portal.get(endpoints.SETTINGS))

    assert Field.WIZARD_TOKEN not in settings, "wizard is still pending"


def test_owner_can_log_in(admin):
    """The owner gets an authorization token."""
    assert admin.token


def test_login_with_wrong_password_is_rejected(portal, settings, wizard_completed):
    """A wrong password does not authenticate and leaks no token."""
    response = login(portal, settings, password=WRONG_PASSWORD)

    assert response.status_code != HTTP_OK, "wrong password must not authenticate"
    assert Field.TOKEN not in response.text


def test_people_self_returns_the_owner(admin):
    """The profile of the authorized user is the owner created by the wizard."""
    response = admin.get(endpoints.PEOPLE_SELF)

    assert response.status_code == HTTP_OK, preview(response)
    assert body_of(response)[Field.EMAIL] == PORTAL_EMAIL


def test_private_data_requires_authorization(portal, wizard_completed):
    """An anonymous client cannot read a private profile."""
    response = portal.get(endpoints.PEOPLE_SELF)

    assert response.status_code in HTTP_REJECTED, preview(response)
