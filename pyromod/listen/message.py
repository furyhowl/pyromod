import pyrogram

from ..utils import patch_into


@patch_into(pyrogram.types.messages_and_media.message.Message)
class Message(pyrogram.types.messages_and_media.message.Message):
    pass
