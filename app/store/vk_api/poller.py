from asyncio import Task, create_task
from typing import Optional

# from app.store import Store


class Poller:
    def __init__(self, store):
        self.store = store
        self.is_running = False
        self.polling_task: Optional[Task] = None

    async def start(self):
        self.is_running = True
        self.polling_task = create_task(self.poll())

    async def stop(self):
        self.is_running = False
        await self.polling_task

    async def poll(self):
        while self.is_running:
            await self.store.vk_api.poll()
