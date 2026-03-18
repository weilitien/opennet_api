"""
TC-02 — GET /auth/me

Tests the "who am I?" endpoint that requires a valid Bearer token.
This is the simplest way to prove that:
  - a valid token grants access
  - a missing or invalid token is rejected
"""

from utils.validators import (
    assert_status_code,
    assert_field_equals,
    assert_unauthorised,
)
from config.settings import VALID_USERNAME
from clients.dummyjson_client import DummyJsonClient
from config.settings import BASE_URL


class TestAuthMe:
    # ------------------------------------------------------------------
    # TC-02a — Positive: valid token
    # ------------------------------------------------------------------

    def test_get_me_with_valid_token_returns_200(self, auth_client):
        """
        Steps:
          1. Use auth_client (Bearer token already set from session login)
          2. GET /auth/me
          3. Assert status 200
        Expected result: HTTP 200 OK
        Validation: assert_status_code(response, 200)
        """
        response = auth_client.get_me()
        assert_status_code(response, 200)

    def test_get_me_returns_correct_username(self, auth_client):
        """
        Steps:
          1. GET /auth/me with valid token
          2. Assert response username matches the account we logged in with
        Expected result: server identifies the correct user from the token
        Validation: field equality on 'username'
        """
        response = auth_client.get_me()
        assert_status_code(response, 200)
        assert_field_equals(response.json(), "username", VALID_USERNAME)

    def test_get_me_response_has_no_password(self, auth_client):
        """
        Steps:
          1. GET /auth/me
          2. Assert response does NOT contain a 'password' field
        Expected result: sensitive fields are never exposed in API responses
        Validation: 'password' key absent from response body
        Why? Leaking password hashes is a critical security bug.
        """
        response = auth_client.get_me()
        assert_status_code(response, 200)
        data = response.json()
        assert "password" not in data, (
            "Security issue: 'password' field should never appear in /auth/me response"
        )

    # ------------------------------------------------------------------
    # TC-02b — Negative: missing or invalid token
    # ------------------------------------------------------------------

    def test_get_me_without_token_returns_401(self, client):
        """
        Steps:
          1. Use unauthenticated client (no Authorization header)
          2. GET /auth/me
          3. Assert status 401
        Expected result: HTTP 401 Unauthorised
        Validation: assert_unauthorised (status + body check)
        """
        response = client.get_me()
        assert_unauthorised(response)

    def test_get_me_with_invalid_token_returns_401(self):
        """
        Steps:
          1. Create a client with a garbage token string
          2. GET /auth/me
          3. Assert status 401
        Expected result: malformed/fake JWT is rejected
        Validation: assert_unauthorised
        Why test garbage tokens separately? Ensures the server actually
        validates the JWT signature — not just the presence of any string
        in the Authorization header.
        """
        bad_client = DummyJsonClient(base_url=BASE_URL, token="this.is.fake")
        response = bad_client.get_me()
        assert_unauthorised(response)
