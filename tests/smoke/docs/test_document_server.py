"""Document Server: it builds and converts documents for DocSpace."""
import pytest

from support.client import relative_url
from support.constants import EDITOR_API_MARKER, HTTP_OK, RTF_CONTENT, DocumentType, Field, Signature, Title
from support.files import convert, create_document, download_file, open_editor_config, upload_file


def test_empty_document_can_be_created(admin):
    """Document Server builds an empty document from a template."""
    document = create_document(admin, Title.DOCUMENT)

    assert document[Field.ID]
    assert document[Field.WEB_URL]


@pytest.mark.parametrize("source, target, signature", [
    (Title.CONVERSION_SOURCE, Title.CONVERSION_TARGET, Signature.PDF),
])
def test_document_server_converts_files(admin, source, target, signature):
    """Conversion proves that DocSpace, Document Server, Redis and RabbitMQ work together."""
    source_file = create_document(admin, source)

    converted = convert(admin, source_file[Field.ID], target)

    content = download_file(admin, converted[Field.ID])
    assert content.startswith(signature), f"unexpected file signature: {content[:8]!r}"


def test_rtf_file_converts_to_docx(admin):
    """A legacy RTF file is converted to DOCX."""
    source_file = upload_file(admin, Title.RTF_SOURCE, RTF_CONTENT)

    converted = convert(admin, source_file[Field.ID], Title.RTF_TARGET)

    content = download_file(admin, converted[Field.ID])
    assert content.startswith(Signature.ZIP), f"unexpected file signature: {content[:8]!r}"


def test_editor_config_leads_to_a_reachable_editor_script(admin, portal):
    """The editor config names a Document Server script that browsers reach through the router."""
    document = create_document(admin, Title.EDITOR_DOCUMENT)

    config = open_editor_config(admin, document[Field.ID])

    assert config[Field.DOCUMENT_TYPE] == DocumentType.WORD
    script = portal.get(relative_url(config[Field.EDITOR_URL]))
    assert script.status_code == HTTP_OK, f"editor script {config[Field.EDITOR_URL]} failed: HTTP {script.status_code}"
    assert EDITOR_API_MARKER in script.text, "the editor script is not the Document Server API"
