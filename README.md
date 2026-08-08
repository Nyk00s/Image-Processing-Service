# Image Processing Service

Asynchronous image-processing service: a REST API with JWT authentication, file uploads to
S3-compatible storage, and image transformations executed asynchronously through a task queue.

---

## Features

- JWT authentication (access + refresh tokens, session invalidation via `token_version`)
- File upload with size and format validation (PNG, JPEG, WEBP)
- 8 transformation operations: resize, crop, rotate, flip, grayscale, sepia, watermark, format
- Asynchronous task processing with status polling
- Presigned URLs for downloading results (downloads bypass the API and go straight to storage)
- Upload rate limiting (sliding window)
- Paginated listing of pictures and tasks

---

## Stack

- **API:** FastAPI, Pydantic v2
- **Database:** PostgreSQL, SQLAlchemy 2.0, Alembic
- **Image processing:** Pillow, NumPy
- **Task queue:** Celery + Redis
- **Storage:** MinIO (S3-compatible API), boto3
- **Authentication:** pyjwt (HS256), pwdlib[bcrypt]
- **Tests:** pytest
- **Deployment:** Docker Compose

---

## Quick start

```bash
git clone git@github.com:Nyk00s/Image-Processing-Service.git
cd Image-Processing-Service

cp .env.example .env    # fill in JWT_SECRET and S3_SECRET_KEY with generated hex tokens (see below)

docker compose up -d --build
```

Once the stack is running(make sure to change ports if you change them in .env):

- **API + Swagger docs:** http://localhost:8000/docs
- **MinIO console:** http://localhost:9001

Database migrations run automatically when the `api` container starts.

> Generate `JWT_SECRET` and `S3_SECRET_KEY` with:
> `python -c "import secrets; print(secrets.token_hex(32))"`

---

## Endpoints

### Auth
| Method | Path             | Description                                   | Auth |
|--------|------------------|-----------------------------------------------|------|
| POST   | `/auth/register` | Register a user                               | —    |
| POST   | `/auth/login`    | Log in; returns access and refresh tokens     | —    |
| GET    | `/auth/me`       | Return the current authenticated user         | ✓    |
| POST   | `/auth/refresh`  | Rotate access and refresh tokens              | —    |
| POST   | `/auth/logout`   | Log out (invalidates tokens)                  | ✓    |

### Pictures
| Method | Path                     | Description                              | Auth |
|--------|--------------------------|------------------------------------------|------|
| POST   | `/pictures`              | Upload a file                            | ✓    |
| GET    | `/pictures`              | List pictures (paginated)                | ✓    |
| GET    | `/pictures/{id}`         | Picture details with presigned URL       | ✓    |
| POST   | `/pictures/{id}/tasks`   | Submit an asynchronous transformation    | ✓    |

### Tasks
| Method | Path           | Description                          | Auth |
|--------|----------------|--------------------------------------|------|
| GET    | `/tasks`       | List tasks (paginated)               | ✓    |
| GET    | `/tasks/{id}`  | Task status and result presigned URL | ✓    |

---

## Operations

`POST /pictures/{id}/tasks` accepts a list of operations, applied **in order**:

**crop** — cuts a rectangle out of the picture
```json
{ "operations": [{ "type": "crop", "x": 0, "y": 0, "width": 100, "height": 100 }] }
```

**flip** — mirrors the picture horizontally or vertically
```json
{ "operations": [{ "type": "flip", "direction": "horizontal" }] }
```
> `direction` accepts: `horizontal`, `vertical`

**format** — changes the output format
```json
{ "operations": [{ "type": "format", "target": "jpeg" }] }
```
> `target` accepts: `jpeg`, `png`, `webp`

**grayscale** — converts the picture to grayscale
```json
{ "operations": [{ "type": "grayscale" }] }
```

**resize** — resizes the picture
```json
{ "operations": [{ "type": "resize", "width": 500, "height": 500 }] }
```

**rotate** — rotates the picture by the given angle (degrees)
```json
{ "operations": [{ "type": "rotate", "angle": 30 }] }
```

**sepia** — applies a sepia tone
```json
{ "operations": [{ "type": "sepia" }] }
```

**watermark** — draws a text watermark onto the picture
```json
{
  "operations": [
    {
      "type": "watermark",
      "text": "sometext",
      "position": "center",
      "size": 30,
      "opacity": 255,
      "color": [255, 255, 0]
    }
  ]
}
```
> `position` accepts: `top-left`, `top-right`, `bottom-left`, `bottom-right`, `center`

