"""OAuth clients of the identity service."""
import uuid

from support import endpoints
from support.client import find_key, payload
from support.constants import HTTP_CREATED, HTTP_OK, SIGNATURE_HEADER, Field, Scope

CLIENT_SITE = "https://smoke.com"


def identity_headers(admin):
    """The identity service wants a signature issued to the logged-in user, in a header and a cookie."""
    response = admin.get(endpoints.OAUTH_SIGNATURE)
    signature = payload(response)
    assert response.status_code == HTTP_OK and isinstance(signature, str) and signature, \
        f"no identity signature: HTTP {response.status_code} {response.text[:200]}"
    return {SIGNATURE_HEADER: signature, "Cookie": f"{SIGNATURE_HEADER}={signature}"}


def scope_names(client, headers):
    response = client.get(endpoints.OAUTH_SCOPES, headers=headers)
    scopes = payload(response) if response.status_code == HTTP_OK else []
    return {scope.get(Field.NAME) for scope in scopes} if isinstance(scopes, list) else set()


def client_request():
    """Registration form of a throwaway client."""
    return {
        "name": f"Smoke client {uuid.uuid4().hex[:8]}",
        "description": "Created by the smoke test",
        "logo": "data:image/png;base64,ivBORw0KGgo=",
        "allow_pkce": False,
        "is_public": False,
        "website_url": CLIENT_SITE,
        "terms_url": f"{CLIENT_SITE}/terms",
        "policy_url": f"{CLIENT_SITE}/policy",
        "redirect_uris": [f"{CLIENT_SITE}/callback"],
        "allowed_origins": [CLIENT_SITE],
        "logout_redirect_uri": f"{CLIENT_SITE}/logout",
        "scopes": [Scope.OPENID, Scope.FILES_READ],
    }


def register_client(client, headers):
    """Register a client and return its id."""
    response = client.post(endpoints.OAUTH_CLIENTS, json=client_request(), headers=headers)
    client_id = find_key(response.json(), Field.CLIENT_ID) if response.status_code in HTTP_CREATED else None
    assert client_id, f"client registration failed: HTTP {response.status_code} {response.text[:300]}"
    return client_id


def delete_client(client, headers, client_id):
    return client.delete(endpoints.oauth_client(client_id), headers=headers)
