from pydantic import BaseModel, Field, validator
from typing import Optional

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название товара")
    description: Optional[str] = Field(None, max_length=500, description="Описание товара")
    price: float = Field(..., gt=0, description="Цена товара")
    quantity: int = Field(0, ge=0, description="Количество на складе")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Название товара не может быть пустым')
        return v.strip()
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Цена должна быть положительным числом')
        return round(v, 2)

class Product(ProductCreate):
    id: int = Field(..., description="Уникальный идентификатор товара")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Ноутбук",
                "description": "Мощный игровой ноутбук",
                "price": 999.99,
                "quantity": 10
            }
        }