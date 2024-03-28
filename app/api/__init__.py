from fastapi import APIRouter
from .endpoints import cars, categories, parts

api_router = APIRouter()
api_router.include_router(cars.router, prefix="/cars", tags=["Cars"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(parts.router, prefix="/parts", tags=["Parts"])
