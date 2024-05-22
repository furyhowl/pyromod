from enum import StrEnum


class ListenerTypes(StrEnum):
    MESSAGE = "message"
    CALLBACK_QUERY = "callback_query"
