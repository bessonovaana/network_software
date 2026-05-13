# ===== main.py (ПОЛНЫЙ ФАЙЛ) =====
import logging
import aio_pika
from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, APIRouter, Depends, Body
from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from pydantic_settings import BaseSettings

# ----- Конфиг -----
class Settings(BaseSettings):
    APP_NAME: str = "order-service"
    DB_URL: str = "postgresql+asyncpg://orders:secret@postgres-orders:5432/orders_db"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    LOG_LEVEL: str = "INFO"
    class Config:
        env_file = ".env"

settings = Settings()
logging.basicConfig(level=settings.LOG_LEVEL)
log = logging.getLogger(settings.APP_NAME)

# ----- БД -----
engine = create_async_engine(settings.DB_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    item = Column(String, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String, default="created")

async def get_db():
    async with SessionLocal() as session:
        yield session

# ----- RabbitMQ -----
async def publish_order_created(order_id: int, user_id: int, total: float):
    try:
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            await channel.declare_queue("orders.created", durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=f"{order_id}:{user_id}:{total}".encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key="orders.created"
            )
        log.info(f"Event published for order {order_id}")
    except Exception as e:
        log.error(f"Failed to publish event: {e}")

# ----- Роуты -----
router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/")
async def create_order(
    user_id: int = Body(..., embed=True),
    item: str = Body(..., embed=True),
    total: float = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    order = Order(user_id=user_id, item=item, total=total, status="created")
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    # Fire-and-forget: не ждём отправки в очередь
    asyncio.create_task(publish_order_created(order.id, order.user_id, order.total))
    
    return {"id": order.id, "status": order.status}

# ----- Приложение -----
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: создать таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: закрыть БД
    await engine.dispose()

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.APP_NAME}