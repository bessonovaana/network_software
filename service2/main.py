from fastapi import FastAPI
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Service 2", description="Второй микросервис")

@app.get("/")
async def root():
    logger.info("Request: GET /")
    return "Welcome to Service 2!",
     