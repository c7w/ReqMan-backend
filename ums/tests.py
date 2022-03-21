from django.test import TestCase
from django.test import Client as DefaultClient
from ums.models import *

SUCC = {'code': 0}
FAIL = {'code': 1}

class Client(DefaultClient):
    """
    for copy cookie sessionId into respective method body
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def _add_cookie(self, kw):
        if 'sessionId' in self.cookies:
            if 'data' not in kw:
                kw['data'] = {}
            kw['data']['sessionId'] = self.cookies['sessionId'].value
        return kw

    def post(self, *args, **kw):
        return super(Client, self).post(*args, **self._add_cookie(kw))

    def get(self, *args, **kw):
        return super(Client, self).get(*args, **self._add_cookie(kw))

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
        self.u3 = User.objects.create(
            name='Caorl',
            password='159357',
            email='carol@secoder.net'
        )

        self.p1 = Project.objects.create(
            title='ProjTit1',
            description='Desc1'
        )
        self.p2 = Project.objects.create(
            title='ProjTit2',
            description='Desc2'
        )
        self.p3 = Project.objects.create(
            title='ProjTit3',
            description='Desc3'
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
        UserProjectAssociation.objects.create(
            user=self.u3,
            project=self.p2,
            role=Role.SUPERMASTER
        )


    """
    create a template client as u1
    """
    def login_u1(self, sess):
        c = Client()
        c.cookies['sessionId'] = sess

        c.post("/ums/login/", data={
            'identity': self.u1.name,
            'password': self.u1.password
        }, content_type="application/json")

        return c

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
        c = self.login_u1('5')

        resp = c.post("/ums/logout/")
        self.assertEqual(resp.json()['code'], 0)

        resp = c.post("/ums/logout/")
        self.assertEqual(resp.json()['code'], 1)

    """
    /ums/user/
    """
    def test_user(self):
        c = self.login_u1('6')
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

        # successful
        resp = c.post("/ums/project/", data={
            'project': self.p1.id
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 0)

    """
    /ums/modify_project/
    """
    def test_modify_project(self):
        c = self.login_u1('10')

        # not supermaster
        resp = c.post("/ums/modify_project/", data={
            'project': self.p2.id,
            'title': 't',
            'description': 'd'
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        # invalid project id
        resp = c.post("/ums/modify_project/", data={
            'project': 9801
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        # successful
        resp = c.post("/ums/modify_project/", data={
            'project': self.p1.id,
            'title': 'NewTitle',
            'description': 'NewDesc'
        }, content_type="application/json")
        self.p1 = Project.objects.get(id=self.p1.id) # refresh model
        self.assertEqual(resp.json()['code'], 0)
        self.assertEqual(self.p1.title, 'NewTitle')
        self.assertEqual(self.p1.description, 'NewDesc')


    def inv_legal_check(self, resp):
        inv = resp.json()['data']['invitation']
        self.assertEqual(resp.json()['code'], 0)
        self.assertEqual(len(inv), 8)
        self.assertEqual(inv,
                         ProjectInvitationAssociation.objects.filter(
                             project=self.p1,
                         ).first().invitation)
        return inv

    def get_inv_for(self, c, proj_id):
        return c.post("/ums/get_invitation/", data={
            'project': proj_id,
        }, content_type="application/json")

    """
    /ums/get_invitation/
    """
    def test_get_invitation(self):
        c = self.login_u1('11')

        # not supermaster
        resp = self.get_inv_for(c, self.p2.id)
        self.assertEqual(resp.json()['code'], 1)

        # invalid project id
        resp = self.get_inv_for(c, 9999)
        self.assertEqual(resp.json()['code'], 1)

        # successful
        resp = self.get_inv_for(c, self.p1.id)
        inv = self.inv_legal_check(resp)

        # do not change
        resp = self.get_inv_for(c, self.p1.id)
        self.assertEqual(resp.json()['code'], 0)
        self.assertEqual(resp.json()['data']['invitation'], inv)

    """
    /ums/refresh_invitation/
    """
    def test_refresh_invitation(self):
        c = self.login_u1('12')

        # not supermaster
        resp = c.post("/ums/refresh_invitation/", data={
            'project': self.p2.id,
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        # invalid project id
        resp = c.post("/ums/refresh_invitation/", data={
            'project': 7777
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        # successful
        resp = c.post("/ums/refresh_invitation/", data={
            'project': self.p1.id,
        }, content_type="application/json")
        inv = self.inv_legal_check(resp)

        # do change
        resp = c.post("/ums/refresh_invitation/", data={
            'project': self.p1.id,
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 0)
        self.assertEqual(len(resp.json()['data']['invitation']), 8)
        self.assertNotEqual(resp.json()['data']['invitation'], inv)

    """
    /ums/modify_user_role/
    """
    def test_modify_user_role(self):
        c = self.login_u1('13')

        # not supermaster
        resp = c.post("/ums/modify_user_role/", data={
            'project': self.p2.id,
            'user': self.u2.id,
            'role': Role.SUPERMASTER
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        # invalid project id
        resp = c.post("/ums/modify_user_role/", data={
            'project': -1,
            'user': self.u2.id,
            'role': Role.SUPERMASTER
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        # invalid role
        resp = c.post("/ums/modify_user_role/", data={
            'project': self.p1.id,
            'user': self.u2.id,
            'role': 'undefined'
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        # not in project
        resp = c.post("/ums/modify_user_role/", data={
            'project': self.p1.id,
            'user': self.u3.id,
            'role': Role.DEV
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        # successful
        resp = c.post("/ums/modify_user_role/", data={
            'project': self.p1.id,
            'user': self.u2.id,
            'role': Role.MEMBER
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 0)
        self.assertEqual(UserProjectAssociation.objects.filter(
            user=self.u2,
            project=self.p1
        ).first().role, Role.MEMBER)

    """
    /ums/project_add_user/
    """
    def test_project_add_user(self):
        c = self.login_u1('14')
        url = '/ums/project_add_user/'

        # not supermaster
        resp = c.post(url, data={
            'project': self.p3.id,
            'user': self.u3.id,
            'role': Role.MEMBER
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        # invalid project id
        resp = c.post(url, data={
            'project': -1,
            'user': self.u3.id,
            'role': Role.SUPERMASTER
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        # invalid role
        resp = c.post(url, data={
            'project': self.p1.id,
            'user': self.u3.id,
            'role': 'undefined'
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        # in project
        resp = c.post(url, data={
            'project': self.p1.id,
            'user': self.u2.id,
            'role': Role.DEV
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        # successful
        resp = c.post(url, data={
            'project': self.p1.id,
            'user': self.u3.id,
            'role': Role.MEMBER
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 0)
        self.assertEqual(UserProjectAssociation.objects.filter(
            user=self.u3,
            project=self.p1
        ).first().role, Role.MEMBER)


    """
    /ums/project_rm_user/
    """
    def test_project_rm_user(self):
        c = self.login_u1('15')
        url = '/ums/project_rm_user/'

        # not supermaster
        resp = c.post(url, data={
            'project': self.p2.id,
            'user': self.u2.id,
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        # invalid project id
        resp = c.post(url, data={
            'project': -1,
            'user': self.u3.id,
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        # successful
        resp = c.post(url, data={
            'project': self.p1.id,
            'user': self.u2.id,
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 0)
        self.assertEqual(UserProjectAssociation.objects.filter(
            user=self.u2,
            project=self.p1
        ).first(), None)

        # not in project
        resp = c.post(url, data={
            'project': self.p1.id,
            'user': self.u2.id,
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

    """
    /ums/register/
    """
    def test_register(self):
        url = '/ums/register/'
        c = Client()
        c.cookies['sessionId'] = '16'

        d = self.login_u1('17')
        self.get_inv_for(d, self.p1.id)
        self.assertNotEqual(len(ProjectInvitationAssociation.objects.all()), 0)

        # invalid invitation
        resp = c.post(url, data={
            'name': 'Dave',
            'password': 'Dave123456',
            'email': 'dave@secoder.net',
            'invitation': 'invalid'
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 2)

        # successful with invitation
        inv = ProjectInvitationAssociation.objects.filter(project=self.p1).first()
        resp = c.post(url, data={
            'name': 'Dave',
            'password': 'Dave123456',
            'email': 'dave@secoder.net',
            'invitation': inv.invitation
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 0)
        new_user = User.objects.filter(name='Dave').first()
        self.assertEqual(new_user.email, 'dave@secoder.net')
        self.assertEqual(new_user.password, 'Dave123456')
        self.assertEqual(UserProjectAssociation.objects.filter(
            project=inv.project,
            user=new_user
        ).first().role, inv.role)

        # successful without invitation
        resp = c.post(url, data={
            'name': 'Eve',
            'password': 'Eve123456',
            'email': 'eve@secoder.net',
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 0)
        new_user = User.objects.filter(name='Eve').first()
        self.assertEqual(new_user.email, 'eve@secoder.net')
        self.assertEqual(new_user.password, 'Eve123456')
        self.assertEqual(len(UserProjectAssociation.objects.filter(
            user=new_user
        )), 0)

        # dup name
        resp = c.post(url, data={
            'name': 'eve',
            'password': 'Eve123456',
            'email': 'eve_dup_name@secoder.net',
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)

        # dup email
        resp = c.post(url, data={
            'name': 'EEE',
            'password': 'Eve123456',
            'email': 'EVE@secoder.net',
        }, content_type="application/json")
        self.assertEqual(resp.json()['code'], 1)


