import json
import allure
import pytest
from apis.auth_api import AuthAPI
from apis.booking_api import BookingAPI
from config.settings import settings
from core.assertions import assert_json_key, assert_status_code

_INVALID_AUTH = json.loads((settings.data_dir / "invalid_auth.json").read_text(encoding="utf-8"))

@allure.epic("Restful Booker")
@allure.feature("鉴权")
@pytest.mark.auth
class TestAuth:

    @allure.story("合法账号获取 token")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_create_token_success(self, auth_api: AuthAPI):
        response = auth_api.create_token(settings.username, settings.password)
        assert_status_code(response, 200)
        token = assert_json_key(response.json(), "token")
        assert isinstance(token, str) and token


    @allure.story("非法账号无法获取 token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.negative
    @pytest.mark.parametrize(
        "credentials",
        _INVALID_AUTH.values(),
        ids=_INVALID_AUTH.keys(),
    )
    def test_create_token_invalid_credentials(self, auth_api: AuthAPI, credentials: dict):
        response = auth_api.create_token(credentials["username"], credentials["password"])
        # Restful Booker 对错误凭据仍返回 200，body 里带 reason，这是被测服务的已知行为
        assert_status_code(response, 200)
        body = response.json()
        assert "token" not in body
        assert body.get("reason") == "Bad credentials"


    @allure.story("无 token 不能全量更新")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.negative
    def test_update_without_token_forbidden(
        self, booking_api: BookingAPI, created_booking: dict
    ):
        payload = dict(created_booking["payload"])
        payload["firstname"] = "ShouldNotUpdate"
        response = booking_api.update(created_booking["id"], payload, with_token=False)
        assert_status_code(response, 403)


    @allure.story("无 token 不能删除")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.negative
    def test_delete_without_token_forbidden(
        self, booking_api: BookingAPI, created_booking: dict
    ):
        response = booking_api.delete(created_booking["id"], with_token=False)
        assert_status_code(response, 403)


    @allure.story("伪造 token 不能更新")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_update_with_invalid_token_forbidden(
        self, http_client, booking_api: BookingAPI, created_booking: dict
    ):
        payload = dict(created_booking["payload"])
        payload["firstname"] = "InvalidToken"
        original = http_client.token
        http_client.set_token("invalid-token")
        try:
            response = booking_api.update(created_booking["id"], payload, with_token=True)
            assert_status_code(response, 403)
        finally:
            http_client.set_token(original)


    @allure.story("Basic Auth 也可以删除预订")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_with_basic_auth(
        self, booking_api: BookingAPI, booking_payload: dict
    ):
        created = booking_api.create(booking_payload)
        assert_status_code(created, 200)
        booking_id = created.json()["bookingid"]
        response = booking_api.delete(
            booking_id,
            with_token=False,
            basic_auth=(settings.username, settings.password),
        )
        assert_status_code(response, 201)
        assert_status_code(booking_api.get_by_id(booking_id), 404)


