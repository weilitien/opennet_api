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



---

## Test Cases

### TC-01 — POST /auth/login

| # | Test | Type | Steps | Expected Result | Validation |
|---|------|------|-------|-----------------|------------|
| 1 | `test_valid_login_returns_200` | [V] Positive | POST with valid credentials | HTTP 200 | `assert_status_code(200)` |
| 2 | `test_valid_login_response_schema` | [V] Positive | POST valid credentials, parse body | Body contains all required fields | `assert_login_response` |
| 3 | `test_valid_login_refresh_token_is_jwt` | [V] Positive | POST valid credentials, check refreshToken | refreshToken is a valid JWT with `exp` claim | `assert_token_is_jwt` |
| 4 | `test_valid_login_username_matches` | [V] Positive | POST valid credentials, check username | Response username equals sent username | `assert_field_equals("username")` |
| 5 | `test_wrong_password_returns_400` | [X] Negative | POST with wrong password | HTTP 400 | `assert_status_code(400)` |
| 6 | `test_wrong_username_returns_400` | [X] Negative | POST with non-existent username | HTTP 400 | `assert_status_code(400)` |
| 7 | `test_empty_credentials_returns_400` | [X] Negative | POST with empty username + password | HTTP 400 | `assert_status_code(400)` |
| 8 | `test_invalid_credential_combinations_return_400` | [X] Negative | POST 4 bad-credential combos (parametrize) | HTTP 400 for all | `parametrize` × `assert_status_code(400)` |

### TC-02 — Authenticated CRUD /auth/products

| # | Test | Type | Steps | Expected Result | Validation |
|---|------|------|-------|-----------------|------------|
| 1 | `test_get_products_with_token_returns_200` | [V] Positive | GET /auth/products with Bearer token | HTTP 200 | `assert_status_code(200)` |
| 2 | `test_get_products_schema` | [V] Positive | GET /auth/products, parse body | All product objects have required fields | `assert_all_products_schema` |
| 3 | `test_get_single_product_with_token_returns_200` | [V] Positive | GET /auth/products/1 with Bearer token | HTTP 200 | `assert_status_code(200)` |
| 4 | `test_get_single_product_id_matches` | [V] Positive | GET /auth/products/1, check id | Response `id == 1` | `assert_field_equals("id", 1)` |
| 5 | `test_get_products_without_token_returns_401` | [X] Negative | GET /auth/products with no token | HTTP 401 | `assert_unauthorised` |
| 6 | `test_get_nonexistent_product_returns_404` | [X] Negative | GET /auth/products/999999 | HTTP 404 | `assert_status_code(404)` |
| 7 | `test_create_product_returns_201` | [V] Positive | POST /auth/products/add with valid payload | HTTP 201 | `assert_status_code(201)` |
| 8 | `test_create_product_response_schema` | [V] Positive | POST valid payload, parse body | Response is a valid product object | `assert_product_schema` |
| 9 | `test_create_product_title_matches` | [V] Positive | POST with known title, check echo | Response title equals sent title | `assert_field_equals("title")` |
| 10 | `test_create_product_without_token_returns_401` | [X] Negative | POST with no token | HTTP 401 | `assert_unauthorised` |
| 11 | `test_create_products_parametrized` | [V] Positive | POST 3 different categories (parametrize) | HTTP 201 + title/price echoed for all | `parametrize` × `assert_field_equals` |
| 12 | `test_update_product_returns_200` | [V] Positive | PUT /auth/products/1 with new title | HTTP 200 | `assert_status_code(200)` |
| 13 | `test_update_product_title_is_changed` | [V] Positive | PUT new title, check response | Response title equals new title | `assert_field_equals("title")` |
| 14 | `test_update_product_without_token_returns_401` | [X] Negative | PUT with no token | HTTP 401 | `assert_unauthorised` |
| 15 | `test_delete_product_returns_200` | [V] Positive | DELETE /auth/products/1 with Bearer token | HTTP 200 | `assert_status_code(200)` |
| 16 | `test_delete_product_response_has_deleted_flag` | [V] Positive | DELETE, check isDeleted field | `isDeleted: true` in response | `data["isDeleted"] is True` |
| 17 | `test_delete_product_without_token_returns_401` | [X] Negative | DELETE with no token | HTTP 401 | `assert_unauthorised` |

---


## Validation Strategy

| Validation | Used where | Why |
|------------|-----------|-----|
| **Status code** | All tests | Primary HTTP contract — wrong code = broken endpoint |
| **`assert_login_response` schema** | TC-01-2 | Catches silent field removal that would break all downstream token usage |
| **`assert_token_is_jwt`** | TC-01-3 | JWT structure + `exp` claim check — catches malformed tokens before they silently fail elsewhere |
| **`assert_all_products_schema`** | TC-02-2 | Ensures every item in the list is a valid product object |
| **`assert_unauthorised`** | All 401 tests | Accepts both 401 and 403 — DummyJSON uses both depending on the endpoint |
| **`isDeleted: true` check** | TC-02-16 | Confirms deletion was acknowledged — not just an empty 200 |
| **`parametrize` on bad credentials** | TC-01-8 | 4 invalid combos in 1 function, zero duplication |
| **`parametrize` on product categories** | TC-02-11 | Proves the API accepts different product types, not a hardcoded fixture |

---


**Key design decisions:**
- Login runs **once per session** in `conftest.py` — no repeated logins per test
- `auth_client` fixture injects token automatically via `set_token()`
- `client` fixture is unauthenticated — used for 401 tests

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
