# URL Shortener

A simple, production-deployed URL shortener built with FastAPI and SQLite. Submit a long URL, get back a short one — with optional expiration and click analytics.

**Live demo:** https://<your-app>.onrender.com
*(Note: hosted on Render's free tier — the app spins down after ~15 minutes of inactivity, so the first request after idle time may take 30–60 seconds to respond.)*

## Features

- Shorten any valid URL into a compact, random 6-character code
- Redirect from the short link to the original URL
- Optional per-link expiration (`expires_in_days`) — expired links return a `410 Gone` instead of redirecting
- Click tracking — every redirect increments a counter
- A `/stats/{code}` endpoint to view a link's metadata and click count without triggering a redirect
- Request validation via Pydantic (`HttpUrl`, `EmailStr`) — malformed URLs or emails are rejected automatically with a `422` response
- Interactive API docs auto-generated at `/docs`

## Tech Stack

- **Python 3** / **FastAPI** — web framework and routing
- **Pydantic** — request/response validation
- **SQLite** — persistence (via Python's built-in `sqlite3` module)
- **Uvicorn** — ASGI server
- **Render** — hosting (free tier)

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check — returns `{"status": "ok"}` |
| `POST` | `/shorten` | Create a short link. Body: `{"original_url": str, "creator_email": str, "expires_in_days": int (optional)}` |
| `GET` | `/{code}` | Redirects to the original URL. Returns `404` if not found, `410` if expired |
| `GET` | `/stats/{code}` | Returns link metadata: original URL, click count, created/expiry timestamps |

Full interactive documentation available at `/docs`.

## Design Decisions

**Short-code generation — random string.** Considered three approaches: random strings, an incrementing counter with base62 encoding, and hashing the input URL. Went with random generation (6 characters, letters + digits) for simplicity and unpredictability, at the cost of needing a collision check on each creation — a deliberate, documented tradeoff rather than a default.

**Persistence — SQLite.** Started with an in-memory dictionary to build and test the core create/redirect logic quickly, then swapped in SQLite behind the same three operations (`save_link`, `get_link`, `increment_clicks`) without changing any route logic. Chosen for zero external setup — it's a single file, no separate database server required, appropriate for this project's scale.

**Validation — Pydantic's `HttpUrl` and `EmailStr`.** Rather than writing manual validation logic, these types validate incoming data automatically at the schema level, rejecting malformed input before it reaches any application code.

**Expired vs. not-found — distinct status codes.** Expired links return `410 Gone` rather than reusing `404 Not Found`, since the link existed but is no longer valid — a more precise and honest signal to the client than lumping both failure cases together.

## Known Limitations (v1)

These are deliberate scope decisions, not oversights:

- No user accounts or authentication — anyone can create a link, and `creator_email` is just a label, not a verified identity
- No custom aliases — codes are always randomly generated
- No rate limiting on link creation
- No frontend UI — API only
- **Database resets on redeploy/restart.** Render's free tier uses an ephemeral filesystem, and persistent disks require a paid plan. For a portfolio demo, this tradeoff was accepted rather than adding hosting cost or complexity.
- Short codes aren't filtered for ambiguous characters (e.g., `0`/`O`, `1`/`l`)

## Running Locally

```bash
git clone <your-repo-url>
cd url-shortener
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000/docs` to try it out.

## Possible Future Improvements

- Rate limiting on the `/shorten` endpoint
- Custom aliases
- Move to Postgres for real concurrent-write support
- A minimal frontend