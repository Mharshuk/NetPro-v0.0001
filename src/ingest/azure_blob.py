from __future__ import annotations
import asyncio
import gzip
import json
from typing import AsyncIterator
from azure.storage.blob import BlobServiceClient
from ..normalise import normalise

async def ingest(cfg) -> AsyncIterator[dict]:
    if not cfg.azure_connstr:
        return
    client = BlobServiceClient.from_connection_string(cfg.azure_connstr)
    container = client.get_container_client('$logs')
    loop = asyncio.get_running_loop()
    blobs = await loop.run_in_executor(None, lambda: list(container.list_blobs()))
    for blob in blobs:
        downloader = await loop.run_in_executor(None, container.download_blob, blob)
        data = await loop.run_in_executor(None, downloader.readall)
        if blob.name.endswith('.gz'):
            data = gzip.decompress(data)
        lines = data.splitlines()
        for line in lines:
            yield normalise(line.decode())
