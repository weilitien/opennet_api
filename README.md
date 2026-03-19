# DummyJSON — REST API Test Framework (JWT Auth)

Automated API test suite for [DummyJSON](https://dummyjson.com/),
built with **Python + pytest** as part of an AQA home test.

> DummyJSON is a free public REST API with built-in JWT authentication.
> No registration required — test credentials are provided out of the box.

---

## Auth Flow

```
POST /auth/login  ──→  accessToken + refreshToken
         │
         ▼
GET  /auth/me          (Bearer accessToken)
GET  /auth/products    (Bearer accessToken)
POST /auth/products/add
PUT  /auth/products/{id}
DELETE /auth/products/{id}
         │
         ▼
POST /auth/refresh ──→  new accessToken + refreshToken
```

**Built-in credentials (no signup needed):**
- Username: `emilys`
- Password: `emilyspass`

---

## Project Structure

```
rest-api-tests/
├── conftest.py                    # Login once → share token session-wide
├── pytest.ini
├── requirements.txt
├── config/
│   └── settings.py                # Base URL, credentials, constants
├── clients/
│   └── dummyjson_client.py        # HTTP client (set_token / clear_token)
├── tests/
└── utils/
    └── validators.py              # Reusable assertion helpers
```

**Key design decisions:**
- Login runs **once per session** in `conftest.py` — no repeated logins per test
- `auth_client` fixture injects token automatically via `set_token()`
- `client` fixture is unauthenticated — used for 401 tests
- `PyJWT` decodes tokens structurally without re-verifying the server secret

---

## Running the Tests

```bash
# 1. Setup
git clone <your-repo-url>
cd rest-api-tests

python3 -m venv .venv

# macOS / Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt

# 2. Run everything (no token setup needed — credentials are built in)
pytest

# 3. Run a specific file
pytest tests/test_login.py -v
pytest tests/test_token_refresh.py -v
pytest tests/test_products.py -v

# 4. HTML report
pytest --html=report.html --self-contained-html
```
