from typing import Any

import requests

from core.client import HttpClient


class BookingAPI:
    def __init__(self, client: HttpClient):
        self._client = client

    def get_ids(self, **filters: Any) -> requests.Response:
        return self._client.get("/booking", params=filters or None)

    def get_by_id(self, booking_id: int) -> requests.Response:
        return self._client.get(f"/booking/{booking_id}")

    def create(self, payload: dict[str, Any]) -> requests.Response:
        return self._client.post("/booking", json=payload)

    def update(self, booking_id: int, payload: dict[str, Any], with_token: bool = True) -> requests.Response:
        return self._client.put(f"/booking/{booking_id}", json=payload, with_token=with_token)

    def partial_update(self, booking_id: int, payload: dict[str, Any], with_token: bool = True) -> requests.Response:
        return self._client.patch(f"/booking/{booking_id}", json=payload, with_token=with_token)

    def delete(
        self,
        booking_id: int,
        with_token: bool = True,
        basic_auth: tuple[str, str] | None = None,
    ) -> requests.Response:
        return self._client.delete(
            f"/booking/{booking_id}",
            with_token=with_token,
            basic_auth=basic_auth,
        )
