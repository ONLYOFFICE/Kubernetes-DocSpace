"""HTTP client for the portal API."""
from urllib.parse import urlparse

import requests

from support.config import REQUEST_TIMEOUT
from support.constants import HTTP_OK, Field

ERROR_PREVIEW = 300  # characters of a reply shown in an assertion message
ERROR_STACK_LINES = 6  # lines of the portal error stack shown in an assertion message


class Portal:
    """Thin wrapper around requests that prefixes every path with the portal address.

    Pass `token` to get an authorized client (the API expects it in the
    Authorization header).
    """

    def __init__(self, base_url, token=None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self._session = requests.Session()
        if token:
            self._session.headers["Authorization"] = token

    def request(self, method, path, **kwargs):
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        # The API returns absolute links (e.g. viewUrl); pass them through as they are.
        url = path if path.startswith(("http://", "https://")) else self.base_url + path
        return self._session.request(method, url, **kwargs)

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)

    def with_token(self, token):
        return Portal(self.base_url, token)


def relative_url(url):
    """Path and query of an absolute link, to request it through the portal address of the run."""
    parts = urlparse(url)
    return f"{parts.path}?{parts.query}" if parts.query else parts.path


def preview(response):
    """Beginning of a reply for an assertion message."""
    return response.text[:ERROR_PREVIEW]


def body_of(response):
    """The `response` payload of a portal API reply; the raw text goes into the error if absent."""
    data = response.json()
    assert Field.RESPONSE in data, f"unexpected API reply: {preview(response)}"
    return data[Field.RESPONSE]


def payload(response):
    """Portal endpoints wrap results into `response`; the identity service answers bare."""
    data = response.json()
    return data[Field.RESPONSE] if isinstance(data, dict) and Field.RESPONSE in data else data


def find_key(node, key):
    """Depth-first search for a non-empty key in nested JSON; None when absent."""
    if isinstance(node, dict):
        if node.get(key):
            return node[key]
        children = node.values()
    elif isinstance(node, list):
        children = node
    else:
        return None
    for child in children:
        found = find_key(child, key)
        if found:
            return found
    return None


def describe_failure(response):
    """Status and error of a failed call; for a portal error also the top of its stack, one line each."""
    status = f"HTTP {response.status_code}"
    try:
        error = response.json()["error"]
    except (ValueError, KeyError, TypeError):
        return f"{status} {preview(response)}"
    if not isinstance(error, dict):
        return f"{status} {preview(response)}"
    stack = [line.strip() for line in (error.get("stack") or "").splitlines() if line.strip()]
    return "\n".join([f"{status} {error.get('message')}", *stack[:ERROR_STACK_LINES]])


def expect_ok(response, action):
    """Assert the call succeeded and return its payload."""
    assert response.status_code == HTTP_OK, f"{action} failed: {describe_failure(response)}"
    return body_of(response)
