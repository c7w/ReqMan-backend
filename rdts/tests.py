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
            # url="223.edu",
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
        IssueMRAssociation.objects.create(issue=self.issue1, MR=self.MR1)

    """
    Test GET
    """

    def getRequest(self, c, datas, excode):
        url = "/rdts/project/"
        resp = c.get(url, data=datas)
        print("______json________")
        print(resp.json())
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

        data8 = {
            "repo": str(self.repo.id),
            "type": "issue-mr",
            "issueId": self.issue1.id,
        }
        self.getRequest(c, data8, 0)

    def post_message(self, c, datas, excode):
        url = "/rdts/project/"
        resq = c.post(url, data=datas, content_type="application/json")
        print(resq.json())
        self.assertEqual(resq.json()["code"], excode)

    def test_RDTSPOST(self):
        c = self.rms.login(self.rms.u4, "302")

        # test create
        data = {
            "project": self.rms.ums.p1.id,
            "type": "repo",
            "operation": "create",
            "data": {
                "updateData": {
                    # "url": "22333.edu",
                    "project": self.rms.ums.p1.id,
                    "title": "repo2",
                    "description": "a common repo",
                    "createdBy": self.rms.ums.u1.id,
                }
            },
        }
        self.post_message(c, data, -1)

        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "commit",
            "operation": "create",
            "data": {
                "updateData": {
                    "hash_id": "ToUseID",
                    "repo": self.repo.id,
                    "title": "Test.001.001",
                    "message": "just a test",
                    "commiter_email": "admin@233.edu",
                    "commiter_name": "233",
                    "createdAt": 1.0,
                    "url": "233.edu",
                }
            },
        }
        self.post_message(c, data, 0)

        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "mr",
            "operation": "create",
            "data": {
                "updateData": {
                    "merge_id": 2,
                    "repo": self.repo.id,
                    "title": "Merge",
                    "description": "98",
                    "state": "opened",
                    "url": "98.233.edu",
                }
            },
        }
        self.post_message(c, data, 0)

        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "issue",
            "operation": "create",
            "data": {
                "updateData": {
                    "issue_id": 5,
                    "repo": self.repo.id,
                    "title": "First",
                    "description": "first",
                    "state": "closed",
                    "url": "233.edu",
                }
            },
        }
        self.post_message(c, data, 0)

        commit = Commit.objects.filter(hash_id="ToUseID").first()
        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "commit-sr",
            "operation": "create",
            "data": {
                "updateData": {
                    "commitId": commit.id,
                    "SRId": self.rms.SR1.id,
                }
            },
        }
        self.post_message(c, data, 0)

        MR = MergeRequest.objects.filter(merge_id=2).first()
        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "mr-sr",
            "operation": "create",
            "data": {
                "updateData": {
                    "MRId": MR.id,
                    "SRId": self.rms.SR1.id,
                }
            },
        }
        self.post_message(c, data, 0)

        issue = Issue.objects.filter(issue_id=5).first()
        data2 = {"repo": str(self.repo.id), "type": "issue"}
        self.getRequest(c, data2, 0)
        self.test_Get()
        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "issue-sr",
            "operation": "create",
            "data": {
                "updateData": {
                    "issueId": issue.id,
                    "SRId": self.rms.SR1.id,
                }
            },
        }
        self.post_message(c, data, 0)

        # update test
        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "mr",
            "operation": "update",
            "data": {
                "id": MR.id,
                "updateData": {
                    "merge_id": 3,
                    "repo": self.repo.id,
                    "title": "Merge",
                    "description": "981",
                    "state": "opened",
                    "url": "98.2333.edu",
                },
            },
        }
        self.post_message(c, data, 0)

        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "commit",
            "operation": "update",
            "data": {
                "id": commit.id,
                "updateData": {
                    "hash_id": "s2",
                    "repo": self.repo.id,
                    "title": "Test.001.001",
                    "message": "just a test",
                    "commiter_email": "admin@2333.edu",
                    "commiter_name": "2333",
                    "createdAt": 1.0,
                    # "url": "233.edu",
                },
            },
        }
        self.post_message(c, data, 0)

        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "issue",
            "operation": "update",
            "data": {
                "id": issue.id,
                "updateData": {
                    "issue_id": 7,
                    "repo": self.repo.id,
                    "title": "First1",
                    "description": "first",
                    "state": "closed",
                    "url": "2333.edu",
                },
            },
        }
        self.post_message(c, data, 0)

        repo = Repository.objects.filter(title="repo2").first()
        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "repo",
            "operation": "update",
            "data": {
                "id": repo.id,
                "updateData": {
                    # "url": "23333.edu",
                    "project": self.rms.ums.p1.id,
                    "title": "repo2333",
                    "description": "a 2333 repo",
                    "createdBy": self.rms.ums.u1.id,
                },
            },
        }
        self.post_message(c, data, -1)

        # test delete
        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "repo",
            "operation": "delete",
            "data": {"id": repo.id},
        }
        self.post_message(c, data, 0)

        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "mr",
            "operation": "delete",
            "data": {"id": MR.id},
        }
        self.post_message(c, data, 0)

        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "issue",
            "operation": "delete",
            "data": {"id": issue.id},
        }
        self.post_message(c, data, 0)

        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "commit",
            "operation": "delete",
            "data": {"id": commit.id},
        }
        self.post_message(c, data, 0)

        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "mr-sr",
            "operation": "delete",
            "data": {
                "MRId": MR.id,
                "SRId": self.rms.SR1.id,
            },
        }
        self.post_message(c, data, 0)

        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "commit-sr",
            "operation": "delete",
            "data": {
                "commitId": commit.id,
                "SRId": self.rms.SR1.id,
            },
        }
        self.post_message(c, data, 0)

        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "issue-sr",
            "operation": "delete",
            "data": {
                "issueId": issue.id,
                "SRId": self.rms.SR1.id,
            },
        }
        self.post_message(c, data, 0)

        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "issue-mr",
            "operation": "delete",
            "data": {"issueId": self.issue1.id, "MRId": self.MR1.id},
        }
        self.post_message(c, data, 0)

        data = {
            "project": self.rms.ums.p1.id,
            "repo": self.repo.id,
            "type": "issue-mr",
            "operation": "create",
            "data": {"updateData": {"issueId": self.issue1.id, "MRId": self.MR1.id}},
        }
        self.post_message(c, data, 0)


class ScheduleFunctionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(name="bla", password="****", email="e@e.e")
        self.proj = Project.objects.create(title="proj title", description="desc")
        self.repo = Repository.objects.create(
            project=self.proj,
            title="repo title",
            description="repo desc",
            createdBy=self.user,
            # url="https://gitlab.secoder.net/2020011156/unittest_repo",
        )
        self.remote = RemoteRepo.objects.create(
            repo=self.repo,
            remote_id="791",
            type="gitlab",
            access_token="vzDY55aaS-5rjeeYYxxn",
            info='{"base_url": "https://gitlab.secoder.net"}',
            secret_token="",
        )

    def test_fetch_function(self):
        from rdts.management.commands.schedule import Command

        cmd = Command()
        cmd.crawl_all()

        # self.assertEqual(CrawlLog.objects.all().__len__(), 3)
        # self.assertNotEqual(Commit.objects.all().__len__(), 0)
        # self.assertNotEqual(Issue.objects.all().__len__(), 0)
        # self.assertNotEqual(MergeRequest.objects.all().__len__(), 0)
