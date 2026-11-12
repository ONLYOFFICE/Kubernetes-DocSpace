"""File, folder and room scenarios on behalf of an authorized client."""
import uuid
from urllib.parse import parse_qs, urlparse

from support import endpoints
from support.client import expect_ok, find_key
from support.config import CONVERSION_TIMEOUT
from support.constants import HTTP_OK, Field


def unique_content(prefix):
    """Bytes nobody else uploaded, so a round-trip proves we got our own file back."""
    return f"{prefix} {uuid.uuid4().hex}".encode()


def my_folder_id(client):
    return expect_ok(client.get(endpoints.MY_FOLDER), "open My Documents")[Field.CURRENT][Field.ID]


def folder_title(client, folder_id):
    """Title of a folder or a room."""
    return expect_ok(client.get(endpoints.folder_contents(folder_id)), "open folder")[Field.CURRENT][Field.TITLE]


def create_document(client, title):
    """Empty document built by Document Server from a template."""
    return expect_ok(client.post(endpoints.MY_FILE, json={Field.TITLE: title}), "create document")


def create_folder(client, title, parent_id=None):
    parent_id = parent_id or my_folder_id(client)
    return expect_ok(client.post(endpoints.folder(parent_id), json={Field.TITLE: title}), "create folder")


def create_room(client, title, room_type):
    return expect_ok(client.post(endpoints.ROOMS, json={Field.TITLE: title, "roomType": room_type}), "create room")


def upload_file(client, title, content):
    uploaded = expect_ok(client.post(endpoints.MY_UPLOAD, files={"file": (title, content)}), "upload")
    return uploaded[0]


def update_file(client, file_id, title, content):
    """Save new content as the next version of an existing file."""
    return expect_ok(client.put(endpoints.file_update(file_id), files={"file": (title, content)}), "update file")


def file_versions(client, file_id):
    """Version history, the newest version first."""
    history = expect_ok(client.get(endpoints.file_history(file_id)), "read history")
    return sorted(history, key=lambda item: item[Field.VERSION], reverse=True)


def download(client, url):
    response = client.get(url)
    assert response.status_code == HTTP_OK, f"download failed: HTTP {response.status_code}"
    return response.content


def download_file(client, file_id):
    file_info = expect_ok(client.get(endpoints.file_info(file_id)), "read file info")
    return download(client, file_info[Field.VIEW_URL])


def download_version(client, version):
    """Content of one entry of `file_versions`."""
    url = version[Field.VIEW_URL]
    separator = "&" if "?" in url else "?"
    return download(client, f"{url}{separator}{Field.VERSION}={version[Field.VERSION]}")


def open_editor_config(client, file_id):
    """What the portal hands to a browser to open the file in the editor."""
    return expect_ok(client.get(endpoints.file_open_edit(file_id)), "get editor config")


def create_share_key(client, file_id, access):
    """Create the primary external link of a file and return its key (it goes into Request-Token)."""
    shared = expect_ok(client.post(endpoints.file_link(file_id), json={"access": access}), "create external link")
    key = find_key(shared, Field.REQUEST_TOKEN)
    if not key:
        link = find_key(shared, Field.SHARE_LINK) or ""
        key = (parse_qs(urlparse(link).query).get("share") or [None])[0]
    assert key, f"no key in the external link reply: {shared}"
    return key


def convert(client, file_id, target_title):
    """Copy a file under a new title; Document Server converts it by the extension."""
    return expect_ok(
        client.post(
            endpoints.file_copy_as(file_id),
            json={"destFolderId": my_folder_id(client), "destTitle": target_title},
            timeout=CONVERSION_TIMEOUT,
        ),
        "convert file",
    )
