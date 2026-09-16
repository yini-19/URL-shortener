import random
import string
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl, EmailStr
import os
import storage

app = FastAPI()

class ShortenRequest(BaseModel):
    """Request body for creating a short link.
    Validation (URL format, email format) is handled automatically by Pydantic's HttpUrl and EmailStr types."""
    original_url: HttpUrl
    creator_email: EmailStr

class ShortenResponse(BaseModel):
    short_url: str

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

    storage.save_link(code, str(request.original_url), request.creator_email)

    short_url = f"{BASE_URL}/{code}"
    return ShortenResponse(short_url=short_url)

@app.get("/{code}")
def redirect_to_url(code: str):
    record = storage.get_link(code)
    if record is None:
        raise HTTPException(status_code=404, detail="short link not found")
    
    storage.increment_clicks(code)
    
    return RedirectResponse(url=record["original_url"])
