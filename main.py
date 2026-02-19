from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import List, Optional
from schemas import Product, ProductCreate
import logging
import os
from datetime import datetime
import traceback

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=os.getenv("APP_NAME", "Inventory Microservice"),
    description="Микросервис для управления товарами с полной обработкой исключений",
    version=os.getenv("APP_VERSION", "1.0.0")
)

# База данных в памяти
products_db = []
id_counter = 1

# Кастомные исключения
class ProductNotFoundException(Exception):
    def __init__(self, product_id: int):
        self.product_id = product_id
        self.message = f"Товар с ID {product_id} не найден"
        super().__init__(self.message)

class ProductAlreadyExistsException(Exception):
    def __init__(self, product_name: str):
        self.product_name = product_name
        self.message = f"Товар с названием '{product_name}' уже существует"
        super().__init__(self.message)

# Обработчики исключений
@app.exception_handler(ProductNotFoundException)
async def product_not_found_handler(request: Request, exc: ProductNotFoundException):
    logger.warning(f"Product not found: {exc.product_id}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "ProductNotFound",
            "detail": exc.message,
            "product_id": exc.product_id,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(ProductAlreadyExistsException)
async def product_already_exists_handler(request: Request, exc: ProductAlreadyExistsException):
    logger.warning(f"Product already exists: {exc.product_name}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "ProductAlreadyExists",
            "detail": exc.message,
            "product_name": exc.product_name,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "detail": exc.errors(),
            "body": exc.body,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "detail": "Внутренняя ошибка сервера",
            "timestamp": datetime.now().isoformat()
        }
    )

# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    start_time = datetime.now()
    
    try:
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Response: {response.status_code} - Time: {process_time:.3f}s")
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise

# Эндпоинты
@app.get("/", tags=["Root"])
async def root():
    return {
        "service": app.title,
        "version": app.version,
        "status": "running",
        "user": os.getenv("USER", "non-root"),
        "endpoints": {
            "create_product": "POST /products/",
            "get_products": "GET /products/",
            "get_product": "GET /products/{product_id}",
            "health": "GET /health",
            "stats": "GET /stats"
        }
    }

@app.post("/products/", response_model=Product, status_code=201, tags=["Products"])
async def create_product(product: ProductCreate):
    global id_counter
    
    # Проверка на дубликат
    existing_product = next(
        (p for p in products_db if p.name.lower() == product.name.lower()), 
        None
    )
    if existing_product:
        raise ProductAlreadyExistsException(product.name)
    
    # Проверка цены
    if product.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Цена должна быть положительным числом"
        )
    
    try:
        new_product = Product(
            id=id_counter, 
            **product.model_dump()
        )
        products_db.append(new_product)
        id_counter += 1
        
        logger.info(f"Product created: {new_product}")
        return new_product
    except Exception as e:
        logger.error(f"Failed to create product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось создать товар"
        )

@app.get("/products/", response_model=List[Product], tags=["Products"])
async def get_products(
    skip: int = 0, 
    limit: int = 100,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    try:
        products = products_db[skip:skip + limit]
        
        # Фильтрация по цене
        if min_price is not None:
            products = [p for p in products if p.price >= min_price]
        if max_price is not None:
            products = [p for p in products if p.price <= max_price]
        
        logger.info(f"Products retrieved: {len(products)} (filtered from {len(products_db)})")
        return products
    except Exception as e:
        logger.error(f"Failed to get products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось получить список товаров"
        )

@app.get("/products/{product_id}", response_model=Product, tags=["Products"])
async def get_product(product_id: int):
    try:
        product = next((p for p in products_db if p.id == product_id), None)
        if not product:
            raise ProductNotFoundException(product_id)
        
        logger.info(f"Product retrieved: {product}")
        return product
    except ProductNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to get product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось получить товар с ID {product_id}"
        )

@app.delete("/products/{product_id}", status_code=204, tags=["Products"])
async def delete_product(product_id: int):
    global products_db
    
    try:
        product_index = next(
            (i for i, p in enumerate(products_db) if p.id == product_id), 
            None
        )
        
        if product_index is None:
            raise ProductNotFoundException(product_id)
        
        deleted_product = products_db.pop(product_index)
        logger.info(f"Product deleted: {deleted_product}")
        
        return None
    except ProductNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось удалить товар с ID {product_id}"
        )

@app.get("/health", tags=["Monitoring"])
async def health_check():
    return {
        "status": "healthy",
        "user": os.getenv("USER", "appuser"),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/stats", tags=["Monitoring"])
async def get_stats():
    return {
        "total_products": len(products_db),
        "available_products": len([p for p in products_db if p.quantity > 0]),
        "out_of_stock": len([p for p in products_db if p.quantity == 0]),
        "average_price": sum(p.price for p in products_db) / len(products_db) if products_db else 0,
        "timestamp": datetime.now().isoformat()
    }