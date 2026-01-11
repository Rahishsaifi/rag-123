"""
API v1 router aggregation.
"""
from fastapi import APIRouter
from app.api.v1.routes import upload, chat

api_router = APIRouter()

api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

