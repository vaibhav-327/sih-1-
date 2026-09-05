import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.database import Base, engine, SessionLocal
from backend.models import Project, Contractor, Constituency, Transaction, Milestone, Alert, AuditLog, ModelRun
from backend.routes import (
    dashboard_router,
    projects_router,
    contractors_router,
    constituencies_router,
    alerts_router,
    map_router,
    insights_router,
    model_router,
    data_router
)

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("MPLAD_Sentinel")

# Create tables in SQLite if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MPLAD AI SENTINEL API",
    description="AI-Powered Detection of Anomalies, Fraud Risks & Inefficiencies in MPLAD Implementation",
    version="2.4.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend Vite/React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(dashboard_router)
app.include_router(projects_router)
app.include_router(contractors_router)
app.include_router(constituencies_router)
app.include_router(alerts_router)
app.include_router(map_router)
app.include_router(insights_router)
app.include_router(model_router)
app.include_router(data_router)

@app.get("/")
def root():
    return {
        "system": "MPLAD AI SENTINEL",
        "tagline": "AI-Powered Implementation Monitoring & Risk Intelligence for MPLADS",
        "version": "2.4.0",
        "philosophy": "CONNECT -> ANALYZE -> DETECT -> EXPLAIN -> INVESTIGATE",
        "status": "OPERATIONAL",
        "docs": "/docs",
        "active_mode": os.getenv("DATA_MODE", "synthetic")
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "engine": "FastAPI + scikit-learn Isolation Forest + NLP Cosine Similarity"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error on {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred in MPLAD AI Sentinel.", "error": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
