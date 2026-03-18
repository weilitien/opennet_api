import pytest
from config.settings import (
    VALID_USERNAME,
    VALID_PASSWORD,
    INVALID_USERNAME,
    INVALID_PASSWORD,
)
from utils.validators import (
    assert_status_code,
    assert_login_response,
    assert_token_is_jwt,
    assert_field_equals,
)


class TestLogin:
    # ------------------------------------------------------------------
    # TC-01a — Positive: valid credentials
    # ------------------------------------------------------------------

    def test_valid_login_returns_200(self, client):
        """
        Steps:
          1. POST /auth/login with valid username + password
          2. Assert status 200
        Expected result: HTTP 200 OK
        Validation: assert_status_code(response, 200)
        """
        response = client.login(VALID_USERNAME, VALID_PASSWORD)
        assert_status_code(response, 200)

    def test_valid_login_response_schema(self, client):
        """
        Steps:
          1. POST /auth/login with valid credentials
          2. Parse body
          3. Assert all required fields present
        Expected result: body contains id, username, email, firstName,
                         lastName, gender, image, accessToken, refreshToken
        Validation: assert_login_response (schema check)
        """
        response = client.login(VALID_USERNAME, VALID_PASSWORD)
        assert_status_code(response, 200)
        assert_login_response(response.json())

    def test_valid_login_access_token_is_jwt(self, client):
        """
        Steps:
          1. POST /auth/login
          2. Extract accessToken
          3. Assert it is a structurally valid JWT with an 'exp' claim
        Expected result: accessToken is a 3-part JWT with expiry
        Validation: assert_token_is_jwt (structure + decode check)
        Why? A malformed token would silently fail on every downstream
        request. Catching it here pinpoints the root cause immediately.
        """
        response = client.login(VALID_USERNAME, VALID_PASSWORD)
        assert_status_code(response, 200)
        assert_token_is_jwt(response.json()["accessToken"])

    def test_valid_login_refresh_token_is_jwt(self, client):
        """
        Steps:
          1. POST /auth/login
          2. Extract refreshToken
          3. Assert it is a valid JWT
        Expected result: refreshToken is also a 3-part JWT
        Validation: assert_token_is_jwt
        """
        response = client.login(VALID_USERNAME, VALID_PASSWORD)
        assert_status_code(response, 200)
        assert_token_is_jwt(response.json()["refreshToken"])

    def test_valid_login_username_matches(self, client):
        """
        Steps:
          1. POST /auth/login with username 'emilys'
          2. Assert response username == 'emilys'
        Expected result: server echoes back the authenticated user's data
        Validation: field equality on 'username'
        """
        response = client.login(VALID_USERNAME, VALID_PASSWORD)
        assert_status_code(response, 200)
        assert_field_equals(response.json(), "username", VALID_USERNAME)

    # ------------------------------------------------------------------
    # TC-01b — Negative: invalid credentials
    # ------------------------------------------------------------------

    def test_wrong_password_returns_400(self, client):
        """
        Steps:
          1. POST /auth/login with valid username but WRONG password
          2. Assert status 400
        Expected result: HTTP 400 Bad Request
        Validation: assert_status_code(response, 400)
        Why 400 and not 401? DummyJSON returns 400 for bad credentials
        (login is not an authenticated endpoint, so 401 doesn't apply).
        """
        response = client.login(VALID_USERNAME, INVALID_PASSWORD)
        assert_status_code(response, 400)

    def test_wrong_username_returns_400(self, client):
        """
        Steps:
          1. POST /auth/login with non-existent username
          2. Assert status 400
        Expected result: HTTP 400 Bad Request
        Validation: assert_status_code(response, 400)
        """
        response = client.login(INVALID_USERNAME, VALID_PASSWORD)
        assert_status_code(response, 400)

    def test_empty_credentials_returns_400(self, client):
        """
        Steps:
          1. POST /auth/login with empty username and password
          2. Assert status 400
        Expected result: server rejects blank credentials
        Validation: assert_status_code(response, 400)
        """
        response = client.login("", "")
        assert_status_code(response, 400)

    @pytest.mark.parametrize(
        "username,password",
        [
            ("emilys", "wrongpass"),
            ("nobody", "emilyspass"),
            ("", "emilyspass"),
            ("emilys", ""),
        ],
    )
    def test_invalid_credential_combinations_return_400(
        self, client, username, password
    ):
        """
        Steps:
          1. POST /auth/login with each invalid credential pair
          2. Assert status 400 for all combinations
        Expected result: every invalid combination is rejected
        Validation: parametrize covers 4 bad-credential scenarios
        Why parametrize? One function = 4 negative cases, no duplication.
        """
        response = client.login(username, password)
        assert_status_code(response, 400)
