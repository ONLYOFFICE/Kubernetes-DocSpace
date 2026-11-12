"""The portal is reachable through the router and routes requests correctly."""
from support import endpoints
from support.client import preview
from support.constants import HTML_MARKER, HTTP_NOT_FOUND, HTTP_OK


def test_root_page_is_served(portal):
    """The root page returns HTML."""
    response = portal.get(endpoints.ROOT)

    assert response.status_code == HTTP_OK, preview(response)
    assert HTML_MARKER in response.text.lower(), "root page should return HTML"


def test_healthchecks_service_is_alive(portal):
    """The healthchecks service behind the router answers (enabled in the chart by default)."""
    response = portal.get(endpoints.HEALTH_LIVENESS)

    assert response.status_code == HTTP_OK, preview(response)


def test_unknown_api_path_returns_404_not_gateway_error(portal):
    """An unknown API path gives 404; 502/503 would mean the router lost its upstream."""
    response = portal.get(endpoints.UNKNOWN_API)

    assert response.status_code == HTTP_NOT_FOUND, preview(response)
