"""Portal URL paths, so tests never spell them out."""
ROOT = "/"
HEALTH_LIVENESS = "/healthchecks/liveness/"
UNKNOWN_API = "/api/2.0/this-endpoint-does-not-exist"

CAPABILITIES = "/api/2.0/capabilities.json"
BUILD_VERSION = "/api/2.0/settings/version/build"
SETTINGS = "/api/2.0/settings"
LICENSE_REQUIRED = "/api/2.0/settings/license/required"
LICENSE_UPLOAD = "/api/2.0/settings/license"
WIZARD_COMPLETE = "/api/2.0/settings/wizard/complete"

AUTHENTICATION = "/api/2.0/authentication"
PEOPLE_SELF = "/api/2.0/people/@self"

MY_FOLDER = "/api/2.0/files/@my"
MY_FILE = "/api/2.0/files/@my/file"
MY_UPLOAD = "/api/2.0/files/@my/upload"
ROOMS = "/api/2.0/files/rooms"


OAUTH_SIGNATURE = "/api/2.0/security/oauth2/token"
OAUTH_SCOPES = "/api/2.0/oauth2/scopes"
OAUTH_CLIENTS = "/api/2.0/oauth2/clients"


def oauth_client(client_id):
    return f"/api/2.0/oauth2/clients/{client_id}"


def oauth_client_public_info(client_id):
    return f"/api/2.0/oauth2/clients/{client_id}/public/info"


def file_link(file_id):
    return f"/api/2.0/files/file/{file_id}/link"


def folder(parent_id):
    return f"/api/2.0/files/folder/{parent_id}"


def folder_contents(folder_id):
    return f"/api/2.0/files/{folder_id}"


def file_info(file_id):
    return f"/api/2.0/files/file/{file_id}"


def file_open_edit(file_id):
    return f"/api/2.0/files/file/{file_id}/openedit"


def file_copy_as(file_id):
    return f"/api/2.0/files/file/{file_id}/copyas"


def file_history(file_id):
    return f"/api/2.0/files/file/{file_id}/history"


def file_update(file_id):
    return f"/api/2.0/files/{file_id}/update"
