import requests

from core.client import HttpClient


class HealthAPI:
    def __init__(self, client: HttpClient):
        self._client = client

    def ping(self) -> requests.Response:
        return self._client.get("/ping")
