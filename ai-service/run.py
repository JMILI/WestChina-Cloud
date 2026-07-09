#!/usr/bin/env python3
"""Entry point: uvicorn app.main:app"""
import os

import uvicorn

from app.config import settings

if __name__ == "__main__":
    workers = int(os.getenv("AI_WORKERS", "1"))
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        workers=workers,
    )
