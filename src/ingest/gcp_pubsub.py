from __future__ import annotations
import asyncio
from typing import AsyncIterator
from google.cloud import pubsub_v1
from ..normalise import normalise

async def ingest(cfg) -> AsyncIterator[dict]:
    if not cfg.gcp_project:
        return
    subscriber = pubsub_v1.SubscriberClient()
    sub_path = subscriber.subscription_path(cfg.gcp_project, cfg.gcp_sub_id)
    q = asyncio.Queue()

    def callback(msg):
        q.put_nowait(msg)

    future = subscriber.subscribe(sub_path, callback=callback)
    try:
        while True:
            msg = await q.get()
            yield normalise(msg.data.decode())
            msg.ack()
    finally:
        future.cancel()
