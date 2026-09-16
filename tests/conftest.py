import json

import pytest

from apis.auth_api import AuthAPI
from apis.booking_api import BookingAPI
from apis.health_api import HealthAPI
from config.settings import settings
from core.client import HttpClient
from core.logger import setup_logger
from models.booking import Booking


def pytest_configure(config: pytest.Config):
    setup_logger(settings.log_dir, settings.log_level)


@pytest.fixture(scope="session")
def http_client() -> HttpClient:
    return HttpClient(base_url=settings.base_url, timeout=settings.timeout)


@pytest.fixture(scope="session")
def health_api(http_client: HttpClient) -> HealthAPI:
    return HealthAPI(http_client)


@pytest.fixture(scope="session")
def auth_api(http_client: HttpClient) -> AuthAPI:
    return AuthAPI(http_client)


@pytest.fixture(scope="session")
def booking_api(http_client: HttpClient) -> BookingAPI:
    return BookingAPI(http_client)


@pytest.fixture(scope="session", autouse=True)
def login(http_client: HttpClient, auth_api: AuthAPI):
    """整场测试登录一次，token 只存在 HttpClient 上。"""
    response = auth_api.create_token(settings.username, settings.password)
    token = response.json().get("token")
    if not token:
        raise RuntimeError(f"登录失败，无法获取 token: {response.text}")
    http_client.set_token(token)


@pytest.fixture
def booking_payload() -> dict:
    template = json.loads((settings.data_dir / "booking.json").read_text(encoding="utf-8"))
    return Booking.from_template(template, unique=True).to_dict()


@pytest.fixture
def created_booking(booking_api: BookingAPI, booking_payload: dict) -> dict:
    """创建一条预订，测试结束后尝试删除，避免污染环境。"""
    response = booking_api.create(booking_payload)
    assert response.status_code == 200, response.text
    booking_id = response.json()["bookingid"]
    yield {"id": booking_id, "payload": booking_payload, "create_response": response.json()}
    booking_api.delete(booking_id, with_token=True)
