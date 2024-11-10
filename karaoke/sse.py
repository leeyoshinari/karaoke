#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import asyncio
import traceback
from typing import List
from settings import logger


class SSE:
    def __init__(self):
        self.clients: List[asyncio.StreamWriter] = []
        self.queue: asyncio.Queue = asyncio.Queue()

    async def event_processor(self):
        while True:
            data = await self.queue.get()
            for client in self.clients[:]:
                try:
                    client.write(data.encode('utf-8'))
                    await client.drain()
                except:
                    self.clients.remove(client)
                    logger.error(traceback.format_exc())
