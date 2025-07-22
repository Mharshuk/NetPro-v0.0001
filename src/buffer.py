from __future__ import annotations
import os
import asyncio
from diskqueue import DiskQueue

class Buffer:
    def __init__(self, path: str):
        os.makedirs(path, exist_ok=True)
        self.q = DiskQueue(path)

    async def put(self, item: dict):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.q.put, item)

    async def get(self) -> dict | None:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.q.get_nowait)

    async def task_done(self):
        pass
