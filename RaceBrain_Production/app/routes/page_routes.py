"""
Page Routes
HTML page serving
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import os
from config.settings import FRONTEND_DIR

router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
async def home():
    """Main game page"""
    try:
        game_html = os.path.join(FRONTEND_DIR, "game.html")
        with open(game_html, "r") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Game page not found")


@router.get("/game", response_class=HTMLResponse)
async def game():
    """Game page (same as home)"""
    try:
        game_html = os.path.join(FRONTEND_DIR, "game.html")
        with open(game_html, "r") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Game page not found")


@router.get("/test", response_class=HTMLResponse)
async def test():
    """Multi-agent test dashboard"""
    try:
        test_html = os.path.join(FRONTEND_DIR, "test.html")
        with open(test_html, "r") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Test page not found")
