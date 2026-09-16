from collections.abc import Iterable
from typing import Any

import requests


def _body(response: requests.Response) -> str:
    text = response.text or ""
    return text if len(text) <= 1000 else text[:1000] + "...(truncated)"


def assert_status_code(response: requests.Response, expected: int | Iterable[int]):
    allowed = (expected,) if isinstance(expected, int) else tuple(expected)
    assert response.status_code in allowed, (
        f"状态码不符合预期: 期望 {allowed}，实际 {response.status_code}，响应: {_body(response)}"
    )


def assert_json_key(payload: dict[str, Any], key: str) -> Any:
    assert key in payload, f"响应 JSON 缺少字段 '{key}'，实际 keys={list(payload.keys())}"
    return payload[key]


def assert_json_contains(payload: dict[str, Any], expected: dict[str, Any], path: str = ""):

    for key, value in expected.items():

        current = f"{path}.{key}" if path else key #记录当前期望字段

        assert key in payload, f"缺少字段 {current}，实际 keys={list(payload.keys())}"

        actual = payload[key]

        if isinstance(value, dict):
            assert isinstance(actual, dict), f"{current} 期望是对象，实际是 {type(actual).__name__}"
            assert_json_contains(actual, value, current)
        else:
            assert actual == value, f"{current} 值不匹配: 期望 {value!r}，实际 {actual!r}"


