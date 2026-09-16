import allure
import pytest
from apis.booking_api import BookingAPI
from core.assertions import assert_json_contains, assert_json_key, assert_status_code
from models.booking import Booking

@allure.epic("Restful Booker")
@allure.feature("预订管理")
@pytest.mark.crud
class TestBookingCRUD:
    @allure.story("创建预订")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_create_booking(self, booking_api: BookingAPI, booking_payload: dict):
        response = booking_api.create(booking_payload)
        assert_status_code(response, 200)
        body = response.json()
        booking_id = assert_json_key(body, "bookingid")
        assert isinstance(booking_id, int)
        assert_json_contains(body["booking"], booking_payload)
        booking_api.delete(booking_id, with_token=True)

    @allure.story("按 ID 查询预订")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_booking_by_id(self, booking_api: BookingAPI, created_booking: dict):
        response = booking_api.get_by_id(created_booking["id"])
        assert_status_code(response, 200)
        assert_json_contains(response.json(), created_booking["payload"])

    @allure.story("按firstname过滤预订 ID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_booking_ids_by_firstname(
        self, booking_api: BookingAPI, created_booking: dict
    ):
        firstname = created_booking["payload"]["firstname"]
        response = booking_api.get_ids(firstname=firstname)
        assert_status_code(response, 200)
        ids = [item["bookingid"] for item in response.json()]
        assert created_booking["id"] in ids

    @allure.story("按lastname过滤 ID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_booking_ids_by_lastname(
        self,booking_api:BookingAPI,created_booking:dict
    ):
        lastname = created_booking["payload"]["lastname"]
        response = booking_api.get_ids(lastname=lastname)
        assert_status_code(response,200)
        ids = [item["bookingid"] for item in response.json()]
        assert created_booking["id"] in ids

    @allure.story("全量更新预订")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_booking(self, booking_api: BookingAPI, created_booking: dict):
        updated = Booking.from_dict(created_booking["payload"])
        updated.firstname = updated.firstname + "Upd"
        updated.totalprice = 999
        updated.additionalneeds = "Lunch"
        payload = updated.to_dict()

        response = booking_api.update(created_booking["id"], payload)
        assert_status_code(response, 200)
        assert_json_contains(response.json(), payload)

        fetched = booking_api.get_by_id(created_booking["id"])
        assert_json_contains(fetched.json(), payload)

    @allure.story("部分更新预订")
    @allure.severity(allure.severity_level.NORMAL)
    def test_partial_update_booking(self, booking_api: BookingAPI, created_booking: dict):
        patch_body = {"additionalneeds": "Late Checkout"}
        response = booking_api.partial_update(created_booking["id"], patch_body)
        assert_status_code(response, 200)
        assert_json_contains(response.json(), patch_body)
        assert response.json()["firstname"] == created_booking["payload"]["firstname"]

    @allure.story("删除预订")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_booking(self, booking_api: BookingAPI, booking_payload: dict):
        created = booking_api.create(booking_payload)
        assert_status_code(created, 200)
        booking_id = created.json()["bookingid"]

        deleted = booking_api.delete(booking_id)
        assert_status_code(deleted, 201)
        assert deleted.text == "Created"
        assert_status_code(booking_api.get_by_id(booking_id), 404)


