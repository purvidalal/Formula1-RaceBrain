"""
RaceBrain - Main Application
Production-quality F1 Strategy Game Server
"""

import sys
import os

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.routes import game_routes, api_routes, page_routes
from app.services.recommendation_service import recommendation_service
from config.settings import FRONTEND_DIR

# ============================================================
# CREATE APP
# ============================================================

app = FastAPI(
    title="RaceBrain API",
    debug=True,  # Show full errors
    description="Multi-Agent Deep RL F1 Strategy Game",
    version="2.0.0"
)

# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# LOAD AI AGENTS ON STARTUP
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🤖 Initializing services...")
    # Agents are loaded automatically in RecommendationService.__init__()
    print("✅ Services ready")

# ============================================================
# MOUNT ROUTES
# ============================================================

# Game API
app.include_router(game_routes.router)

# General API
app.include_router(api_routes.router)

# HTML pages
app.include_router(page_routes.router)

# ============================================================
# STATIC FILES
# ============================================================

# Mount frontend directory for static assets
if os.path.exists(FRONTEND_DIR):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🏎️  RACEBRAIN PRODUCTION SERVER")
    print("="*60)
    print("📍 URL: http://localhost:8000")
    print("📍 Game: http://localhost:8000/game")
    print("📍 Test: http://localhost:8000/test")
    print("📍 Docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
