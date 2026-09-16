import allure
import pytest
from apis.health_api import HealthAPI
from core.assertions import assert_status_code

@allure.epic("Restful Booker")
@allure.feature("健康检查")
@pytest.mark.smoke
class TestHealth:
    @allure.story("服务存活")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_ping_returns_201(self, health_api: HealthAPI):
        response = health_api.ping()
        assert_status_code(response, 201)
        assert response.text == "Created"
