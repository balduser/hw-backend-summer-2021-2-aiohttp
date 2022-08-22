import random
import typing
from typing import Optional

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update, UpdateObject, UpdateMessage
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application


class VkApiAccessor(BaseAccessor):
    VK_API = 'https://api.vk.com/method/'

    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector())
        await self._get_long_poll_service()
        self.poller = Poller(app.store)
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.session:
            await self.session.close()
        if self.poller:
            await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        """Launched once at the startup to define current VK api server"""
        url = self._build_query(
            host=self.VK_API,
            method='groups.getLongPollServer',
            params={
                'group_id': self.app.config.bot.group_id,
                'access_token': self.app.config.bot.token,
            },
        )
        response = await self.session.get(url)
        response_json = await response.json()
        print(response_json)
        data = response_json['response']
        self.key = data['key']
        self.server = data['server']
        self.ts = data['ts']

    async def poll(self):
        url = self._build_query(
                host=self.server,
                method='',
                params={
                    'act': 'a_check',
                    'key': self.key,
                    'ts': self.ts,
                    'wait': 30,
                },
            )
        response = await self.session.get(url)
        data = await response.json()
        print(data)
        self.ts = data['ts']
        raw_updates = data.get('updates')
        update_list = []
        for update in raw_updates:
            update_list.append(
                Update(
                    type=update['type'],
                    object=UpdateObject(
                        message=UpdateMessage(
                            from_id=update['object']['message']['peer_id'],
                            text=update['object']['message']['text'],
                            id=update['object']['message']['id'],
                        )
                    ),
                )
            )
        await self.app.store.bots_manager.handle_updates(update_list)

    async def send_message(self, message: Message) -> None:
        url = self._build_query(
                self.VK_API,
                'messages.send',
                params={
                    'user_id': message.user_id,
                    'random_id': random.randint(1, 2**32),
                    'peer_id': f'-{self.app.config.bot.group_id}',
                    'message': message.text,
                    'access_token': self.app.config.bot.token,
                },
            )
        response = await self.session.get(url)
        data = await response.json()
        print(data)
