import base64
import json

from project import create_app


class BaseTestClass:

    get_all_users_url = "/users"
    get_one_user_url = "/user/68999207-14ed-4e8b-8372-f91ceb672855"
    login_url = "/login"
    promote_url = "/admin/promote/68999207-14ed-4e8b-8372-f91ceb672855"
    demote_url = "/admin/demote/68999207-14ed-4e8b-8372-f91ceb672855"
    delete_user_url = "/admin/delete/twer43vc435vt"

    app = create_app()
    app_ctx = app.app_context()
    app_ctx.push()
    client = app.test_client()


class BaseTestUser(BaseTestClass):
    username = "KateRock"
    password = "12345"
    credentials = f"{username}:{password}"
    credentials = base64.b64encode(bytes(credentials, "utf-8")).decode("utf-8")
    response = BaseTestClass.client.get(
        "/login", headers={"Authorization": f"Basic {credentials}"})
    token = json.loads(response.data)["token"]

class BaseTestAdmin(BaseTestClass):
    username = "Admin"
    password = "12345"
    credentials = f"{username}:{password}"
    credentials = base64.b64encode(bytes(credentials, "utf-8")).decode("utf-8")
    response = BaseTestClass.client.get(
        "/login", headers={"Authorization": f"Basic {credentials}"})
    token = json.loads(response.data)["token"]
