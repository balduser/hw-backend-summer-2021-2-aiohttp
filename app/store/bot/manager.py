import typing

from app.store.vk_api.dataclasses import Update, Message

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            if update.type == 'message_new':
                await self.app.store.vk_api.send_message(
                    Message(
                        user_id=update.object.message.from_id,
                        text=f'You sent: {update.object.message.text}',
                    )
                )
