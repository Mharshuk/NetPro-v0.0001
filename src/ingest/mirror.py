from __future__ import annotations
import asyncio
from typing import AsyncIterator
from aioquic.asyncio import serve
from aioquic.quic.configuration import QuicConfiguration
from ..normalise import normalise

async def ingest(cfg) -> AsyncIterator[dict]:
    if not (cfg.mirror_tls_cert and cfg.mirror_tls_key):
        return
    q = asyncio.Queue()

    async def handler(stream_reader, stream_writer):
        data = await stream_reader.read()
        for line in data.splitlines():
            q.put_nowait(normalise(line.decode()))
        stream_writer.close()

    conf = QuicConfiguration(is_client=False)
    conf.load_cert_chain(cfg.mirror_tls_cert, cfg.mirror_tls_key)
    server = await serve("0.0.0.0", cfg.mirror_port, configuration=conf, stream_handler=handler)
    try:
        while True:
            item = await q.get()
            yield item
    finally:
        server.close()
        await server.wait_closed()
