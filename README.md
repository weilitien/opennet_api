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

## 🧪 Test Cases

| # | TC | Method | Endpoint | Type | Steps | Expected Result | Validation |
|---|-----|--------|----------|------|-------|-----------------|------------|
| 1 | TC-01a | POST | `/auth/login` | ✅ Login | Valid credentials | HTTP 200 | `assert_status_code(200)` |
| 2 | TC-01b | POST | `/auth/login` | ✅ Login | Valid credentials | Body has all required fields | `assert_login_response` (schema) |
| 3 | TC-01c | POST | `/auth/login` | ✅ Login | Valid credentials | `accessToken` is a valid JWT with `exp` claim | `assert_token_is_jwt` |
| 4 | TC-01d | POST | `/auth/login` | ✅ Login | Valid credentials | `refreshToken` is a valid JWT | `assert_token_is_jwt` |
| 5 | TC-01e | POST | `/auth/login` | ✅ Login | Valid credentials | `username` in response matches what we sent | `assert_field_equals("username")` |
| 6 | TC-01f | POST | `/auth/login` | ❌ Auth | Wrong password | HTTP 400 | `assert_status_code(400)` |
| 7 | TC-01g | POST | `/auth/login` | ❌ Auth | Wrong username | HTTP 400 | `assert_status_code(400)` |
| 8 | TC-01h | POST | `/auth/login` | ❌ Auth | Empty credentials | HTTP 400 | `assert_status_code(400)` |
| 9 | TC-01i×4 | POST | `/auth/login` | ❌ Auth | 4 bad-credential combos | HTTP 400 for all | `parametrize` |
| 10 | TC-02a | GET | `/auth/me` | ✅ Protected | Valid token | HTTP 200 | `assert_status_code(200)` |
| 11 | TC-02b | GET | `/auth/me` | ✅ Protected | Valid token | `username` matches login account | `assert_field_equals("username")` |
| 12 | TC-02c | GET | `/auth/me` | ✅ Protected | Valid token | No `password` field in response | `"password" not in data` |
| 13 | TC-02d | GET | `/auth/me` | ❌ Auth | No token | HTTP 401 | `assert_unauthorised` |
| 14 | TC-02e | GET | `/auth/me` | ❌ Auth | Fake/garbage JWT | HTTP 401 | `assert_unauthorised` |
| 15 | TC-03a | POST | `/auth/refresh` | ✅ Refresh | Valid refreshToken | HTTP 200 | `assert_status_code(200)` |
| 16 | TC-03b | POST | `/auth/refresh` | ✅ Refresh | Valid refreshToken | New `accessToken` is valid JWT | `assert_token_is_jwt` |
| 17 | TC-03c | POST | `/auth/refresh` | ✅ Refresh | Valid refreshToken | New `refreshToken` is valid JWT | `assert_token_is_jwt` |
| 18 | TC-03d | POST | `/auth/refresh` | ✅ Refresh | Valid refreshToken | New `accessToken` ≠ original | `assert_tokens_are_different` |
| 19 | TC-03e | POST | `/auth/refresh` | ✅ Refresh | Use refreshed token on `/auth/me` | HTTP 200 — token is usable | `assert_status_code(200)` |
| 20 | TC-03f | POST | `/auth/refresh` | ❌ Refresh | Fake refreshToken | HTTP 401 | `assert_unauthorised` |
| 21 | TC-04a | GET | `/auth/products` | ✅ CRUD | Valid token | HTTP 200 + valid schema list | `assert_all_products_schema` |
| 22 | TC-04b | GET | `/auth/products/1` | ✅ CRUD | Valid token | `id == 1` | `assert_field_equals("id", 1)` |
| 23 | TC-04c | GET | `/auth/products` | ❌ Auth | No token | HTTP 401 | `assert_unauthorised` |
| 24 | TC-04d | GET | `/auth/products/999999` | ❌ CRUD | Valid token | HTTP 404 | `assert_status_code(404)` |
| 25 | TC-04e | POST | `/auth/products/add` | ✅ CRUD | Valid token + payload | HTTP 201 + schema valid | `assert_product_schema` |
| 26 | TC-04f | POST | `/auth/products/add` | ✅ CRUD | title echoed back | Response title matches payload | `assert_field_equals("title")` |
| 27 | TC-04g×3 | POST | `/auth/products/add` | ✅ CRUD | 3 different categories | All 3 return 201 | `parametrize` |
| 28 | TC-04h | POST | `/auth/products/add` | ❌ Auth | No token | HTTP 401 | `assert_unauthorised` |
| 29 | TC-04i | PUT | `/auth/products/1` | ✅ CRUD | Update title | HTTP 200, title changed | `assert_field_equals("title")` |
| 30 | TC-04j | PUT | `/auth/products/1` | ❌ Auth | No token | HTTP 401 | `assert_unauthorised` |
| 31 | TC-04k | DELETE | `/auth/products/1` | ✅ CRUD | Valid token | HTTP 200 + `isDeleted: true` | `data["isDeleted"] is True` |
| 32 | TC-04l | DELETE | `/auth/products/1` | ❌ Auth | No token | HTTP 401 | `assert_unauthorised` |

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

---

## 📊 Expected Output

```
tests/test_login.py::TestLogin::test_valid_login_returns_200 PASSED
tests/test_login.py::TestLogin::test_valid_login_response_schema PASSED
tests/test_login.py::TestLogin::test_valid_login_access_token_is_jwt PASSED
...
tests/test_login.py::test_invalid_credential_combinations_return_400[emilys-wrongpass] PASSED
tests/test_login.py::test_invalid_credential_combinations_return_400[nobody-emilyspass] PASSED
...
tests/test_token_refresh.py::TestTokenRefresh::test_refreshed_token_works_on_protected_endpoint PASSED
...
tests/test_products.py::TestCreateProduct::test_create_products_parametrized[Laptop Pro-999.99-electronics] PASSED
tests/test_products.py::TestCreateProduct::test_create_products_parametrized[Cozy Blanket-29.99-home] PASSED
tests/test_products.py::TestCreateProduct::test_create_products_parametrized[Running Shoes-79.99-sports] PASSED
...
========== 32 passed in X.XXs ==========
```
