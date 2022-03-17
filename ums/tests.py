from django.test import TestCase, Client
from ums.models import User, Project, UserProjectAssociation

class UMS_Tests(TestCase):
    def set_up(self):
        u1 = User.objects.create(
            name='Alice',
            password='123456',
            email='alice@secoder.net'
        )
        u2 = User.objects.create(
            name='Bob',
            password='789123',
            email='bob@secoder.net'
        )

        p1 = Project.objects.create(
            title='ProjTit1',
            description='Desc1'
        )
        p2 = Project.objects.create(
            title='ProjTit2',
            description='Desc2'
        )

        UserProjectAssociation.objects.create(
            user=u1,
            project=p1
        )
        UserProjectAssociation.objects.create(
            user=u1,
            project=p2
        )
        UserProjectAssociation.objects.create(
            user=u2,
            project=p1
        )


