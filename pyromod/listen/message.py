import hydrogram

from pyromod.utils import patch_into


@patch_into(hydrogram.types.messages_and_media.message.Message)
class Message(hydrogram.types.messages_and_media.message.Message):
    pass
