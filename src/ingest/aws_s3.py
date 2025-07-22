from __future__ import annotations
import asyncio
import gzip
import json
from typing import AsyncIterator
import boto3
from ..normalise import normalise

async def ingest(cfg) -> AsyncIterator[dict]:
    if not cfg.aws_s3_bucket:
        return
    s3 = boto3.client('s3', region_name=cfg.aws_region,
                      aws_access_key_id=cfg.aws_access_key,
                      aws_secret_access_key=cfg.aws_secret_key)
    # Simplified: list objects and yield
    loop = asyncio.get_running_loop()
    objs = await loop.run_in_executor(None, lambda: s3.list_objects_v2(Bucket=cfg.aws_s3_bucket).get('Contents', []))
    for obj in objs:
        key = obj['Key']
        body = await loop.run_in_executor(None, lambda: s3.get_object(Bucket=cfg.aws_s3_bucket, Key=key)['Body'].read())
        if key.endswith('.gz'):
            body = gzip.decompress(body)
        lines = body.splitlines()
        for line in lines:
            yield normalise(line.decode())
