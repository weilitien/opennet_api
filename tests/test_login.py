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
        response = client.login(VALID_USERNAME, VALID_PASSWORD)
        assert_status_code(response, 200)

    def test_valid_login_response_schema(self, client):
        response = client.login(VALID_USERNAME, VALID_PASSWORD)
        assert_status_code(response, 200)
        assert_login_response(response.json())

    def test_valid_login_refresh_token_is_jwt(self, client):
        response = client.login(VALID_USERNAME, VALID_PASSWORD)
        assert_status_code(response, 200)
        assert_token_is_jwt(response.json()["refreshToken"])

    def test_valid_login_username_matches(self, client):
        response = client.login(VALID_USERNAME, VALID_PASSWORD)
        assert_status_code(response, 200)
        assert_field_equals(response.json(), "username", VALID_USERNAME)

    def test_wrong_password_returns_400(self, client):
        response = client.login(VALID_USERNAME, INVALID_PASSWORD)
        assert_status_code(response, 400)

    def test_wrong_username_returns_400(self, client):
        response = client.login(INVALID_USERNAME, VALID_PASSWORD)
        assert_status_code(response, 400)

    def test_empty_credentials_returns_400(self, client):
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
        response = client.login(username, password)
        assert_status_code(response, 400)
