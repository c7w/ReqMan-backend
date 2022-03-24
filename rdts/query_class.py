import requests
from apscheduler.schedulers.background import BackgroundScheduler


class Gitlab:
    def __init__(self, base_url: str, repo, access_token: str):
        self.base = base_url.strip("/")
        self.repo = int(repo)
        self.token = access_token

    def merges(self, page):
        return self.request("merge_requests", page)

    def issues(self, page):
        return self.request("issues", page)

    def commits(self, page):
        return self.request("repository/commits", page)

    def request(self, req_type: str, page):
        url = (
            self.base.strip("/")
            + ("/api/v4/projects/%d/" % self.repo)
            + req_type
            + f"?page={page}"
        )
        print(url)
        resp = requests.get(url, headers={"PRIVATE-TOKEN": self.token})
        return resp.status_code, resp.json()


type_map = {"gitlab": Gitlab}
