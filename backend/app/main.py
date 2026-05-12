"""Main — Entrypoint FastAPI do backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.config import LLM_MODEL
from app.schemas.contracts import HealthResponse

app = FastAPI(
    title="Comparador de Contratos API",
    description="API REST para comparacao inteligente de contratos usando LLM.",
    version="1.0.0",
)

# CORS — permite que o frontend (Streamlit) acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check da aplicacao. Retorna status e modelo configurado."""
    return HealthResponse(status="ok", model=LLM_MODEL)


@app.get("/")
async def root():
    return {"message": "Comparador de Contratos API", "docs": "/docs"}
