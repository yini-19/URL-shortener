import random
import string
from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel

from fastapi import HTTPException
from fastapi.responses import RedirectResponse

app = FastAPI()

class ShortenRequest(BaseModel):
    original_url: str
    creator_email: str

class ShortenResponse(BaseModel):
    short_url: str

storage = {}
BASE_URL = "http://127.0.0.1:8000"


def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/shorten", response_model=ShortenResponse)
def create_short_link(request: ShortenRequest):
    code = generate_code()
    while code in storage:
        code = generate_code()

    storage[code] = {
        "original_url": request.original_url,
        "creator_email": request.creator_email,
        "created_at": datetime.now(timezone.utc),
        "clicks": 0,
    }

    short_url = f"{BASE_URL}/{code}"
    return ShortenResponse(short_url=short_url)

@app.get("/{code}")
def redirect_to_url(code: str):
    record = storage.get(code)
    if record is None:
        raise HTTPException(status_code=404, detail="short link not found")
    
    record["clicks"] += 1
    print(storage)
    return RedirectResponse(url=record["original_url"])