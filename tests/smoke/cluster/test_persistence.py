"""Data written before the DocSpace services restart is still there afterwards."""
from support.auth import owner_token
from support.cluster import RESTARTED_DEPLOYMENTS, restart_deployments
from support.config import NAMESPACE, PORTAL_READY_INTERVAL, PORTAL_READY_TIMEOUT
from support.constants import Field, RoomType, Title
from support.files import create_room, download_file, folder_title, unique_content, upload_file
from support.readiness import wait_until_ready


def test_room_and_file_survive_a_restart_of_the_services(admin, portal, settings):
    """A room and a file created before the services restart are intact after it."""
    content = unique_content("persistent content")
    room = create_room(admin, Title.PERSISTENT_ROOM, RoomType.CUSTOM)
    uploaded = upload_file(admin, Title.PERSISTENT_FILE, content)

    restart_deployments(NAMESPACE, RESTARTED_DEPLOYMENTS)
    wait_until_ready(portal, PORTAL_READY_TIMEOUT, PORTAL_READY_INTERVAL)

    # A new login also proves that the owner is stored in the database, not in the pod.
    owner = portal.with_token(owner_token(portal, settings))
    assert folder_title(owner, room[Field.ID]) == Title.PERSISTENT_ROOM
    assert download_file(owner, uploaded[Field.ID]) == content
