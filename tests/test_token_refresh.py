from utils.validators import (
    assert_status_code,
    assert_token_is_jwt,
    assert_tokens_are_different,
    assert_unauthorised,
)
from clients.dummyjson_client import DummyJsonClient
from config.settings import BASE_URL


class TestTokenRefresh:
  # ------------------------------------------------------------------
  # TC-03a — Positive: valid refresh token
  # ------------------------------------------------------------------

  def test_refresh_returns_200(self, client, auth_tokens):
      """
      Steps:
        1. Take refreshToken from the session login
        2. POST /auth/refresh with that refreshToken
        3. Assert status 200
      Expected result: HTTP 200 OK
      Validation: assert_status_code(response, 200)
      """
      response = client.refresh_token(auth_tokens["refreshToken"])
      assert_status_code(response, 200)

  def test_refresh_returns_new_access_token(self, client, auth_tokens):
      """
      Steps:
        1. POST /auth/refresh
        2. Parse body
        3. Assert 'accessToken' is present and is a valid JWT
      Expected result: new accessToken is a well-formed JWT
      Validation: assert_token_is_jwt
      """
      response = client.refresh_token(auth_tokens["refreshToken"])
      assert_status_code(response, 200)
      data = response.json()
      assert "accessToken" in data, "Refresh response must contain 'accessToken'"
      assert_token_is_jwt(data["accessToken"])

  def test_refresh_returns_new_refresh_token(self, client, auth_tokens):
      """
      Steps:
        1. POST /auth/refresh
        2. Assert 'refreshToken' is in response and is a valid JWT
      Expected result: a new refreshToken is also issued (token rotation)
      Validation: assert_token_is_jwt on the new refreshToken
      """
      response = client.refresh_token(auth_tokens["refreshToken"])
      assert_status_code(response, 200)
      data = response.json()
      assert "refreshToken" in data, "Refresh response must contain 'refreshToken'"
      assert_token_is_jwt(data["refreshToken"])

  def test_refreshed_access_token_is_different_from_original(
      self, client, auth_tokens
  ):
      """
      Steps:
        1. Record the original accessToken from session login
        2. POST /auth/refresh
        3. Assert new accessToken != original accessToken
      Expected result: each refresh produces a genuinely new token
      Validation: assert_tokens_are_different
      Why? If the server hands back the same token, the 'refresh'
      endpoint is broken — there's no session extension happening.
      """
      response = client.refresh_token(auth_tokens["refreshToken"])
      assert_status_code(response, 200)
      new_access_token = response.json()["accessToken"]
      assert_tokens_are_different(auth_tokens["accessToken"], new_access_token)

  def test_refreshed_token_works_on_protected_endpoint(self, client, auth_tokens):
      """
      Steps:
        1. POST /auth/refresh → get new accessToken
        2. Create a new client with the refreshed token
        3. GET /auth/me
        4. Assert status 200
      Expected result: the freshly issued token is immediately usable
      Validation: assert_status_code(response, 200) on /auth/me
      This is the most important refresh test — it proves the new token
      is cryptographically valid and accepted by the auth server.
      """
      refresh_response = client.refresh_token(auth_tokens["refreshToken"])
      assert_status_code(refresh_response, 200)
      new_token = refresh_response.json()["accessToken"]

      # Build a fresh client using only the refreshed token
      refreshed_client = DummyJsonClient(base_url=BASE_URL, token=new_token)
      me_response = refreshed_client.get_me()
      assert_status_code(me_response, 200)

  # ------------------------------------------------------------------
  # TC-03b — Negative: invalid refresh token
  # ------------------------------------------------------------------

  def test_invalid_refresh_token_is_rejected(self, client):
      """
      Steps:
        1. POST /auth/refresh with a fake/garbage refreshToken
        2. Assert status 401
      Expected result: server rejects invalid refresh tokens
      Validation: assert_unauthorised
      """
      response = client.refresh_token("this.fake.refreshtoken")
      assert_unauthorised(response)

