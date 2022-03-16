from django.test import TestCase, Client
from ums.models import *

SUCC = {'code': 0}
FAIL = {'code': 1}

class UMS_Tests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create(
            name='Alice',
            password='123456',
            email='alice@secoder.net'
        )
        self.u2 = User.objects.create(
            name='Bob',
            password='789123',
            email='bob@secoder.net'
        )

        self.p1 = Project.objects.create(
            title='ProjTit1',
            description='Desc1'
        )
        self.p2 = Project.objects.create(
            title='ProjTit2',
            description='Desc2'
        )

        UserProjectAssociation.objects.create(
            user=self.u1,
            project=self.p1,
            role=Role.SUPERMASTER
        )
        UserProjectAssociation.objects.create(
            user=self.u1,
            project=self.p2,
            role=Role.DEV
        )
        UserProjectAssociation.objects.create(
            user=self.u2,
            project=self.p1,
            role=Role.DEV
        )

    """
    illegal cookie
    """
    def test_lacking_cookie(self):
        c = Client()
        resp = c.post("/ums/login/")
        self.assertEqual(resp.json()['code'], -1)

    """
    /ums/login/
    """
    def test_login(self):
        c = Client()
        c.cookies['sessionId'] = '0'
        resp = c.post("/ums/login/", data={
            'identity': self.u1.name,
            'password': self.u1.password
        }, content_type="application/json")
        self.assertEqual(resp.json(), {'code': 0})

        c.cookies['sessionId'] = '1'
        resp = c.post("/ums/login/", data={
            'identity': self.u1.email,
            'password': self.u1.password
        }, content_type="application/json")
        self.assertEqual(resp.json(), {'code': 0})

        c.cookies['sessionId'] = '2'
        resp = c.post("/ums/login/", data={
            'identity': self.u1.email + 'cccccc',
            'password': self.u1.password
        }, content_type="application/json")
        self.assertEqual(resp.json(), {'code': 2})

        c.cookies['sessionId'] = '3'
        resp = c.post("/ums/login/", data={
            'identity': self.u1.email,
            'password': self.u1.password + 'cccccc'
        }, content_type="application/json")
        self.assertEqual(resp.json(), {'code': 3})

        c.cookies['sessionId'] = '4'
        resp = c.post("/ums/login/", data={
            'identity': self.u1.email ,
            'password': self.u1.password
        }, content_type="application/json")
        self.assertEqual(resp.json(), {'code': 0})

        c.cookies['sessionId'] = '4'
        resp = c.post("/ums/login/", data={
            'identity': self.u1.email,
            'password': self.u1.password
        }, content_type="application/json")
        self.assertEqual(resp.json(), {'code': 1})


    """
    /ums/logout
    """
    def test_logout(self):
        c = Client()
        c.cookies['sessionId'] = '5'
        c.post("/ums/login/", data={
            'identity': self.u1.email,
            'password': self.u1.password
        }, content_type="application/json")

        resp = c.post("/ums/logout/")
        self.assertEqual(resp.json()['code'], 0)

        resp = c.post("/ums/logout/")
        self.assertEqual(resp.json()['code'], 1)

    """
    /ums/user/
    """
    def test_user(self):
        c = Client()
        c.cookies['sessionId'] = '6'
        c.post("/ums/login/", data={
            'identity': self.u1.email,
            'password': self.u1.password
        }, content_type="application/json")
        resp = c.get("/ums/user/")
        self.assertEqual(resp.json()['data']['user']['id'], self.u1.id)
        self.assertEqual(len(resp.json()['data']['projects']), 2)

        # logout leads to fail
        c.post("/ums/logout/")
        resp = c.get("/ums/user/")
        self.assertEqual(resp.json()['code'], 1)

    """
    /ums/check_username_available
    """
    def test_check_username_av(self):
        c = Client()
        c.cookies['sessionId'] = '7'
        resp = c.post("/ums/check_username_available/",
                      data={"name": 'Alice'}, content_type="application/json")
        self.assertEqual(resp.json(), FAIL)

        resp = c.post("/ums/check_username_available/",
                      data={"name": 'Eve'}, content_type="application/json")
        self.assertEqual(resp.json(), SUCC)

    """
    /ums/check_email_available/`
    """
    def test_check_email_av(self):
        c = Client()
        c.cookies['sessionId'] = '8'
        resp = c.post("/ums/check_email_available/",
                      data={"email": 'ALICE@secoder.net'},
                      content_type="application/json")
        self.assertEqual(resp.json(), FAIL)

        resp = c.post("/ums/check_email_available/",
                      data={"email": 'hey@secoder.net'},
                      content_type="application/json")
        self.assertEqual(resp.json(), SUCC)

    """
     /ums/project/
    """
    def test_project(self):
        c = Client()
        c.cookies['sessionId'] = '9'
        c.post("/ums/login/", data={
            'identity': self.u2.email,
            'password': self.u2.password
        }, content_type="application/json")

        # invalid project id
        resp = c.post("/ums/project/", data={
            'project': 999
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        # not in project
        resp = c.post("/ums/project/", data={
            'project': self.p2.id
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        resp = c.post("/ums/project/", data={
            'project': self.p1.id
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 0)


