from __future__ import annotations

import asyncio
import logging
import aio_pika
from fastapi import FastAPI
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "notification-service"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    LOG_LEVEL: str = "INFO"


settings = Settings()
logging.basicConfig(level=settings.LOG_LEVEL)
log = logging.getLogger(settings.APP_NAME)

async def start_rabbitmq_consumer():
    while True:
        try:
            connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            async with connection:
                channel = await connection.channel()
                queue = await channel.declare_queue("orders.created", durable=True)
                log.info("RabbitMQ consumer connected, waiting for messages")

                async def on_message(message: aio_pika.IncomingMessage):
                    async with message.process():
                        body = message.body.decode(errors="replace")
                        log.info("RabbitMQ orders.created: %s", body)

                await queue.consume(on_message)
                await asyncio.Future()
        except Exception as e:
            log.error("RabbitMQ consumer error: %s (retry in 2s)", e)
            await asyncio.sleep(2)


app = FastAPI(title=settings.APP_NAME)


@app.on_event("startup")
async def startup():
    asyncio.create_task(start_rabbitmq_consumer())


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.APP_NAME}