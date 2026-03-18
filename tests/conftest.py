import pytest
from clients.dummyjson_client import DummyJsonClient
from config.settings import (
    BASE_URL,
    VALID_USERNAME,
    VALID_PASSWORD,
    TOKEN_EXPIRES_IN_MINS,
)


@pytest.fixture(scope="function")
def client():
    """
    Didn't login yet fixture.
    """
    return DummyJsonClient(base_url=BASE_URL)


@pytest.fixture(scope="function")
def auth_client():
    client = DummyJsonClient(base_url=BASE_URL)
    response = client.login(VALID_USERNAME, VALID_PASSWORD, TOKEN_EXPIRES_IN_MINS)
    if response.status_code != 200:
        pytest.fail(
            f"Session setup failed: POST /auth/login returned "
            f"{response.status_code}. Body: {response.text[:300]}"
        )
    client.set_token(response.json()["accessToken"])
    return client
