# DummyJSON — REST API Test Framework (JWT Auth)

Automated API test suite for [DummyJSON](https://dummyjson.com/),
built with **Python + pytest** as part of an AQA home test.

> DummyJSON is a free public REST API with built-in JWT authentication.
> No registration required — test credentials are provided out of the box.

---

## 🔑 Auth Flow

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

## 📁 Project Structure

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

## 🔍 Validation Strategy

| Validation | Used where | Why |
|------------|-----------|-----|
| **Status code** | All tests | Primary HTTP contract — wrong code = broken endpoint |
| **`assert_login_response` schema** | TC-01b | Catches silent field removal that would break all downstream token usage |
| **`assert_token_is_jwt`** | TC-01c/d, TC-03b/c | JWT structure + `exp` claim check — catches malformed tokens before they silently fail elsewhere |
| **`assert_tokens_are_different`** | TC-03d | Proves the refresh endpoint actually issues NEW tokens, not echoes the old one |
| **Follow-up request with refreshed token** | TC-03e | The only way to prove a new token actually works — not just structurally valid |
| **`password` field absent** | TC-02c | Security check — password exposure is a critical bug |
| **`parametrize` on bad credentials** | TC-01i | 4 invalid combos in 1 function, zero duplication |
| **`parametrize` on product categories** | TC-04g | Proves the API accepts different product types, not a hardcoded fixture |
| **`isDeleted: true` check** | TC-04k | Confirms deletion was acknowledged — not just an empty 200 |
| **Auth guard on every method** | TC-02d/e, TC-04c/h/j/l | Every protected endpoint must reject unauthenticated requests consistently |

---

## 🚀 Running the Tests

```bash
# 1. Clone & install
git clone <your-repo-url>
cd rest-api-tests
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
