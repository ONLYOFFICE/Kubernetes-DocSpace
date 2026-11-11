"""Sharing: files opened by an external link."""
from support import endpoints
from support.client import body_of, preview
from support.constants import HTTP_NO_ACCESS, HTTP_OK, REQUEST_TOKEN_HEADER, Access, Field, Title
from support.files import create_share_key, unique_content, upload_file


def test_external_link_opens_the_file_only_with_its_key(admin, portal):
    """An external read link opens the file without a login, and only with its key."""
    uploaded = upload_file(admin, Title.PUBLIC_LINK_FILE, unique_content("smoke link"))
    key = create_share_key(admin, uploaded[Field.ID], Access.READ)

    with_key = portal.get(endpoints.file_info(uploaded[Field.ID]), headers={REQUEST_TOKEN_HEADER: key})
    without_key = portal.get(endpoints.file_info(uploaded[Field.ID]))

    assert with_key.status_code == HTTP_OK, f"the key does not open the file: {preview(with_key)}"
    assert body_of(with_key)[Field.ID] == uploaded[Field.ID]
    assert without_key.status_code in HTTP_NO_ACCESS, f"the file is open without the key: HTTP {without_key.status_code}"
