"""Public (unauthenticated) API endpoints answer with valid JSON."""
import pytest

from support import endpoints
from support.client import body_of, preview
from support.config import EXPECTED_VERSION
from support.constants import HTTP_OK, Field


def test_capabilities_endpoint_returns_json_object(portal):
    """The capabilities endpoint returns a JSON object."""
    response = portal.get(endpoints.CAPABILITIES)

    assert response.status_code == HTTP_OK, preview(response)
    assert isinstance(response.json(), dict)


def test_build_version_is_reported(portal):
    """The build version comes from the database, so it proves API and MySQL work together."""
    response = portal.get(endpoints.BUILD_VERSION)

    assert response.status_code == HTTP_OK, preview(response)
    assert response.json().get(Field.RESPONSE), f"version info is empty: {preview(response)}"


def test_portal_identifies_itself_as_docspace(portal):
    """The anonymous settings carry the DocSpace flag and the portal version."""
    response = portal.get(endpoints.SETTINGS)

    assert response.status_code == HTTP_OK, preview(response)
    settings = body_of(response)
    assert settings.get(Field.DOC_SPACE), f"portal does not identify as DocSpace: {settings}"
    assert settings.get(Field.VERSION), f"portal version is missing: {settings}"


@pytest.mark.skipif(not EXPECTED_VERSION, reason="EXPECTED_VERSION is not set")
def test_portal_version_matches_the_chart(portal):
    """The installed portal reports the version the chart is meant to install."""
    version = body_of(portal.get(endpoints.SETTINGS)).get(Field.VERSION) or ""

    assert version == EXPECTED_VERSION or version.startswith(EXPECTED_VERSION + "."), \
        f"expected version {EXPECTED_VERSION}, got {version}"
