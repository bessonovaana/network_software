from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import List, Union
import logging
import os
from datetime import datetime
import traceback
from pydantic import BaseModel, Field

app = FastAPI(version="1.0.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# База данных в памяти (отдельная для каждого экземпляра)
db = []
current_id = 1

# Модели для orders сервиса
class OrderCreate(BaseModel):
    name: str
    priority: int

class Order(BaseModel):
    id: int
    name: str
    priority: int
    created_at: datetime = Field(default_factory=datetime.now)



@app.get("/")
async def root():
     return "This is sevise1"
@app.get("/health")
async def health_check():
        return {"status": "healthy", "service": "orders-svc-s04"}

@app.post("/orders", status_code=status.HTTP_201_CREATED, response_model=Order)
async def create_order(order: OrderCreate):
        global current_id, db
        logger.info(f"Received order data: {order.dict()}")
        
        new_order = Order(
            id=current_id,
            name=order.name,
            priority=order.priority
        )
        
        db.append(new_order)
        current_id += 1
        
        logger.info(f"Created order {new_order.id}")
        return new_order

@app.get("/orders", response_model=List[Order])
async def get_orders():
        return db

@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int):
        for order in db:
            if order.id == order_id:
                return order
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")

@app.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: int, updated_order: OrderCreate):
        for i, order in enumerate(db):
            if order.id == order_id:
                order_to_update = Order(
                    id=order_id,
                    name=updated_order.name,
                    priority=updated_order.priority,
                    created_at=order.created_at
                )
                db[i] = order_to_update
                return order_to_update
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")

@app.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int):
        for i, order in enumerate(db):
            if order.id == order_id:
                db.pop(i)
                return
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")



# Общие middleware и обработчики ошибок
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"Response status: {response.status_code} - Time: {process_time:.3f}s")
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "detail": "Ошибка валидации данных",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPError",
            "detail": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )