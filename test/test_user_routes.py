import json
from test import BaseTestAdmin, BaseTestClass, BaseTestUser

import pytest
from project import db
from project.user.models import User


@pytest.fixture()
def setup(request):
    print("\n Fixutre Setup")

    def tear():
        print("\n Teardown Fixture")

    request.addfinalizer(tear)


class TestLogin(BaseTestUser):

    url = "/login"

    def test_login_success(self, setup):
        print("testing login success")
        response = self.client.get(
            self.url, headers={"Authorization": f"Basic {self.credentials}"})
        token = json.loads(response.data)["token"]
        assert response.status_code == 200 and token != None and token != ''

    def test_login_unauthorized(self, setup):
        print("testing login unauthorized")
        response = self.client.get(
            self.url, headers={"Authorization": f"Basic wrongnameandpassword"})
        assert response.status_code == 401


class TestAbout(BaseTestUser):

    url = "/about"

    def test_about_response(self):

        response = self.client.get(
            self.url, headers={"Authorization": f"Bearer {self.token}"})
        about = json.loads(response.data)
        assert about["user"]["name"] == self.username

    def test_about_response_sad(self):
        response = self.client.get(
            self.url, headers={"Authorization":\
                 f"jlfksjiojefjlksjf"})
        assert response.status_code == 401


class TestAdmin(BaseTestAdmin):

    def test_gettall_users(self):

        response = self.client.get(
            self.get_all_users_url,
            headers={"Authorization": f"Bearer {self.token}"})
        users = json.loads(response.data)
        assert users != None

    def test_admin_can_promote(self):

        response = self.client.put(
            self.promote_url,
            headers={"Authorization":\
                 f"Bearer {self.token}"})
        response = json.loads(response.data)["admin"]
        assert response == True

    def test_admin_can_demote(self):

        response = self.client.put(
            self.demote_url,
            headers={"Authorization": f"Bearer {self.token}"})
        response = json.loads(response.data)["admin"]
        assert response == False

    def test_admin_can_delete_user(self):
        with self.app_ctx:
            user = User(public_id="twer43vc435vt",
                        name="fadfsdfafacvvzv6765",
                        password="test",
                        admin=False)
            db.session.add(user)
            db.session.commit()
        response = self.client.delete(
            self.delete_user_url,
            headers={"Authorization": f"Bearer {self.token}"})
        assert response.status_code == 200


class TestNonAdmin(BaseTestUser):

    def test_non_admin_cannot_get_users(self):
        response = self.client.get(
            self.get_all_users_url,
            headers={"Authorization": f"Bearer {self.token}"})
        assert response.status_code == 403

    def test_non_admin_cannot_get_any_single_user_details(self):

        response = self.client.get(
            self.get_one_user_url,
            headers={"Authorization": f"Bearer {self.token}"})
        assert response.status_code == 403

    def test_user_can_create_new_user(self):
        response = self.client.\
            post("/user",
                 data=json.dumps(dict(
                     name="testnewuser",
                     password="testnewuserpassword"
                 )), content_type='application/json')
        print(response.status)
        with self.app_ctx:
            user = User.query.\
                filter_by(name="testnewuser").\
                first()
            db.session.delete(user)
            db.session.commit()
        assert response.status_code == 201
