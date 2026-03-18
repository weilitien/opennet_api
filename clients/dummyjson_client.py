import requests
from config.settings import BASE_URL, TIMEOUT
from typing import Optional


class DummyJsonClient:
    def __init__(
        self, base_url: str = BASE_URL, token: Optional[str] = None, timeout: int = TIMEOUT
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        if token:
            self.set_token(token)

    def set_token(self, token: str):
        """Inject / replace the Bearer token on the shared session."""
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def clear_token(self):
        """Remove the Authorization header (simulate logged-out state)."""
        self.session.headers.pop("Authorization", None)

    def login(self, username: str, password: str, expires_in_mins: int = 30):
        """POST /auth/login — returns accessToken + refreshToken"""
        return self.session.post(
            f"{self.base_url}/auth/login",
            json={
                "username": username,
                "password": password,
                "expiresInMins": expires_in_mins,
            },
            timeout=self.timeout,
        )

    def get_me(self) -> requests.Response:
        """GET /auth/me — returns the currently authenticated user (requires token)"""
        return self.session.get(f"{self.base_url}/auth/me", timeout=self.timeout)

    def refresh_token(
        self, refresh_token: str, expires_in_mins: int = 30
    ) -> requests.Response:
        """POST /auth/refresh — exchange refreshToken for a new accessToken"""
        return self.session.post(
            f"{self.base_url}/auth/refresh",
            json={"refreshToken": refresh_token, "expiresInMins": expires_in_mins},
            timeout=self.timeout,
        )

    # ------------------------------------------------------------------
    # Products
    # ------------------------------------------------------------------

    def get_products(self, **params) -> requests.Response:
        """GET /auth/products"""
        return self.session.get(
            f"{self.base_url}/auth/products", params=params, timeout=self.timeout
        )

    def get_product(self, product_id: int) -> requests.Response:
        """GET /auth/products/{id}"""
        return self.session.get(
            f"{self.base_url}/auth/products/{product_id}", timeout=self.timeout
        )

    def create_product(self, payload: dict) -> requests.Response:
        """POST /auth/products/add"""
        return self.session.post(
            f"{self.base_url}/auth/products/add", json=payload, timeout=self.timeout
        )

    def update_product(self, product_id: int, payload: dict) -> requests.Response:
        """PUT /auth/products/{id}"""
        return self.session.put(
            f"{self.base_url}/auth/products/{product_id}",
            json=payload,
            timeout=self.timeout,
        )

    def delete_product(self, product_id: int) -> requests.Response:
        """DELETE /auth/products/{id}"""
        return self.session.delete(
            f"{self.base_url}/auth/products/{product_id}", timeout=self.timeout
        )
