#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: app.py
@Author: Claude
@Software: PyCharm
@Desc: FastAPI Application - REST API for Gravix
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.api.routes import skills, mcp, chat
from app.utils.logger import logger

# Create FastAPI app
app = FastAPI(
    title="Gravix API",
    description="Skills, MCP, and Chat API for Gravix Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])
app.include_router(mcp.router, prefix="/api/mcp", tags=["MCP"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

# Mount static files for web interface
web_dir = Path(__file__).parent.parent.parent / "web" / "static"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Gravix API starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Gravix API shutting down...")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Gravix API",
        "version": "1.0.0",
        "docs": "/docs",
        "web_ui": "/static/index.html"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "gravix-api",
        "version": "1.0.0"
    }


# Serve web UI at /ui
@app.get("/ui", tags=["Web UI"])
async def web_ui():
    """Serve the web chat interface"""
    index_file = web_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"error": "Web UI not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
