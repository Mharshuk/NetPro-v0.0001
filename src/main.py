import signal
import asyncio
from .config import Config
from .kafka import KafkaClient
from .buffer import Buffer
from .ingest import aws_s3, azure_blob, gcp_pubsub, mirror

async def producer_task(source, queue):
    async for record in source:
        await queue.put(record)

def start_source(cfg):
    tasks = []
    if cfg.aws_s3_bucket:
        tasks.append(aws_s3.ingest(cfg))
    if cfg.azure_connstr:
        tasks.append(azure_blob.ingest(cfg))
    if cfg.gcp_project:
        tasks.append(gcp_pubsub.ingest(cfg))
    if cfg.mirror_tls_cert and cfg.mirror_tls_key:
        tasks.append(mirror.ingest(cfg))
    return tasks

async def main():
    cfg = Config()
    kafka = KafkaClient(cfg)
    buffer = Buffer(cfg.buffer_dir)
    queue = asyncio.Queue(maxsize=10000)

    async def consume_queue():
        while True:
            record = await queue.get()
            try:
                await kafka.send(record)
            except Exception:
                await buffer.put(record)
            queue.task_done()

    producers = [asyncio.create_task(consume_queue())]
    for src in start_source(cfg):
        producers.append(asyncio.create_task(producer_task(src, queue)))

    stop = asyncio.Event()
    def shutdown():
        stop.set()
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, shutdown)
    await stop.wait()
    await queue.join()
    await kafka.flush()

if __name__ == "__main__":
    asyncio.run(main())
