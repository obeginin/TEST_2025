from fastapi import APIRouter
from my_wallet_service.app.api.v1.wallets import wallets_router

'''automatic connection router'''
api_router = APIRouter()
api_router.include_router(wallets_router, prefix="/wallets", tags=["Wallets"])