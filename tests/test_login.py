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

    def test_valid_login_returns_200(self, client):
        """
        Steps:
          1. Send POST /auth/login with valid username and password
          2. Assert status code is 200
        Expected result: HTTP 200 OK
        Validation: assert_status_code(response, 200)
        """
        response = client.login(VALID_USERNAME, VALID_PASSWORD)
        assert_status_code(response, 200)

    def test_valid_login_response_schema(self, client):
        """
        Steps:
          1. Send POST /auth/login with valid credentials
          2. Parse response body
          3. Assert all required fields are present
        Expected result: body contains id, username, email, firstName,
                         lastName, gender, image, accessToken, refreshToken
        Validation: assert_login_response (schema check)
        """
        response = client.login(VALID_USERNAME, VALID_PASSWORD)
        assert_status_code(response, 200)
        assert_login_response(response.json())

    def test_valid_login_refresh_token_is_jwt(self, client):
        """
        Steps:
          1. Send POST /auth/login with valid credentials
          2. Extract refreshToken from response body
          3. Assert it is a structurally valid JWT with an 'exp' claim
        Expected result: refreshToken is a 3-part JWT with expiry
        Validation: assert_token_is_jwt (structure + decode check)
        """
        response = client.login(VALID_USERNAME, VALID_PASSWORD)
        assert_status_code(response, 200)
        assert_token_is_jwt(response.json()["refreshToken"])

    def test_valid_login_username_matches(self, client):
        """
        Steps:
          1. Send POST /auth/login with username 'emilys'
          2. Parse response body
          3. Assert response username equals 'emilys'
        Expected result: server echoes back the authenticated user's username
        Validation: assert_field_equals(data, "username", VALID_USERNAME)
        """
        response = client.login(VALID_USERNAME, VALID_PASSWORD)
        assert_status_code(response, 200)
        assert_field_equals(response.json(), "username", VALID_USERNAME)

    def test_wrong_password_returns_400(self, client):
        """
        Steps:
          1. Send POST /auth/login with valid username but wrong password
          2. Assert status code is 400
        Expected result: HTTP 400 Bad Request
        Validation: assert_status_code(response, 400)
        """
        response = client.login(VALID_USERNAME, INVALID_PASSWORD)
        assert_status_code(response, 400)

    def test_wrong_username_returns_400(self, client):
        """
        Steps:
          1. Send POST /auth/login with non-existent username
          2. Assert status code is 400
        Expected result: HTTP 400 Bad Request
        Validation: assert_status_code(response, 400)
        """
        response = client.login(INVALID_USERNAME, VALID_PASSWORD)
        assert_status_code(response, 400)

    def test_empty_credentials_returns_400(self, client):
        """
        Steps:
          1. Send POST /auth/login with empty username and password
          2. Assert status code is 400
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
            ("",       "emilyspass"),
            ("emilys", ""),
        ],
    )
    def test_invalid_credential_combinations_return_400(
        self, client, username, password
    ):
        """
        Steps:
          1. Send POST /auth/login with each invalid credential pair
          2. Assert status code is 400 for all combinations
        Expected result: every invalid combination is rejected
        Validation: parametrize covers 4 bad-credential scenarios,
                    assert_status_code(response, 400) for each
        """
        response = client.login(username, password)
        assert_status_code(response, 400)