from typing import Any

import requests

from core.client import HttpClient


class AuthAPI:
    def __init__(self, client: HttpClient):
        self._client = client

    def create_token(self, username: str, password: str) -> requests.Response:
        payload: dict[str, Any] = {"username": username, "password": password}
        return self._client.post("/auth", json=payload)
