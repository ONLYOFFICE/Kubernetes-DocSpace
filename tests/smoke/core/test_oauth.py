"""OAuth clients of the identity service."""
from support import endpoints
from support.constants import HTTP_DELETED, HTTP_OK, Scope
from support.oauth import delete_client, identity_headers, register_client, scope_names


def test_oauth_client_lifecycle(admin, portal):
    """The identity service lists scopes, registers a client, serves its public info and deletes it."""
    headers = identity_headers(admin)
    assert Scope.OPENID in scope_names(portal, headers), "the openid scope is missing"

    client_id = register_client(portal, headers)
    try:
        info = portal.get(endpoints.oauth_client_public_info(client_id))
        assert info.status_code == HTTP_OK, f"public client info failed: HTTP {info.status_code}"
        assert client_id in info.text
    finally:
        deleted = delete_client(portal, headers, client_id)

    assert deleted.status_code in HTTP_DELETED, f"client deletion failed: HTTP {deleted.status_code}"
