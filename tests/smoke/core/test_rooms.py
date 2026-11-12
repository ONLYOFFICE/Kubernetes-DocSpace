"""Rooms: collaboration spaces of DocSpace."""
from support.constants import Field, RoomType, Title
from support.files import create_room


def test_custom_room_can_be_created(admin):
    """The owner can create a custom room."""
    room = create_room(admin, Title.ROOM, RoomType.CUSTOM)

    assert room[Field.ID]
