import random
import string
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl, EmailStr
from fastapi.middleware.cors import CORSMiddleware


import os
import storage
from typing import Optional
from datetime import timedelta


app = FastAPI()

class ShortenRequest(BaseModel):
    """Request body for creating a short link.
    Validation (URL format, email format) is handled automatically by Pydantic's HttpUrl and EmailStr types."""
    original_url: HttpUrl
    creator_email: EmailStr
    expires_in_days: Optional[int]= None

class ShortenResponse(BaseModel):
    short_url: str

class StatsResponse(BaseModel):
    code: str
    original_url: str
    clicks: int
    created_at: str
    expires_at: Optional[str] = None

storage.init_db()

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")

def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/shorten", response_model=ShortenResponse)
def create_short_link(request: ShortenRequest):
    code = generate_code()
    while storage.code_exist(code):
        code = generate_code()

    expires_at = None
    if request.expires_in_days is not None:
        expires_at = datetime.now(timezone.utc) + timedelta(days=request.expires_in_days)

    storage.save_link(code, str(request.original_url), request.creator_email, expires_at)

    short_url = f"{BASE_URL}/{code}"
    return ShortenResponse(short_url=short_url)

@app.get("/stats/{code}", response_model=StatsResponse)
def get_link_stats(code: str):
    record = storage.get_link(code)
    if record is None:
        raise HTTPException(status_code=404, detail="Short link not found")

    return StatsResponse(
        code=code,
        original_url=record["original_url"],
        clicks=record["clicks"],
        created_at=record["created_at"],
        expires_at=record["expires_at"],
    )

@app.get("/{code}")
def redirect_to_url(code: str):
    record = storage.get_link(code)
    if record is None:
        raise HTTPException(status_code=404, detail="Short link not found")

    if record["expires_at"] is not None:
        expires_at = datetime.fromisoformat(record["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=410, detail="This link has expired")

    storage.increment_clicks(code)

    return RedirectResponse(url=record["original_url"])



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)