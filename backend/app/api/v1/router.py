"""Router v1 — Agrupa todos os endpoints da API versao 1."""

from fastapi import APIRouter
from app.api.v1.endpoints import contracts

router = APIRouter()
router.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
