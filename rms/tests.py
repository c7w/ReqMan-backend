from http import client
from venv import create
from django.test import TestCase
from rms.models import *
from ums.models import *
from ums.tests import *

class RMS_Tests(TestCase):
    def setUp(self):
        self.ums = UMS_Tests()
        self.ums.setUp()
        '''
        u1 in p1 super,u2 in p1 dev,u3 out p1,u4 in p1 SYS
        '''
        self.u4 = User.objects.create(
            name='Dave',
            password='159357',
            email='Dave@secoder.net'
        )
        UserProjectAssociation.objects.create(
            user=self.u4,
            project=self.ums.p1,
            role=Role.SYS
        )
        self.IR1=IR.objects.create(
            project=self.ums.p1,
            title = 'ir1',
            description = 'ir1',
            rank = 1,
            createdBy = self.ums.u1
        )
        self.It1=Iteration.objects.create(
            project=self.ums.p1,
            sid = 1,
            title = 'Ite1',
            begin = 1.0,
            end = 3.0,
        )
        self.SR1=SR.objects.create(
            project=self.ums.p1,
            title = 'sr1',
            description = 'sr1',
            priority = 3,
            rank = 1,
            state=SR.SRState.TODO,
            createdBy=self.ums.u1
        )
        self.service1=Service.objects.create(
            project=self.ums.p1,
            title = 'ir1',
            description = 'ir1',
            rank = 1,
            createdBy = self.ums.u1
        )
        UserIterationAssociation.objects.create(
            user=self.ums.u1,
            iteration = self.It1
        )
        self.ass=IRSRAssociation.objects.create(
            IR = self.IR1,
            SR = self.SR1
        )
        SRIterationAssociation.objects.create(
            SR = self.SR1,
            iteration=self.It1
        )

    def login(self,user,sess):
        c=Client()
        c.cookies['sessionId'] = sess
        c.post("/ums/login/", data={
            'identity': user.name,
            'password': user.password
        }, content_type="application/json")
        return c


    """
    Test GET
    """
    def test_GET(self):
        c=self.ums.login_u1('101')
        id = self.ums.p1.id
        type = 'ir'
        url='/rms/project/'
        print(url)
        resp = c.get(url,data={
            'project':str(id),
            'type':type
        })
        print(resp)
        self.assertEqual(resp.json()['code'],0)

        type = 'sr'
        resp = c.get(url,data={
            'project':str(id),
            'type':type
        })
        print(resp)
        self.assertEqual(resp.json()['code'],0)

        type = 'service'
        resp = c.get(url,data={
            'project':str(id),
            'type':type
        })
        print(resp)
        self.assertEqual(resp.json()['code'],0)

        type = 'sr-iteration'
        resp = c.get(url,data={
            'project':str(id),
            'type':type
        })
        print(resp)
        self.assertEqual(resp.json()['code'],0)

        type = 'iteration'
        resp = c.get(url,data={
            'project':str(id),
            'type':type
        })
        print(resp)
        self.assertEqual(resp.json()['code'],0)

        type = 'ir-sr'
        resp = c.get(url,data={
            'project':str(id),
            'type':type
        })
        print(resp)
        self.assertEqual(resp.json()['code'],0)

        type = 'user-iteration'
        resp = c.get(url,data={
            'project':str(id),
            'type':type
        })
        print(resp)
        self.assertEqual(resp.json()['code'],0)

        type = 'user-iteration'
        resp = c.get(url,data={
            'project':str(id),
            'type':type
        })
        print(resp.json())
        self.assertEqual(resp.json()['code'],0)
        
        # no type
        type = 'iteration'
        resp = c.get(url,data={
            'project':str(id),
        })
        print(resp.json())
        self.assertEqual(resp.json()['code'],-1)

        # no project
        type = 'iteration'
        resp = c.get(url,data={
            'type':type
        })
        print(resp.json())
        self.assertEqual(resp.json()['code'],-1)

        # wrong project
        type = 'iteration'
        resp = c.get(url,data={
            'project':999,
            'type':type
        })
        print(resp.json())
        self.assertEqual(resp.json()['code'],-1)

        # out of project
        c=self.login(self.ums.u3,'102')
        type = 'iteration'
        resp = c.get(url,data={
            'project':str(id),
            'type':type
        })
        print(resp.json())
        self.assertEqual(resp.json()['code'],1)

        






