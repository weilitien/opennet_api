import pytest
from clients.dummyjson_client import DummyJsonClient
from config.settings import (
    BASE_URL,
    VALID_USERNAME,
    VALID_PASSWORD,
    TOKEN_EXPIRES_IN_MINS,
)


@pytest.fixture(scope="session")
def client():
    """Unauthenticated client — used for login tests and 401 tests."""
    return DummyJsonClient(base_url=BASE_URL)


@pytest.fixture(scope="session")
def auth_tokens(client):
    response = client.login(VALID_USERNAME, VALID_PASSWORD, TOKEN_EXPIRES_IN_MINS)
    if response.status_code != 200:
        pytest.fail(
            f"Session setup failed: POST /auth/login returned "
            f"{response.status_code}. Body: {response.text[:300]}"
        )
    return response.json()


@pytest.fixture(scope="session")
def auth_client(auth_tokens):
    return DummyJsonClient(base_url=BASE_URL, token=auth_tokens["accessToken"])
