import requests
from apscheduler.schedulers.background import BackgroundScheduler


class Gitlab:
    def __init__(self, base_url: str, repo, access_token: str):
        self.base = base_url.strip("/")
        self.repo = int(repo)
        self.token = access_token

    def merges(self):
        return self.request("merge_requests")

    def issues(self):
        return self.request("issues")

    def commits(self):
        return self.request("repository/commits")

    def request(self, req_type: str):
        url = self.base.strip("/") + ("/api/v4/projects/%d/" % self.repo) + req_type
        resp = requests.get(url, headers={"PRIVATE-TOKEN": self.token})
        return resp.status_code, resp.json


type_map = {"gitlab": Gitlab}
