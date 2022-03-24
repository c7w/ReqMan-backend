from django.test import TestCase
from rms.models import *
from ums.models import *
from rdts.models import *
from ums.tests import *
from rms.tests import *


class RDTS_Tests(TestCase):
    def setUp(self):
        self.rms = RMS_Tests()
        self.rms.setUp()
        self.repo = Repository.objects.create(
            url="223.edu",
            project=self.rms.ums.p1,
            title="repo1",
            description="a common repo",
            createdBy=self.rms.ums.u1,
        )
        self.commit1 = Commit.objects.create(
            hash_id="acbd",
            repo=self.repo,
            title="Test.001.001",
            message="just a test",
            commiter_email="admin@233.edu",
            commiter_name="233",
            createdAt=1.0,
            url="233.edu",
        )
        self.MR1 = MergeRequest.objects.create(
            merge_id=1,
            repo=self.repo,
            title="Merge",
            description="98",
            state="opened",
            url="98.233.edu",
        )
        self.issue1 = Issue.objects.create(
            issue_id=1,
            repo=self.repo,
            title="First",
            description="first",
            state="closed",
            url="233.edu",
        )
        CommitSRAssociation.objects.create(commit=self.commit1, SR=self.rms.SR1)
        MRSRAssociation.objects.create(MR=self.MR1, SR=self.rms.SR1)
        IssueSRAssociation.objects.create(issue=self.issue1, SR=self.rms.SR1)

    """
    Test GET
    """

    def getRequest(self, c, datas, excode):
        url = "/rdts/project/"
        resp = c.get(url, data=datas)
        self.assertEqual(resp.json()["code"], excode)

    def test_Get(self):
        c = self.rms.login(self.rms.u4, "301")

        data1 = {"project": str(self.rms.ums.p1.id), "type": "repo"}
        self.getRequest(c, data1, 0)

        data2 = {"repo": str(self.repo.id), "type": "issue"}
        self.getRequest(c, data2, 0)

        data3 = {"repo": str(self.repo.id), "type": "mr"}
        self.getRequest(c, data3, 0)

        data4 = {"repo": str(self.repo.id), "type": "commit"}
        self.getRequest(c, data4, 0)

        data5 = {"repo": str(self.repo.id), "type": "mr-sr"}
        self.getRequest(c, data5, 0)

        data6 = {"repo": str(self.repo.id), "type": "issue-sr"}
        self.getRequest(c, data6, 0)

        data7 = {"repo": str(self.repo.id), "type": "commit-sr"}
        self.getRequest(c, data7, 0)

        # wrong type
        data8 = {"repo": "wa", "type": "commit-sr"}
        self.getRequest(c, data8, -1)

        data7 = {"repo": str(self.repo.id), "type": "mit-sr"}
        self.getRequest(c, data7, 1)
