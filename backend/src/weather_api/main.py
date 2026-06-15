import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from weather_api.routers.chat import router as chat_router

app = FastAPI(title="Weather Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("weather_api.main:app", host="0.0.0.0", port=8001, reload=False)
