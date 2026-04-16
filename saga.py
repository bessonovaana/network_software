from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from typing import Optional

app = FastAPI()

# Включаем CORS для работы с HTML страницы
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)


orders = {}

class OrderCreate(BaseModel):
    user_id: str
    amount: float

class OrderTransition(BaseModel):
    event: str

def next_state(state: str, event: str) -> str:
    
    transitions = {
        ('NEW', 'CREATE'): 'NEW',
        ('NEW', 'RESERVE_OK'): 'NEW',
        ('NEW', 'RESERVE_FAIL'): 'CANCELLED',
        ('NEW', 'PAY_OK'): 'PAID',
        ('NEW', 'PAY_FAIL'): 'CANCELLED',
        ('PAID', 'PAY_OK'): 'DONE',
        ('PAID', 'PAY_FAIL'): 'CANCELLED',
    }
    return transitions.get((state, event), state)

@app.get("/")
async def root():
    
    return {
        "message": "Saga API работает!",
        "endpoints": [
            "POST /orders - создать заказ",
            "GET /orders/{order_id} - получить заказ",
            "POST /orders/{order_id}/transition - применить событие",
            "GET /orders - список всех заказов"
        ]
    }

@app.post("/orders")
async def create_order(order: OrderCreate):
    order_id = str(uuid.uuid4())[:8]
    
    orders[order_id] = {
        "id": order_id,
        "user_id": order.user_id,
        "amount": order.amount,
        "status": "NEW",
        "history": [{"event": "CREATE", "state": "NEW"}]
    }
    
    print(f"Создан заказ: {order_id} для пользователя {order.user_id}")
    return orders[order_id]

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Получение информации о заказе"""
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return orders[order_id]

@app.post("/orders/{order_id}/transition")
async def transition_order(order_id: str, transition: OrderTransition):
    """Применение события к заказу"""
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    order = orders[order_id]
    old_status = order["status"]
    event = transition.event
    
  
    new_status = next_state(old_status, event)
    

    order["status"] = new_status
    if "history" not in order:
        order["history"] = []
    order["history"].append({"event": event, "from": old_status, "to": new_status})
    
    print(f" Заказ {order_id}: {old_status} --({event})--> {new_status}")
    
    return {
        "order_id": order_id,
        "previous_state": old_status,
        "current_state": new_status,
        "event": event
    }

@app.get("/orders")
async def list_orders():
    """Список всех заказов"""
    return {"orders": list(orders.values()), "count": len(orders)}

@app.delete("/orders/{order_id}")
async def delete_order(order_id: str):
    """Удаление заказа (для очистки)"""
    if order_id in orders:
        del orders[order_id]
        return {"message": f"Заказ {order_id} удален"}
    raise HTTPException(status_code=404, detail="Заказ не найден")

@app.options("/{path:path}")
async def options_handler(path: str):
    """Обработка OPTIONS запросов"""
    return {"allowed": True}