Operations can be combined, and **order matters** (e.g. resize before rotate differs from
rotate before resize):
```json
{
  "operations": [
    { "type": "resize", "width": 800, "height": 600 },
    { "type": "grayscale" },
    { "type": "format", "target": "webp" }
  ]
}
```

---

## Architecture

```
Client ──HTTP──> API (FastAPI)
                  │  router → service → repository → PostgreSQL
                  │  upload/download ──> MinIO (S3)
                  │  enqueue task ─────> Redis (broker)
                  ▼
              Worker (Celery) ──reads task──> processes (Pillow) ──> MinIO
                  │
                  └── updates task status in PostgreSQL
```

The API is a thin HTTP layer: routers delegate to services (business logic), which use
repositories (data access). Image transformations run in a separate Celery worker process,
so long-running work never blocks the API.

---

## Design decisions

### Asynchronous processing
Processing images synchronously would block the API whenever a transformation takes a long
time, and a few concurrent requests could exhaust the server. Instead, the client submits a
request, the API creates a task, persists it, and enqueues it on the message broker, returning
immediately. The client polls the API for the task's status.

### Task status in the database instead of Celery's result backend
The service tracks task state in its own `Task` table rather than relying on Celery's result
backend. This gives full control over statuses, error messages, and the result key, keeps the
state queryable through a plain `GET /tasks/{id}`, and avoids coupling the API to Celery.

### Presigned URLs for downloads
`GET /pictures/{id}` and `GET /tasks/{id}` return a presigned URL that lets the client download
the file **directly from storage**, bypassing the API. This keeps the API from proxying large
binary payloads; authorization happens when the URL is issued (the endpoint is protected and
checks ownership), and the short-lived URL acts as a time-limited download token.

### Sliding window rate limiting
I chose a sliding window over a fixed window because a fixed window allows up to twice the limit
around the window boundary (a burst at the end of one window plus a burst at the start of the
next). A sliding window counts requests over the last N seconds from *now*, removing that gap.

### Token invalidation via `token_version`
JWTs are stateless, so a token cannot simply be revoked. Each user has a `token_version` counter
stored in the database and embedded in the token; it is compared on every request. Logout
increments the counter, which invalidates all previously issued tokens for that user.

### Layered architecture and dependency injection
The project is split into router → service → repository layers. This separates concerns, makes
the codebase easier to extend and to swap dependencies, and (because dependencies are injected)
makes the service and endpoint logic testable with in-memory fakes instead of a real database and
storage.

---

## Tests

To run the tests locally:

```bash
python -m venv .venv
.\.venv\Scripts\activate      # Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
```

Coverage on three levels:

- **Unit tests** — individual image operations and multi-operation chains (`process_image`),
  as pure functions with no external dependencies
- **Service tests** — business logic exercised with *fakes* (fake repository/storage) instead of
  a real database or object storage, including ownership checks that guard against IDOR
- **Endpoint tests** — full HTTP requests via `TestClient`, with `dependency_overrides` swapping
  dependencies for fakes

### Why fakes over mocks?
A fake is a small working implementation of a dependency (e.g. a repository backed by a list).
Fakes read like real code and survive refactors better than mocks, which assert on how a
dependency is called rather than on the resulting behavior.

---

## Known limitations

- Rate limiting uses a Redis pipeline rather than a Lua script: a rejected request is still
  added to the window, which slightly tightens the effective limit. A Lua script would make the
  check-and-add atomic.
- Offset-based pagination is simple but does not scale to very large datasets as well as
  cursor/keyset pagination would.
- No protection against cache stampede.
- Login does not use a constant-time path for unknown emails, so an attacker could in principle
  infer whether an email exists from response timing. Responses themselves are identical
  (same status and message) to prevent user enumeration by content.
- Tokens are not encrypted at rest on the client — protecting stored tokens is the frontend's
  responsibility.

---

## What can be added

- **Image watermark** — currently only text watermarks are supported; allow overlaying another
  uploaded image as a watermark.
- **Idempotent / deduplicated results** — derive the result key from a hash of the operations so
  repeating the same transformation reuses the existing output instead of recomputing it.
- **Per-user quotas / storage limits** — cap total storage or number of images per user.
- **More transformations** — blur, brightness/contrast, or arbitrary-angle crop.
- **Lua-based rate limiter** — replace the pipeline with an atomic Lua script (see Known
  limitations).