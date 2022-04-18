import sys

from django.test import TestCase
from rms.models import *
from ums.models import *
from ums.tests import *


class RMS_Tests(TestCase):
    def setUp(self):
        self.ums = UMS_Tests()
        self.ums.setUp()
        """
        u1 in p1 super,u2 in p1 dev,u3 out p1,u4 in p1 SYS
        """
        self.u4 = User.objects.create(
            name="Dave", password="159357", email="Dave@secoder.net"
        )
        UserProjectAssociation.objects.create(
            user=self.u4, project=self.ums.p1, role=Role.SUPERMASTER
        )
        self.IR1 = IR.objects.create(
            project=self.ums.p1,
            title="ir1",
            description="ir1",
            rank=1,
            createdBy=self.ums.u1,
        )
        self.It1 = Iteration.objects.create(
            project=self.ums.p1,
            sid=1,
            title="Ite1",
            begin=1.0,
            end=3.0,
        )
        self.SR1 = SR.objects.create(
            project=self.ums.p1,
            title="sr1",
            description="sr1",
            priority=3,
            rank=1,
            state=SR.SRState.TODO,
            createdBy=self.ums.u1,
        )
        self.service1 = Service.objects.create(
            project=self.ums.p1,
            title="ir1",
            description="ir1",
            rank=1,
            createdBy=self.ums.u1,
        )
        UserIterationAssociation.objects.create(user=self.ums.u1, iteration=self.It1)
        self.ass = IRSRAssociation.objects.create(IR=self.IR1, SR=self.SR1)
        SRIterationAssociation.objects.create(SR=self.SR1, iteration=self.It1)
        ServiceSRAssociation.objects.create(SR=self.SR1, service=self.service1)
        ProjectIterationAssociation.objects.create(
            project=self.ums.p1, iteration=self.It1
        )
        IRIterationAssociation.objects.create(IR=self.IR1, iteration=self.It1)
        UserSRAssociation.objects.create(user=self.ums.u1, sr=self.SR1)

    def login(self, user, sess):
        c = Client()
        c.cookies["sessionId"] = sess
        res = c.post(
            "/ums/login/",
            data={"identity": user.name, "password": user.password},
            content_type="application/json",
        )
        for ss in SessionPool.objects.all():
            print(ss.user, ss.sessionId, file=sys.stderr)

        return c

    """
    Test GET
    """

    def test_GET(self):
        c = self.ums.login_u1("101")
        id = self.ums.p1.id
        type = "ir"
        url = "/rms/project/"
        resp = c.get(url, data={"project": str(id), "type": type})
        print(resp.json())
        self.assertEqual(resp.json()["code"], 0)

        type = "sr"
        resp = c.get(url, data={"project": str(id), "type": type})
        self.assertEqual(resp.json()["code"], 0)

        type = "service"
        resp = c.get(url, data={"project": str(id), "type": type})
        self.assertEqual(resp.json()["code"], 0)

        type = "sr-iteration"
        resp = c.get(url, data={"project": str(id), "type": type})
        self.assertEqual(resp.json()["code"], 0)

        type = "iteration"
        resp = c.get(url, data={"project": str(id), "type": type})
        self.assertEqual(resp.json()["code"], 0)

        type = "ir-sr"
        resp = c.get(url, data={"project": str(id), "type": type})
        self.assertEqual(resp.json()["code"], 0)

        type = "user-iteration"
        resp = c.get(url, data={"project": str(id), "type": type})
        self.assertEqual(resp.json()["code"], 0)

        type = "user-iteration"
        resp = c.get(url, data={"project": str(id), "type": type})
        self.assertEqual(resp.json()["code"], 0)

        type = "service-sr"
        resp = c.get(url, data={"project": str(id), "type": type})
        print(resp.json())
        self.assertEqual(resp.json()["code"], 0)

        type = "serviceOfSR"
        resp = c.get(
            url, data={"project": str(id), "type": type, "SRId": int(self.SR1.id)}
        )
        print(resp.json())
        self.assertEqual(resp.json()["code"], 0)

        type = "SROfService"
        resp = c.get(
            url, data={"project": str(id), "type": type, "serviceId": self.service1.id}
        )
        print(resp.json())
        self.assertEqual(resp.json()["code"], 0)

        type = "user-sr"
        resp = c.get(url, data={"project": str(id), "type": type})
        print(resp.json())
        self.assertEqual(resp.json()["code"], 0)

        type = "ir-iteration"
        resp = c.get(
            url,
            data={
                "project": str(id),
                "type": type,
            },
        )
        print(resp.json())
        self.assertEqual(resp.json()["code"], 0)

        type = "project-iteration"
        resp = c.get(
            url,
            data={
                "project": str(id),
                "type": type,
            },
        )
        print(resp.json())
        self.assertEqual(resp.json()["code"], 0)

        # no type
        type = "iteration"
        resp = c.get(
            url,
            data={
                "project": str(id),
            },
        )
        self.assertEqual(resp.json()["code"], -1)

        # no project
        type = "iteration"
        resp = c.get(url, data={"type": type})
        self.assertEqual(resp.json()["code"], -1)

        # wrong project
        type = "iteration"
        resp = c.get(url, data={"project": 999, "type": type})
        self.assertEqual(resp.json()["code"], 1)

        # out of project
        c = self.login(self.ums.u3, "102")
        type = "iteration"
        resp = c.get(url, data={"project": str(id), "type": type})
        self.assertEqual(resp.json()["code"], 1)

    def postMessage(self, c, datas, excode):
        url = "/rms/project/"
        resp = c.post(url, data=datas, content_type="application/json")
        print(resp.json())
        self.assertEqual(resp.json()["code"], excode)

    def test_Post(self):
        c = self.login(self.u4, "103")
        # print(c.cookies)
        data1 = {
            "project": self.ums.p1.id,
            "type": "ir",
            "operation": "create",
            "data": {
                "updateData": {
                    "title": "aa",
                    "description": "bb",
                    "rank": 132,
                }
            },
        }
        self.postMessage(c, data1, 0)

        # more arugment
        data2 = {
            "project": self.ums.p1.id,
            "type": "ir",
            "operation": "create",
            "data": {
                "updateData": {
                    "title": "cc",
                    "description": "dd",
                    "rank": 112,
                    "name": "12",
                }
            },
        }
        self.postMessage(c, data2, 0)

        # wrong type
        data3 = {
            "project": self.ums.p1.id,
            "type": "ir",
            "operation": "create",
            "data": {
                "updateData": {
                    "title": "aa",
                    "description": "ss",
                    "rank": "ads",
                    "name": "12",
                }
            },
        }
        self.postMessage(c, data3, -1)

        data4 = {
            "project": self.ums.p1.id,
            "type": "sr",
            "operation": "create",
            "data": {
                "updateData": {
                    "title": "av",
                    "description": "sx",
                    "rank": 123,
                    "priority": 2,
                    "state": "TODO",
                }
            },
        }
        self.postMessage(c, data4, 0)

        data5 = {
            "project": self.ums.p1.id,
            "type": "iteration",
            "operation": "create",
            "data": {
                "updateData": {
                    "title": "w",
                    "sid": 21,
                    "begin": 123.0,
                    "end": 2.0,
                    "state": "TODO",
                }
            },
        }
        self.postMessage(c, data5, 0)

        data6 = {
            "project": self.ums.p1.id,
            "type": "service",
            "operation": "create",
            "data": {
                "updateData": {
                    "title": "12a",
                    "description": "d",
                    "rank": 12,
                }
            },
        }
        self.postMessage(c, data6, 0)

        self.SR2 = SR.objects.filter(title="av").first()
        self.IR2 = IR.objects.filter(title="aa").first()
        data7 = {
            "project": self.ums.p1.id,
            "type": "ir-sr",
            "operation": "create",
            "data": {
                "updateData": {
                    "IRId": self.IR2.id,
                    "SRId": self.SR2.id,
                }
            },
        }
        self.postMessage(c, data7, 0)

        data8 = {
            "project": self.ums.p1.id,
            "type": "user-iteration",
            "operation": "create",
            "data": {
                "updateData": {
                    "iterationId": self.It1.id,
                    "userId": self.ums.u2.id,
                }
            },
        }
        self.postMessage(c, data8, 0)

        data9 = {
            "project": self.ums.p1.id,
            "type": "sr-iteration",
            "operation": "create",
            "data": {
                "updateData": {
                    "iterationId": self.It1.id,
                    "SRId": self.SR2.id,
                }
            },
        }
        self.postMessage(c, data9, 0)

        # update
        data10 = {
            "project": self.ums.p1.id,
            "type": "ir",
            "operation": "update",
            "data": {
                "id": 2,
                "updateData": {
                    "title": "aas",
                    "description": "sbb",
                    "rank": 1325,
                },
            },
        }
        self.postMessage(c, data10, 0)

        # wrong Id
        data11 = {
            "project": self.ums.p1.id,
            "type": "ir",
            "operation": "update",
            "data": {
                "id": "daw",
                "updateData": {
                    "title": "aas",
                    "description": "sbb",
                    "rank": 1325,
                },
            },
        }
        self.postMessage(c, data11, -1)

        # wrong Mes
        data11 = {
            "project": self.ums.p1.id,
            "type": "ir",
            "operation": "update",
            "data": {
                "id": 2,
                "updateData": {
                    "title": "aas",
                    "description": "sbb",
                    "rank": 1325,
                    "name": "as",
                },
            },
        }
        self.postMessage(c, data11, 0)

        data12 = {
            "project": self.ums.p1.id,
            "type": "sr",
            "operation": "update",
            "data": {
                "id": self.SR2.id,
                "updateData": {
                    "title": "aas",
                    "description": "sbb",
                    "rank": 1325,
                },
            },
        }
        self.postMessage(c, data12, 0)

        data12 = {
            "project": self.ums.p1.id,
            "type": "SR_changeLog",
            "SRId": 2,
        }
        resp = c.get("/rms/project/", data=data12)
        self.assertEqual(resp.json()["code"], 0)

        data13 = {
            "project": self.ums.p1.id,
            "type": "iteration",
            "operation": "update",
            "data": {
                "id": 2,
                "updateData": {
                    "title": "aas",
                    "sid": 12,
                    "state": "Done",
                },
            },
        }
        self.postMessage(c, data13, 0)

        data14 = {
            "project": self.ums.p1.id,
            "type": "service",
            "operation": "update",
            "data": {
                "id": 2,
                "updateData": {
                    "title": "aasas",
                    "description": "sbb",
                    "rank": 1325,
                },
            },
        }
        self.postMessage(c, data14, 0)

        # delete
        data15 = {
            "project": self.ums.p1.id,
            "type": "ir",
            "operation": "delete",
            "data": {"id": 2},
        }
        self.postMessage(c, data15, 0)

        # wrong id
        data16 = {
            "project": self.ums.p1.id,
            "type": "ir",
            "operation": "delete",
            "data": {"id": "ss"},
        }
        self.postMessage(c, data16, -1)

        # more mes
        data17 = {
            "project": self.ums.p1.id,
            "type": "ir",
            "operation": "delete",
            "data": {"id": 2, "name": "as"},
        }
        self.postMessage(c, data17, 0)

        data18 = {
            "project": self.ums.p1.id,
            "type": "sr",
            "operation": "delete",
            "data": {"id": 2},
        }
        self.postMessage(c, data18, 0)

        data19 = {
            "project": self.ums.p1.id,
            "type": "iteration",
            "operation": "delete",
            "data": {"id": 2},
        }
        self.postMessage(c, data19, 0)

        data150 = {
            "project": self.ums.p1.id,
            "type": "service",
            "operation": "delete",
            "data": {"id": 2},
        }
        self.postMessage(c, data150, 0)

        data151 = {
            "project": self.ums.p1.id,
            "type": "ir-sr",
            "operation": "delete",
            "data": {
                "SRId": 2,
                "IRId": 1,
            },
        }
        self.postMessage(c, data151, 0)

        data152 = {
            "project": self.ums.p1.id,
            "type": "sr-iteration",
            "operation": "delete",
            "data": {
                "SRId": 2,
                "iterationId": 999,
            },
        }
        self.postMessage(c, data152, 0)

        data153 = {
            "project": self.ums.p1.id,
            "type": "user-iteration",
            "operation": "delete",
            "data": {
                "iterationId": 2,
                "userId": 999,
            },
        }
        self.postMessage(c, data153, 0)

        data154 = {
            "project": self.ums.p1.id,
            "type": "service-sr",
            "operation": "create",
            "data": {
                "updateData": {"SRId": self.SR2.id, "serviceId": self.service1.id}
            },
        }
        self.postMessage(c, data154, 0)

        data154 = {
            "project": self.ums.p1.id,
            "type": "service-sr",
            "operation": "delete",
            "data": {"SRId": self.SR2.id, "serviceId": self.service1.id},
        }
        self.postMessage(c, data154, 0)

        data154 = {
            "project": self.ums.p1.id,
            "type": "ir-iteration",
            "operation": "create",
            "data": {"updateData": {"IRId": self.IR2.id, "iterationId": self.It1.id}},
        }

        data154 = {
            "project": self.ums.p1.id,
            "type": "ir-iteration",
            "operation": "delete",
            "data": {
                "IRId": self.IR2.id,
                "iterationId": self.It1.id,
                "updateData": {"IRId": self.IR2.id, "iterationId": self.It1.id},
            },
        }
        self.postMessage(c, data154, 0)

        data154 = {
            "project": self.ums.p1.id,
            "type": "project-iteration",
            "operation": "delete",
            "data": {
                "iterationId": self.It1.id,
                "updateData": {"IRId": self.IR2.id, "iterationId": self.It1.id},
            },
        }
        self.postMessage(c, data154, 0)

        data154 = {
            "project": self.ums.p1.id,
            "type": "project-iteration",
            "operation": "create",
            "data": {"updateData": {"IRId": self.IR2.id, "iterationId": self.It1.id}},
        }
        self.postMessage(c, data154, 0)

        data155 = {
            "project": self.ums.p1.id,
            "type": "user-sr",
            "operation": "create",
            "data": {
                "updateData": {
                    "userId": self.ums.u1.id,
                    "SRId": self.SR2.id,
                }
            },
        }
        self.postMessage(c, data155, 0)
        data156 = {
            "project": self.ums.p1.id,
            "type": "user-sr",
            "operation": "delete",
            "data": {"userId": self.ums.u1.id, "SRId": self.SR2.id},
        }
        self.postMessage(c, data156, 0)
