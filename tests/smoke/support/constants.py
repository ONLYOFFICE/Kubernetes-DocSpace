"""Values the tests compare against: titles, signatures, status codes and JSON field names."""
HTTP_OK = 200
HTTP_NOT_FOUND = 404
HTTP_REJECTED = (401, 403)  # anonymous access to private data
HTTP_NO_ACCESS = (401, 403, 404)  # a file hidden from a client that has no right to it
HTTP_DELETED = (200, 204)
HTTP_CREATED = (200, 201)

REQUEST_TOKEN_HEADER = "Request-Token"  # carries the key of an external link
SIGNATURE_HEADER = "x-signature"  # carries the signature the identity service issues

WIZARD_LANGUAGE = "en"
WIZARD_TIME_ZONE = "UTC"
LICENSE_FILE_NAME = "license.lic"

HTML_MARKER = "<html"


RTF_CONTENT = rb"{\rtf1\ansi\deff0{\fonttbl{\f0 Arial;}}\f0 Smoke conversion text\par}"


class RoomType:
    CUSTOM = 5


class DocumentType:
    """Editor type the portal reports for a file."""
    WORD = "word"


EDITOR_API_MARKER = "DocsAPI"  # the global the editor script defines


class Access:
    READ = 2  # access level of an external link


class Scope:
    OPENID = "openid"
    FILES_READ = "files:read"


class Field:
    """Keys of the JSON the portal API returns."""
    RESPONSE = "response"
    ID = "id"
    TITLE = "title"
    EMAIL = "email"
    TOKEN = "token"
    WIZARD_TOKEN = "wizardToken"
    COMPLETED = "completed"
    DOC_SPACE = "docSpace"
    VERSION = "version"
    VIEW_URL = "viewUrl"
    WEB_URL = "webUrl"
    CURRENT = "current"
    REQUEST_TOKEN = "requestToken"
    SHARE_LINK = "shareLink"
    EDITOR_URL = "editorUrl"
    DOCUMENT_TYPE = "documentType"
    CLIENT_ID = "client_id"
    NAME = "name"


class Title:
    DOCUMENT = "smoke.docx"
    FOLDER = "smoke folder"
    ROOM = "smoke room"
    UPLOAD = "smoke-upload.txt"
    VERSIONED = "smoke-versions.txt"
    PUBLIC_LINK_FILE = "smoke-link.txt"
    EDITOR_DOCUMENT = "smoke-editor.docx"
    PERSISTENT_ROOM = "smoke persistent room"
    PERSISTENT_FILE = "smoke-persistent.txt"
    CONVERSION_SOURCE = "smoke-convert.docx"
    CONVERSION_TARGET = "smoke-converted.pdf"
    RTF_SOURCE = "smoke-convert.rtf"
    RTF_TARGET = "smoke-converted.docx"


class Signature:
    """First bytes of a file format."""
    PDF = b"%PDF"
    ZIP = b"PK"  # DOCX is a zip archive
