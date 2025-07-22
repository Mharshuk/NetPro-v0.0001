from __future__ import annotations
import asyncio
from typing import Any
from kafka import KafkaProducer
import json
from .config import Config

class KafkaClient:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        params = {
            "bootstrap_servers": cfg.kafka_bootstrap,
            "value_serializer": lambda v: json.dumps(v).encode(),
            "acks": "all",
            "linger_ms": 50,
        }
        if cfg.kafka_ssl_cert:
            params.update({
                "security_protocol": "SSL",
                "ssl_cafile": cfg.kafka_ssl_ca,
                "ssl_certfile": cfg.kafka_ssl_cert,
                "ssl_keyfile": cfg.kafka_ssl_key,
            })
        self.producer = KafkaProducer(**params)

    async def send(self, record: dict[str, Any]):
        loop = asyncio.get_running_loop()
        key = str(record.get("dst_port", record.get("protocol", "0"))).encode()
        await loop.run_in_executor(None, self.producer.send, self.cfg.kafka_topic, record, key)

    async def flush(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.producer.flush)
