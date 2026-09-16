# Restful Booker 接口自动化测试框架

基于 **pytest + requests** 的分层接口测试项目，被测服务是本机 Docker 中的 [Restful Booker](https://restful-booker.herokuapp.com/apidoc/index.html)（`http://localhost:3001`）。

覆盖：健康检查、鉴权（Cookie token / Basic Auth）、预订增删改查、负向用例、请求日志、环境配置、Allure / HTML 报告。

---

## 1. 环境准备

- Python 3.10+
- Docker Desktop 已安装并正在运行
- 先拉起被测服务 Restful Booker（宿主机端口 **3001**）：

```powershell
docker run -d --name booker -p 3001:3001 mwinteringham/restfulbooker
docker start booker
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```
```text
BASE_URL=http://localhost:3001
AUTH_USERNAME=admin
AUTH_PASSWORD=password123
```

---

## 2. 运行

```powershell
# 全量
pytest

# 冒烟
pytest -m smoke

# 鉴权 / CRUD / 负向
pytest -m auth
pytest -m crud
pytest -m negative

# HTML 报告
pytest --html=reports/report.html --self-contained-html

# Allure 数据QEQQ
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

运行后请求日志在 `logs/api_YYYYMMDD.log`。密码和 token 已脱敏。

---

## 3. 用例设计

按接口文档主路径和风险设计。服务地址 `http://localhost:3001`。预订数据来自 `data/booking.json`（姓名加唯一后缀）。除特别说明外，session 会先登录并把 token 放在 client 上。

| 用例编号 | 用例标题 | 项目/模块 | 优先级 | 前置条件 | 测试步骤 | 测试数据 | 预期结果 |
|---|---|---|---|---|---|---|---|
| TC-HL-01 | 服务存活 | 健康检查 | P0 | 容器已启动 | 1. GET `/ping` | 无 | 201，body=`Created` |
| TC-AU-01 | 合法账号获取 token | 鉴权 | P0 | 服务可用 | 1. POST `/auth` | `.env` 账号密码 | 200，body 含 `token` |
| TC-AU-02 | 非法账号无法获取 token | 鉴权 | P1 | 服务可用 | 1. POST `/auth` 传非法凭据 | `invalid_auth.json` 四组：空用户/空密码/错密码/不存在用户 | 200，无 token，`reason=Bad credentials` |
| TC-AU-03 | 无 token 不能全量更新 | 鉴权 | P1 | 已有一条预订 | 1. PUT `/booking/{id}` 不带 Cookie | 改 firstname | 403 |
| TC-AU-04 | 无 token 不能删除 | 鉴权 | P1 | 已有一条预订 | 1. DELETE `/booking/{id}` 不带 Cookie | 已有 id | 403 |
| TC-AU-05 | 伪造 token 不能更新 | 鉴权 | P2 | 已有一条预订 | 1. Cookie 换成非法 token 2. PUT `/booking/{id}` | `token=invalid-token` | 403 |
| TC-AU-06 | Basic Auth 可以删除 | 鉴权 | P2 | 服务可用 | 1. POST 创建 2. DELETE，用 Basic Auth、不带 token 3. GET 该 id | `.env` 账号；新建预订 | 删除 201；再查 404 |
| TC-BK-01 | 创建预订 | 预订 CRUD | P0 | 已登录 | 1. POST `/booking` 2. 清理删除 | `booking.json`（唯一姓名） | 200，含 `bookingid`，回显字段一致 |
| TC-BK-02 | 按 ID 查询 | 预订 CRUD | P1 | 已创建预订 | 1. GET `/booking/{id}` | 夹具中的 id | 200，字段与创建时一致 |
| TC-BK-03 | 按 firstname 过滤 | 预订 CRUD | P2 | 已创建预订 | 1. GET `/booking?firstname=` | 该条 firstname | 200，id 列表包含该预订 |
| TC-BK-04 | 按 lastname 过滤 | 预订 CRUD | P2 | 已创建预订 | 1. GET `/booking?lastname=` | 该条 lastname | 200，id 列表包含该预订 |
| TC-BK-05 | 全量更新 | 预订 CRUD | P1 | 已创建预订、已登录 | 1. PUT 改姓名/价格/需求 2. GET 复核 | firstname+`Upd`，price=999，needs=`Lunch` | 两次均为 200，字段已更新 |
| TC-BK-06 | 部分更新 | 预订 CRUD | P2 | 已创建预订、已登录 | 1. PATCH 只改 additionalneeds | `Late Checkout` | 200；该字段变、firstname 不变 |
| TC-BK-07 | 删除预订 | 预订 CRUD | P1 | 已登录 | 1. POST 创建 2. DELETE 3. GET | 新建预订 | 删除 201/`Created`；再查 404 |
| TC-NG-01 | 查询不存在的预订 | 预订负向 | P2 | 服务可用 | 1. GET `/booking/999999` | id=999999 | 404 |
| TC-NG-02 | 缺少必填字段创建 | 预订负向 | P2 | 服务可用 | 1. POST `/booking` 只传 firstname | `{"firstname":"Incomplete"}` | 500（服务未校验，已知缺陷） |
| TC-NG-03 | 删除不存在的预订 | 预订负向 | P2 | 已登录 | 1. DELETE `/booking/999999` | id=999999 | 405（官方实现，非 404） |

