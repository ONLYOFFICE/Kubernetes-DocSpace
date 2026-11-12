"""Folders and files in My Documents: creation, a storage round-trip and versions."""
from support.constants import Field, Title
from support.files import (
    create_folder, download_file, download_version, file_versions, my_folder_id,
    unique_content, update_file, upload_file,
)


def test_my_documents_folder_is_available(admin):
    """The owner has a My Documents folder."""
    assert my_folder_id(admin)


def test_folder_can_be_created(admin):
    """A folder can be created in My Documents."""
    folder = create_folder(admin, Title.FOLDER)

    assert folder[Field.ID]


def test_uploaded_file_downloads_back_unchanged(admin):
    """An uploaded file comes back byte for byte."""
    content = unique_content("smoke upload")

    uploaded = upload_file(admin, Title.UPLOAD, content)

    assert download_file(admin, uploaded[Field.ID]) == content


def test_file_update_keeps_both_versions(admin):
    """Saving a new version keeps the previous one, each with its own content."""
    first = unique_content("version one")
    second = unique_content("version two")
    uploaded = upload_file(admin, Title.VERSIONED, first)

    update_file(admin, uploaded[Field.ID], Title.VERSIONED, second)

    versions = file_versions(admin, uploaded[Field.ID])
    assert len(versions) >= 2, f"expected two versions, got {len(versions)}"
    newest, oldest = versions[0], versions[-1]
    assert download_version(admin, newest) == second, "newest version has unexpected content"
    assert download_version(admin, oldest) == first, "oldest version has unexpected content"
