import allure
import pytest
from apis.booking_api import BookingAPI
from core.assertions import assert_status_code

@allure.epic("Restful Booker")
@allure.feature("预订管理")
@pytest.mark.crud
@pytest.mark.negative
class TestBookingNegative:
    @allure.story("查询不存在的预订")
    def test_get_nonexistent_booking(self, booking_api: BookingAPI):
        response = booking_api.get_by_id(999999)
        assert_status_code(response, 404)

    @allure.story("缺少必填字段创建预订")
    def test_create_booking_missing_fields(self, booking_api: BookingAPI):
        response = booking_api.create({"firstname": "Incomplete"})
        # 被测服务未做参数校验，非法 body 直接 500，属于已知缺陷，这里按实际行为锁定
        assert_status_code(response, 500)

    @allure.story("删除不存在的预订")
    def test_delete_nonexistent_booking(self, booking_api: BookingAPI):
        response = booking_api.delete(999999, with_token=True)
        # 官方实现返回 405 而不是 404，作为缺陷记录进用例
        assert_status_code(response, 405)
