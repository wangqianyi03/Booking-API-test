from typing import Any

import requests

from core.logger import get_logger, mask_sensitive

logger = get_logger()


class HttpClient:

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
        self._token: str | None = None

    @property
    def token(self) -> str | None:
        return self._token

    def set_token(self, token: str | None):
        self._token = token

    def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        with_token: bool = False,
        basic_auth: tuple[str, str] | None = None,
    ) -> requests.Response:
        url = f"{self.base_url}{path if path.startswith('/') else '/' + path}"
        req_headers = dict(headers or {})
        if with_token:
            if not self._token:
                raise RuntimeError("需要 token 但尚未登录，请先调用 http_client.set_token()")
            req_headers["Cookie"] = f"token={self._token}"

        logger.info(">>> %s %s params=%s body=%s", method.upper(), url, params, mask_sensitive(json))
        if req_headers.get("Cookie"):
            logger.info(">>> Cookie: token=***")

        response = self.session.request(
            method=method.upper(),
            url=url,
            json=json,
            params=params,
            headers=req_headers,
            timeout=self.timeout,
            auth=basic_auth,
        )

        body_preview = response.text[:800] if response.text else ""
        logger.info("<<< %s %s (%.3fs) %s", response.status_code, url, response.elapsed.total_seconds(), body_preview)
        return response

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("DELETE", path, **kwargs)
