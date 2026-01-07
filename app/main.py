from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.v1.endpoints import router as api_v1_router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title=settings.PROJECT_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

# API Routes
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

# Serve Static Files
app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")

@app.get("/")
@app.get("/stock/{code}")
@app.get("/portfolio")
def read_root(code: str = None):
    return FileResponse(os.path.join(frontend_path, "index.html"))
