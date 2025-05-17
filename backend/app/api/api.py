from fastapi import APIRouter

from ..api.endpoints import datasets, chat, database_info

api_router = APIRouter()

api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(database_info.router, prefix="/database-info", tags=["database-info"])
