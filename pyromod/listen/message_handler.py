from inspect import iscoroutinefunction
from typing import Callable, Tuple

import hydrogram
from hydrogram.filters import Filter
from hydrogram.types import Message

from pyromod.listen.client import Client
from pyromod.types import Identifier, Listener, ListenerTypes
from pyromod.utils import patch_into, should_patch


@patch_into(hydrogram.handlers.message_handler.MessageHandler)
class MessageHandler(hydrogram.handlers.message_handler.MessageHandler):
    filters: Filter
    old__init__: Callable

    @should_patch()
    def __init__(self, callback: Callable, filters: Filter = None):
        self.original_callback = callback
        self.old__init__(self.resolve_future_or_callback, filters)

    @should_patch()
    async def check_if_has_matching_listener(self, client: Client, message: Message) -> Tuple[bool, Listener]:
        from_user = message.from_user
        from_user_id = from_user.id if from_user else None
        from_user_username = from_user.username if from_user else None

        message_id = getattr(message, "id", getattr(message, "message_id", None))

        data = Identifier(
            message_id=message_id,
            chat_id=[message.chat.id, message.chat.username],
            from_user_id=[from_user_id, from_user_username],
        )

        listener = client.get_listener_matching_with_data(data, ListenerTypes.MESSAGE)

        listener_does_match = False

        if listener:
            filters = listener.filters
            if callable(filters):
                if iscoroutinefunction(filters.__call__):
                    listener_does_match = await filters(client, message)
                else:
                    listener_does_match = await client.loop.run_in_executor(None, filters, client, message)
            else:
                listener_does_match = True

        return listener_does_match, listener

    @should_patch()
    async def check(self, client: Client, message: Message):
        listener_does_match = (await self.check_if_has_matching_listener(client, message))[0]

        if callable(self.filters):
            if iscoroutinefunction(self.filters.__call__):
                handler_does_match = await self.filters(client, message)
            else:
                handler_does_match = await client.loop.run_in_executor(None, self.filters, client, message)
        else:
            handler_does_match = True

        # let handler get the chance to handle if listener
        # exists but its filters doesn't match
        return listener_does_match or handler_does_match

    @should_patch()
    async def resolve_future_or_callback(self, client: Client, message: Message, *args):
        listener_does_match, listener = await self.check_if_has_matching_listener(client, message)

        if listener and listener_does_match:
            client.remove_listener(listener)

            if listener.future and not listener.future.done():
                listener.future.set_result(message)

                raise hydrogram.StopPropagation
            elif listener.callback:
                if iscoroutinefunction(listener.callback):
                    await listener.callback(client, message, *args)
                else:
                    listener.callback(client, message, *args)

                raise hydrogram.StopPropagation
            else:
                raise ValueError("Listener must have either a future or a callback")
        else:
            if iscoroutinefunction(self.original_callback):
                await self.original_callback(client, message, *args)
            else:
                self.original_callback(client, message, *args)
