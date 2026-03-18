import jwt as pyjwt  # PyJWT

REQUIRED_LOGIN_FIELDS = {
    "id",
    "username",
    "email",
    "firstName",
    "lastName",
    "gender",
    "image",
    "accessToken",
    "refreshToken",
}
REQUIRED_PRODUCT_FIELDS = {"id", "title", "price", "stock", "category"}


def assert_status_code(response, expected: int) -> None:
    assert response.status_code == expected, (
        f"Expected HTTP {expected}, got {response.status_code}.\n"
        f"Body: {response.text[:400]}"
    )


# ------------------------------------------------------------------
# Auth / token
# ------------------------------------------------------------------


def assert_login_response(data: dict) -> None:
    """Assert POST /auth/login body contains all expected fields."""
    missing = REQUIRED_LOGIN_FIELDS - data.keys()
    assert not missing, f"Login response missing fields: {missing}"


def assert_token_is_jwt(token: str) -> None:
    """
    Assert the token is a structurally valid JWT (3 dot-separated parts).
    We decode without signature verification — we're testing the API
    contract, not re-implementing the auth server.
    """
    assert isinstance(token, str) and token.count(".") == 2, (
        f"Expected a JWT (3 parts), got: {token!r}"
    )
    # Decode header + payload only (no signature check)
    decoded = pyjwt.decode(token, options={"verify_signature": False})
    assert "exp" in decoded, "JWT payload should contain 'exp' (expiry) claim"


def assert_tokens_are_different(token_a: str, token_b: str) -> None:
    """Assert two tokens are not identical (e.g. after a refresh)."""
    assert token_a != token_b, (
        "Expected a NEW token after refresh, but got the same token back"
    )


def assert_unauthorised(response) -> None:
    assert response.status_code in (401, 403), (
        f"Expected HTTP 401 or 403, got {response.status_code}.\n"
        f"Body: {response.text[:400]}"
    )

def assert_product_schema(product: dict) -> None:
    missing = REQUIRED_PRODUCT_FIELDS - product.keys()
    assert not missing, f"Product object missing fields: {missing}"


def assert_all_products_schema(products: list) -> None:
    assert isinstance(products, list), f"Expected list, got {type(products).__name__}"
    for p in products:
        assert_product_schema(p)


def assert_field_equals(obj: dict, field: str, expected) -> None:
    actual = obj.get(field)
    assert actual == expected, f"Field '{field}': expected {expected!r}, got {actual!r}"


def assert_field_not_empty(obj: dict, field: str) -> None:
    value = obj.get(field)
    assert value not in (None, "", 0), (
        f"Field '{field}' should not be empty/zero, got: {value!r}"
    )
