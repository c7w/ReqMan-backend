from django.test import TestCase
from django.test import Client as DefaultClient
from ums.models import *
import json
from ums.views import EMAIL_EXPIRE_SECONDS, RESETTING_STATUS_EXPIRE_SECONDS
import ums.utils

SUCC = {"code": 0}
FAIL = {"code": 1}


class Client(DefaultClient):
    """
    for copy cookie sessionId into respective method body
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def _add_cookie(self, kw):
        if "sessionId" in self.cookies:
            if "data" not in kw:
                kw["data"] = {}
            kw["data"]["sessionId"] = self.cookies["sessionId"].value
        return kw

    def post(self, *args, **kw):
        return super(Client, self).post(*args, **self._add_cookie(kw))

    def get(self, *args, **kw):
        return super(Client, self).get(*args, **self._add_cookie(kw))


class UMS_Tests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create(
            name="Alice", password="123456", email="alice@secoder.net"
        )
        self.u2 = User.objects.create(
            name="Bob", password="789123", email="bob@secoder.net"
        )
        self.u3 = User.objects.create(
            name="Caorl", password="159357", email="carol@secoder.net"
        )
        self.u4 = User.objects.create(
            name="Fra", password="159357", email="fra@secoder.net"
        )

        self.p1 = Project.objects.create(title="ProjTit1", description="Desc1")
        self.p2 = Project.objects.create(title="ProjTit2", description="Desc2")
        self.p3 = Project.objects.create(title="ProjTit3", description="Desc3")

        UserProjectAssociation.objects.create(
            user=self.u1, project=self.p1, role=Role.SUPERMASTER
        )
        UserProjectAssociation.objects.create(
            user=self.u1, project=self.p2, role=Role.DEV
        )
        UserProjectAssociation.objects.create(
            user=self.u2, project=self.p1, role=Role.DEV
        )
        UserProjectAssociation.objects.create(
            user=self.u3, project=self.p2, role=Role.SUPERMASTER
        )

    """
    create a template client as u1
    """

    def login_u1(self, sess):
        c = Client()
        c.cookies["sessionId"] = sess

        c.post(
            "/ums/login/",
            data={"identity": self.u1.name, "password": self.u1.password},
            content_type="application/json",
        )

        return c

    """
    illegal cookie
    """

    def test_lacking_cookie(self):
        c = Client()
        resp = c.post("/ums/login/")
        self.assertEqual(resp.json()["code"], -4)

    """
    /ums/login/
    """

    def test_login(self):
        c = Client()

        c.cookies["sessionId"] = "0"
        resp = c.post(
            "/ums/login/",
            data={"identity": self.u1.name * 2, "password": self.u1.password},
            content_type="application/json",
        )
        self.assertEqual(resp.json(), {"code": 2})

        c.cookies["sessionId"] = "0"
        resp = c.post(
            "/ums/login/",
            data={"identity": self.u1.name, "password": self.u1.password * 2},
            content_type="application/json",
        )
        self.assertEqual(resp.json(), {"code": 3})

        c.cookies["sessionId"] = "0"
        resp = c.post(
            "/ums/login/",
            data={"identity": self.u1.name, "password": self.u1.password},
            content_type="application/json",
        )
        self.assertEqual(resp.json(), {"code": 0})

        c.cookies["sessionId"] = "1"
        resp = c.post(
            "/ums/login/",
            data={"identity": self.u1.email, "password": self.u1.password},
            content_type="application/json",
        )
        self.assertEqual(resp.json(), {"code": 0})

        c.cookies["sessionId"] = "2"
        resp = c.post(
            "/ums/login/",
            data={"identity": self.u1.email + "cccccc", "password": self.u1.password},
            content_type="application/json",
        )
        self.assertEqual(resp.json(), {"code": 2})

        c.cookies["sessionId"] = "3"
        resp = c.post(
            "/ums/login/",
            data={"identity": self.u1.email, "password": self.u1.password + "cccccc"},
            content_type="application/json",
        )
        self.assertEqual(resp.json(), {"code": 3})

        c.cookies["sessionId"] = "3"
        resp = c.post(
            "/ums/login/",
            data={
                "identity": "non" + self.u1.email,
                "password": self.u1.password + "cccccc",
            },
            content_type="application/json",
        )
        self.assertEqual(resp.json(), {"code": 2})

        c.cookies["sessionId"] = "4"
        resp = c.post(
            "/ums/login/",
            data={"identity": self.u1.email, "password": self.u1.password},
            content_type="application/json",
        )
        self.assertEqual(resp.json(), {"code": 0})

        c.cookies["sessionId"] = "4"
        resp = c.post(
            "/ums/login/",
            data={"identity": self.u1.email, "password": self.u1.password},
            content_type="application/json",
        )
        self.assertEqual(resp.json(), {"code": 1})

    """
    /ums/logout
    """

    def test_logout(self):
        c = self.login_u1("5")

        resp = c.post("/ums/logout/")
        self.assertEqual(resp.json()["code"], 0)

        resp = c.post("/ums/logout/")
        self.assertEqual(resp.json()["code"], 1)

    """
    /ums/user/
    """

    def test_user(self):
        c = self.login_u1("6")
        resp = c.get("/ums/user/")
        self.assertEqual(resp.json()["data"]["user"]["id"], self.u1.id)
        self.assertEqual(len(resp.json()["data"]["projects"]), 2)

        # logout leads to fail
        c.post("/ums/logout/")
        resp = c.get("/ums/user/")
        self.assertEqual(resp.json()["code"], -2)

    """
    /ums/check_username_available
    """

    def test_check_username_av(self):
        c = Client()
        c.cookies["sessionId"] = "7"
        resp = c.post(
            "/ums/check_username_available/",
            data={"name": "Alice"},
            content_type="application/json",
        )
        self.assertEqual(resp.json(), FAIL)

        resp = c.post(
            "/ums/check_username_available/",
            data={"name": "Eve"},
            content_type="application/json",
        )
        self.assertEqual(resp.json(), SUCC)

    """
    /ums/check_email_available/`
    """

    def test_check_email_av(self):
        c = Client()
        c.cookies["sessionId"] = "8"
        resp = c.post(
            "/ums/check_email_available/",
            data={"email": "ALICE@secoder.net"},
            content_type="application/json",
        )
        self.assertEqual(resp.json(), FAIL)

        resp = c.post(
            "/ums/check_email_available/",
            data={"email": "hey@secoder.net"},
            content_type="application/json",
        )
        self.assertEqual(resp.json(), SUCC)

    """
     /ums/project/
    """

    def test_project(self):
        c = Client()
        c.cookies["sessionId"] = "9"
        c.post(
            "/ums/login/",
            data={"identity": self.u2.email, "password": self.u2.password},
            content_type="application/json",
        )

        # invalid project id
        resp = c.post(
            "/ums/project/", data={"project": 999}, content_type="application/json"
        )
        self.assertNotEqual(resp.json()["code"], 0)

        # not in project
        resp = c.post(
            "/ums/project/",
            data={"project": self.p2.id},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], -2)

        # successful
        resp = c.post(
            "/ums/project/",
            data={"project": self.p1.id},
            content_type="application/json",
        ).json()
        self.assertEqual(resp["code"], 0)
        self.assertNotEqual(resp["data"]["users"][0]["role"], "")
        # self.assertIn("avatar", resp["data"])

    """
    /ums/modify_project/
    """

    def test_modify_project(self):
        c = self.login_u1("10")

        # not supermaster
        resp = c.post(
            "/ums/modify_project/",
            data={"project": self.p2.id, "title": "t", "description": "d"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], -2)

        # invalid project id
        resp = c.post(
            "/ums/modify_project/",
            data={"project": 9801},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], -1)

        # successful
        resp = c.post(
            "/ums/modify_project/",
            data={"project": self.p1.id, "title": "NewTitle", "description": "NewDesc"},
            content_type="application/json",
        )
        self.p1 = Project.objects.get(id=self.p1.id)  # refresh model
        self.assertEqual(resp.json()["code"], 0)
        self.assertEqual(self.p1.title, "NewTitle")
        self.assertEqual(self.p1.description, "NewDesc")

        resp = c.post(
            "/ums/modify_project/",
            data={
                "project": self.p1.id,
                "title": "t" * PROJECT_TITLE_LEN + "t",
                "description": "NewDesc",
            },
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 1)

        resp = c.post(
            "/ums/modify_project/",
            data={
                "project": self.p1.id,
                "title": "NewTitle",
                "description": "d" * PROJECT_DESC_LEN + "d",
            },
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 2)

    def inv_legal_check(self, resp):
        inv = resp.json()["data"]["invitation"]
        self.assertEqual(resp.json()["code"], 0)
        self.assertEqual(len(inv), 8)
        self.assertEqual(
            inv,
            ProjectInvitationAssociation.objects.filter(
                project=self.p1,
            )
            .first()
            .invitation,
        )
        return inv

    def get_inv_for(self, c, proj_id):
        return c.post(
            "/ums/get_invitation/",
            data={
                "project": proj_id,
            },
            content_type="application/json",
        )

    """
    /ums/get_invitation/
    """

    def test_get_invitation(self):
        c = self.login_u1("11")

        # not supermaster
        resp = self.get_inv_for(c, self.p2.id)
        self.assertEqual(resp.json()["code"], -2)

        # invalid project id
        resp = self.get_inv_for(c, 9999)
        self.assertEqual(resp.json()["code"], -1)

        # successful
        resp = self.get_inv_for(c, self.p1.id)
        inv = self.inv_legal_check(resp)

        # do not change
        resp = self.get_inv_for(c, self.p1.id)
        self.assertEqual(resp.json()["code"], 0)
        self.assertEqual(resp.json()["data"]["invitation"], inv)
        ProjectInvitationAssociation.objects.filter(project=self.p1).delete()

    """
    /ums/refresh_invitation/
    """

    def test_refresh_invitation(self):
        c = self.login_u1("12")

        # not supermaster
        resp = c.post(
            "/ums/refresh_invitation/",
            data={
                "project": self.p2.id,
            },
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], -2)

        # invalid project id
        resp = c.post(
            "/ums/refresh_invitation/",
            data={"project": 7777},
            content_type="application/json",
        )
        self.assertNotEqual(resp.json()["code"], 0)

        # successful
        resp = c.post(
            "/ums/refresh_invitation/",
            data={
                "project": self.p1.id,
            },
            content_type="application/json",
        )
        inv = self.inv_legal_check(resp)

        # do change
        resp = c.post(
            "/ums/refresh_invitation/",
            data={
                "project": self.p1.id,
            },
            content_type="application/json",
        )
        inv2 = self.inv_legal_check(resp)
        self.assertNotEqual(resp.json()["data"]["invitation"], inv)

    """
    /ums/modify_user_role/
    """

    def test_modify_user_role(self):
        c = self.login_u1("13")

        # not supermaster
        resp = c.post(
            "/ums/modify_user_role/",
            data={"project": self.p2.id, "user": self.u2.id, "role": Role.SUPERMASTER},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], -2)

        # invalid project id
        resp = c.post(
            "/ums/modify_user_role/",
            data={"project": -1, "user": self.u2.id, "role": Role.SUPERMASTER},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], -1)

        # invalid role
        resp = c.post(
            "/ums/modify_user_role/",
            data={"project": self.p1.id, "user": self.u2.id, "role": "undefined"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 1)

        # not in project
        resp = c.post(
            "/ums/modify_user_role/",
            data={"project": self.p1.id, "user": self.u3.id, "role": Role.DEV},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 1)

        # successful
        resp = c.post(
            "/ums/modify_user_role/",
            data={"project": self.p1.id, "user": self.u2.id, "role": Role.MEMBER},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 0)
        self.assertEqual(
            UserProjectAssociation.objects.filter(user=self.u2, project=self.p1)
            .first()
            .role,
            Role.MEMBER,
        )

    """
    /ums/project_add_user/
    """

    def test_project_add_user(self):
        c = self.login_u1("14")
        url = "/ums/project_add_user/"

        # not supermaster
        resp = c.post(
            url,
            data={"project": self.p3.id, "user": self.u3.id, "role": Role.MEMBER},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], -2)

        # invalid project id
        resp = c.post(
            url,
            data={"project": -1, "user": self.u3.id, "role": Role.SUPERMASTER},
            content_type="application/json",
        )
        self.assertNotEqual(resp.json()["code"], 0)

        # invalid user id
        resp = c.post(
            url,
            data={"project": self.p1.id, "user": 9999999, "role": Role.SUPERMASTER},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 3)

        # invalid role
        resp = c.post(
            url,
            data={"project": self.p1.id, "user": self.u3.id, "role": "undefined"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 1)

        # in project
        resp = c.post(
            url,
            data={"project": self.p1.id, "user": self.u2.id, "role": Role.DEV},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 1)

        # successful
        resp = c.post(
            url,
            data={"project": self.p1.id, "user": self.u3.id, "role": Role.MEMBER},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 0)
        self.assertEqual(
            UserProjectAssociation.objects.filter(user=self.u3, project=self.p1)
            .first()
            .role,
            Role.MEMBER,
        )

    """
    /ums/project_rm_user/
    """

    def test_project_rm_user(self):
        c = self.login_u1("15")
        url = "/ums/project_rm_user/"

        # not supermaster
        resp = c.post(
            url,
            data={
                "project": self.p2.id,
                "user": self.u2.id,
            },
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], -2)

        # invalid project id
        resp = c.post(
            url,
            data={
                "project": -1,
                "user": self.u3.id,
            },
            content_type="application/json",
        )
        self.assertNotEqual(resp.json()["code"], 0)

        # successful
        resp = c.post(
            url,
            data={
                "project": self.p1.id,
                "user": self.u2.id,
            },
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 0)
        self.assertEqual(
            UserProjectAssociation.objects.filter(
                user=self.u2, project=self.p1
            ).first(),
            None,
        )

        # not in project
        resp = c.post(
            url,
            data={
                "project": self.p1.id,
                "user": self.u2.id,
            },
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 1)

    """
    /ums/register/
    """

    def test_register(self):
        url = "/ums/register/"
        c = Client()
        c.cookies["sessionId"] = "16"

        d = self.login_u1("17")
        self.get_inv_for(d, self.p1.id)
        self.assertNotEqual(len(ProjectInvitationAssociation.objects.all()), 0)

        # invalid invitation
        resp = c.post(
            url,
            data={
                "name": "Dave",
                "password": "Dave123456",
                "email": "dave@secoder.net",
                "invitation": "invalid",
            },
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 2)

        # successful with invitation
        inv = ProjectInvitationAssociation.objects.filter(project=self.p1).first()
        resp = c.post(
            url,
            data={
                "name": "Dave",
                "password": "Dave123456",
                "email": "dave@secoder.net",
                "invitation": inv.invitation,
            },
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 0)
        new_user = User.objects.filter(name="Dave").first()
        self.assertEqual(new_user.email, "dave@secoder.net")
        self.assertEqual(new_user.password, "Dave123456")
        self.assertEqual(
            UserProjectAssociation.objects.filter(project=inv.project, user=new_user)
            .first()
            .role,
            inv.role,
        )

        # user will not register after login
        resp = d.post(
            url,
            data={
                "name": "Eve",
                "password": "Eve123456",
                "email": "eve@secoder.net",
            },
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 1)

        c = Client()
        c.cookies["sessionId"] = "18"

        # successful without invitation
        resp = c.post(
            url,
            data={
                "name": "Eve",
                "password": "Eve123456",
                "email": "eve@secoder.net",
            },
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 0)
        new_user = User.objects.filter(name="Eve").first()
        self.assertEqual(new_user.email, "eve@secoder.net")
        self.assertEqual(new_user.password, "Eve123456")
        self.assertEqual(len(UserProjectAssociation.objects.filter(user=new_user)), 0)

        # dup name
        resp = c.post(
            url,
            data={
                "name": "eve",
                "password": "Eve123456",
                "email": "eve_dup_name@secoder.net",
            },
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 1)

        # dup email
        resp = c.post(
            url,
            data={
                "name": "EEE",
                "password": "Eve123456",
                "email": "EVE@secoder.net",
            },
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 1)

    # """
    # frequent request should be throttled
    # """
    #
    # def test_throttle(self):
    #     url = "/ums/login/"
    #     c = Client()
    #     c.cookies["sessionId"] = "19"
    #     for i in range(100):
    #         resp = c.post(url, data={})
    #         if resp.json()["code"] == -3:
    #             return
    #     raise AssertionError

    def test_modify_password(self):
        c = self.login_u1("20")
        url = "/ums/modify_password/"

        # fail because password do not match

        resp = c.post(
            url, data={"prev": self.u1.password + "_", "curr": "none sense"}
        ).json()
        self.assertEqual(2, resp["code"])

        # succ
        now = self.u1.password + "_"
        resp = c.post(url, data={"prev": self.u1.password, "curr": now}).json()
        self.assertEqual(0, resp["code"])
        self.u1.refresh_from_db()
        self.assertEqual(self.u1.password, now)

        # fail because has not logged in
        c = Client()
        c.cookies["sessionId"] = "21"
        resp = c.post(url, data={"prev": self.u1.password, "curr": "none sense"}).json()
        self.assertEqual(-2, resp["code"])

    def test_upload_user_avatar(self):
        c = self.login_u1("20")
        url = "/ums/upload_user_avatar/"

        resp = c.post(url, data={"avatar": "test_avatar"}).json()
        self.assertEqual(0, resp["code"])
        self.u1 = User.objects.get(id=self.u1.id)
        self.assertEqual(self.u1.avatar, "test_avatar")

    def test_create_project(self):
        c = self.login_u1("21")
        data = {
            "title": "test_title_create_project",
            "description": "test_desc_create_project",
        }
        resp = c.post("/ums/create_project/", data=data.copy()).json()

        self.assertEqual(resp["code"], 0)
        self.assertNotEqual(Project.objects.filter(**data).first(), None)

        data = {
            "title": "test_title_create_project",
            "description": "t" * PROJECT_DESC_LEN + "t",
        }
        resp = c.post("/ums/create_project/", data=data.copy()).json()

        self.assertEqual(resp["code"], 2)

        data = {
            "title": "t" * PROJECT_TITLE_LEN + "t",
            "description": "t",
        }
        resp = c.post("/ums/create_project/", data=data.copy()).json()

        self.assertEqual(resp["code"], 1)

    def test_upload_project_avatar(self):
        c = self.login_u1("22")
        url = "/ums/upload_project_avatar/"
        avatar = "test_avat"

        resp = c.post(url, data={"avatar": avatar, "project": self.p1.id}).json()
        # print(resp)
        self.assertEqual(resp["code"], 0)

        resp = c.post("/ums/project/", data={"project": self.p1.id}).json()
        self.assertEqual(resp["code"], 0)
        # self.assertEqual(resp["data"]["avatar"], avatar)

    def test_user_join_project_invitation(self):
        c = self.login_u1("24")
        url = "/ums/user_join_project_invitation/"
        self.get_inv_for(c, self.p1.id)

        # reject already in
        resp = c.post(
            url,
            data={
                "invitation": ProjectInvitationAssociation.objects.filter(
                    project=self.p1
                )
                .first()
                .invitation
            },
        ).json()
        self.assertEqual(resp["code"], 1)

        # invalid inviatation
        resp = c.post(url, data={"invitation": "invalid"}).json()
        self.assertEqual(resp["code"], 2)

        c = Client()
        c.cookies["sessionId"] = "25"
        c.post(
            "/ums/login/",
            data={"identity": self.u4.name, "password": self.u4.password},
            content_type="application/json",
        )
        resp = c.post(
            url,
            data={
                "invitation": ProjectInvitationAssociation.objects.filter(
                    project=self.p1
                )
                .first()
                .invitation
            },
        ).json()
        self.assertEqual(resp["code"], 0)
        self.assertNotEqual(
            UserProjectAssociation.objects.filter(
                user=self.u4, project=self.p1
            ).first(),
            None,
        )

        # unlogin, rej
        c = Client()
        c.cookies["sessionId"] = "26"
        resp = c.post(
            url,
            data={
                "invitation": ProjectInvitationAssociation.objects.filter(
                    project=self.p1
                )
                .first()
                .invitation
            },
        ).json()
        self.assertEqual(resp["code"], -2)

    def test_user_exist(self):
        c = self.login_u1("23")
        d = DefaultClient()
        url = "/ums/user_exist/"

        # parameter failures
        resp = c.post(url, data={"project": self.p1.id, "identity": ""}).json()
        self.assertEqual(resp["code"], -1)
        resp = d.post(
            url,
            json.dumps(
                {
                    "project": self.p1.id,
                    "identity": {"type": "unsupported"},
                    "sessionId": "23",
                }
            ),
            content_type="application/json",
        ).json()
        self.assertEqual(resp["code"], -1)
        resp = d.post(
            url,
            json.dumps(
                {"project": self.p1.id, "identity": {"type": "id"}, "sessionId": "23"}
            ),
            content_type="application/json",
        ).json()
        self.assertEqual(resp["code"], -1)

        # non-exist
        resp = d.post(
            url,
            json.dumps(
                {
                    "project": self.p1.id,
                    "identity": {"type": "id", "key": 999999},
                    "sessionId": "23",
                }
            ),
            content_type="application/json",
        ).json()
        self.assertEqual(resp["code"], 0)
        self.assertEqual(resp["data"]["exist"], False)

        # exist
        def successful_judge(data):
            data["sessionId"] = "23"
            resp = d.post(url, json.dumps(data), content_type="application/json").json()
            self.assertEqual(resp["code"], 0)
            self.assertEqual(resp["data"]["exist"], True)
            self.assertEqual(resp["data"]["user"]["id"], self.u3.id)

        successful_judge(
            {"project": self.p1.id, "identity": {"type": "id", "key": self.u3.id}}
        )
        successful_judge(
            {"project": self.p1.id, "identity": {"type": "email", "key": self.u3.email}}
        )
        successful_judge(
            {"project": self.p1.id, "identity": {"type": "name", "key": self.u3.name}}
        )

    def test_email_modify_password(self):
        c = Client()
        c.cookies["sessionId"] = "26"

        url1 = "/ums/email_modify_password_request/"
        url2 = "/ums/email_modify_password_callback/"

        PendingModifyPasswordEmail.objects.all().delete()

        # non-exist email
        resp = c.post(url1, data={"email": "invalid"}).json()
        self.assertEqual(resp["code"], 2)
        self.assertEqual(len(PendingModifyPasswordEmail.objects.all()), 0)

        # non-verified email
        # resp = c.post(url1, data={"email": self.u1.email}).json()
        # self.assertEqual(resp["code"], 2)
        # self.assertEqual(len(PendingModifyPasswordEmail.objects.all()), 0)

        # add verified tag
        self.u1.email_verified = True
        self.u1.save()

        # request successful
        # as a unit test, I do not judge if the mail has been sent or not
        resp = c.post(url1, data={"email": self.u1.email}).json()
        # self.assertEqual(resp['code'], 0)
        self.assertEqual(len(PendingModifyPasswordEmail.objects.all()), 1)

        # stage 1: email expired
        relation = PendingModifyPasswordEmail.objects.filter(
            email=self.u1.email
        ).first()
        original_createdAt = float(relation.createdAt)
        relation.createdAt -= EMAIL_EXPIRE_SECONDS * 2
        relation.save()
        hash1 = relation.hash1
        resp = c.post(url2, data={"hash1": hash1, "stage": 1}).json()
        self.assertEqual(resp["code"], 2)
        relation.createdAt = original_createdAt
        relation.save()

        # stage 1: successful
        hash1 = (
            PendingModifyPasswordEmail.objects.filter(email=self.u1.email).first().hash1
        )
        resp = c.post(url2, data={"hash1": hash1, "stage": 1}).json()
        self.assertEqual(resp["code"], 0)
        print(resp)
        hash2 = resp["data"]["hash2"]

        # stage1: hash1 verified
        resp = c.post(url2, data={"hash1": hash1, "stage": 1}).json()
        self.assertEqual(resp["code"], 1)

        # stage2: resetting status expired
        relation = PendingModifyPasswordEmail.objects.filter(
            email=self.u1.email
        ).first()
        original_beginAt = relation.beginAt
        relation.beginAt -= RESETTING_STATUS_EXPIRE_SECONDS + 1
        relation.save()
        resp = c.post(
            url2,
            data={
                "hash1": hash1,
                "hash2": hash2,
                "stage": 2,
                "password": "new_password",
            },
        ).json()
        self.assertEqual(resp["code"], 2)
        relation.beginAt = original_beginAt
        relation.save()

        # stage2: successful
        resp = c.post(
            url2,
            data={
                "hash1": hash1,
                "hash2": hash2,
                "stage": 2,
                "password": "new_password",
            },
        ).json()
        self.assertEqual(resp["code"], 0)
        self.u1.refresh_from_db()
        self.assertEqual(self.u1.password, "new_password")
        self.assertEqual(len(PendingModifyPasswordEmail.objects.all()), 0)

        # stage2: no relation
        resp = c.post(
            url2,
            data={
                "hash1": hash1,
                "hash2": hash2,
                "stage": 2,
                "password": "new_password",
            },
        ).json()
        self.assertEqual(resp["code"], 1)

        # invalid stage
        resp = c.post(url2, data={"hash1": hash1, "stage": -1}).json()
        self.assertEqual(resp["code"], -1)

    def test_email_request_bad_parameters(self):
        c = self.login_u1("27")
        url = "/ums/email_request/"
        resp = c.post(
            url, data={"email": "ill_email", "op": "ill_op", "type": "ill_type"}
        ).json()
        self.assertEqual(resp["code"], -1)
        resp = c.post(
            url, data={"email": "ill_email", "op": "ill_op", "type": "major"}
        ).json()
        self.assertEqual(resp["code"], 6)
        resp = c.post(
            url, data={"email": "e@e.cn", "op": "add", "type": "major"}
        ).json()
        self.assertEqual(resp["code"], -1)
        resp = c.post(
            url, data={"email": "e@e.cn", "op": "none_sense", "type": "minor"}
        ).json()
        self.assertEqual(resp["code"], -1)

    def test_email_major_verification(self):
        c = self.login_u1("28")
        url1 = "/ums/email_request/"
        url2 = "/ums/email_verify_callback/"
        self.u1.email_verified = True

        # 8 modify: same
        resp = c.post(
            url1, data={"email": self.u1.email, "type": "major", "op": "modify"}
        ).json()
        self.assertEqual(resp["code"], 8)

        # 0 modify: success
        def succ():
            resp = c.post(
                url1, data={"email": "new@secoder.com", "type": "major", "op": "modify"}
            ).json()
            self.assertIn(resp["code"], [0, 1])
            self.u1.refresh_from_db()
            self.assertEqual(self.u1.email, "new@secoder.com")
            self.assertEqual(self.u1.email_verified, False)

        succ()

        # 0 modify: too freq
        resp = c.post(
            url1, data={"email": "new2@secoder.com", "type": "major", "op": "modify"}
        ).json()
        self.assertEqual(resp["code"], 2)
        self.u1.refresh_from_db()
        self.assertEqual(self.u1.email, "new2@secoder.com")
        self.assertEqual(self.u1.email_verified, False)

        # 2 verify expire
        relation = PendingVerifyEmail.objects.filter(
            email="new@secoder.com"  # the previous one
        ).first()
        original_createdAt = float(relation.createdAt)
        relation.createdAt -= EMAIL_EXPIRE_SECONDS * 2
        relation.save()
        resp = c.post(url2, data={"hash": relation.hash}).json()
        self.assertEqual(resp["code"], 2)
        relation.createdAt = original_createdAt
        relation.save()

        # 3 verify collision
        resp = c.post(url2, data={"hash": relation.hash}).json()
        self.assertEqual(resp["code"], 3)
        self.assertEqual(PendingVerifyEmail.objects.all().__len__(), 0)

        # 0 modify: success
        succ()
        relation = PendingVerifyEmail.objects.filter(email=self.u1.email).first()
        resp = c.post(url2, data={"hash": relation.hash}).json()
        self.assertEqual(PendingVerifyEmail.objects.all().__len__(), 0)
        self.assertEqual(resp["code"], 0)
        self.u1.refresh_from_db()
        self.assertEqual(self.u1.email_verified, True)

        # 7: verify: already verified
        resp = c.post(
            url1, data={"email": self.u1.email, "type": "major", "op": "verify"}
        ).json()
        self.assertEqual(resp["code"], 7)

        # 0: verify: successful
        self.u1.email_verified = False
        self.u1.save()
        resp = c.post(
            url1, data={"email": self.u1.email, "type": "major", "op": "verify"}
        ).json()
        self.assertIn(resp["code"], [0, 1])

    def test_email_minor_verification(self):
        c = self.login_u1("29")
        url1 = "/ums/email_request/"
        url2 = "/ums/email_verify_callback/"
        PendingVerifyEmail.objects.all().delete()

        # 5: rm: non-exist
        resp = c.post(
            url1, data={"email": self.u1.email, "type": "minor", "op": "rm"}
        ).json()
        self.assertEqual(resp["code"], 5)

        # 3: add: same with major
        resp = c.post(
            url1, data={"email": self.u1.email, "type": "minor", "op": "add"}
        ).json()
        self.assertEqual(resp["code"], 3)

        # 4: add: already exist
        UserMinorEmailAssociation.objects.create(user=self.u1, email="test@test.com")
        resp = c.post(
            url1, data={"email": "test@test.com", "type": "minor", "op": "add"}
        ).json()
        self.assertEqual(resp["code"], 4)

        # 0: modify: successful
        resp = c.post(
            url1,
            data={
                "previous": "test@test.com",
                "email": "test2@test.com",
                "type": "minor",
                "op": "modify",
            },
        ).json()
        self.assertIn(resp["code"], [0, 1])

        # 2: add: too frequent
        resp = c.post(
            url1, data={"email": "new_one@test.com", "type": "minor", "op": "add"}
        ).json()
        self.assertEqual(resp["code"], 2)

        # 5: modify: non-exist
        resp = c.post(
            url1,
            data={
                "previous": "test@test.com",
                "email": "test3@test.com",
                "type": "minor",
                "op": "modify",
            },
        ).json()
        self.assertEqual(resp["code"], 5)

        # 6: modify: ill_email
        resp = c.post(
            url1,
            data={
                "previous": "test.com",
                "email": "ii@test.com",
                "type": "minor",
                "op": "modify",
            },
        ).json()
        self.assertEqual(resp["code"], 6)

        # 2: verify: frequency
        resp = c.post(
            url1, data={"email": "new_one@test.com", "type": "minor", "op": "verify"}
        ).json()
        self.assertEqual(resp["code"], 2)

        # 10: verify: non-exist
        resp = c.post(
            url1, data={"email": "none@test.com", "type": "minor", "op": "verify"}
        ).json()
        self.assertEqual(resp["code"], 10)

        # 0: verify: successful
        PendingVerifyEmail.objects.all().delete()
        resp = c.post(
            url1, data={"email": "new_one@test.com", "type": "minor", "op": "verify"}
        ).json()
        self.assertIn(resp["code"], [0, 1])

        # 7: already verified
        assoc = UserMinorEmailAssociation.objects.get(email="new_one@test.com")
        assoc.verified = True
        assoc.save()
        resp = c.post(
            url1, data={"email": "new_one@test.com", "type": "minor", "op": "verify"}
        ).json()
        self.assertEqual(resp["code"], 7)

        # verifications
        PendingVerifyEmail.objects.all().delete()
        UserMinorEmailAssociation.objects.create(user=self.u1, email="verify@test.com")
        relation = PendingVerifyEmail.objects.create(
            user=self.u1, email="verify2@test.com", hash="test_hash", is_major=False
        )

        # 1: non-exist hash
        resp = c.post(url2, data={"hash": "non-exist"}).json()
        self.assertEqual(resp["code"], 1)

        # 3: no matching minor email
        resp = c.post(url2, data={"hash": "test_hash"}).json()
        self.assertEqual(resp["code"], 3)

        relation.email = "verify@test.com"
        relation.save()

        # 0: successful
        resp = c.post(url2, data={"hash": "test_hash"}).json()
        self.assertEqual(resp["code"], 0)

        # 0: verify: successful
        resp = c.post(
            url1, data={"email": "verify@test.com", "type": "major", "op": "modify"}
        ).json()
        self.assertEqual(resp["code"], 12)

    def test_utils(self):
        ums.utils.user_to_list(self.u4, self.p1)
        ums.utils.send_mail("", "")
