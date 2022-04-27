import time

import requests
from apscheduler.schedulers.background import BackgroundScheduler


class RemoteRepoFetcher:
    def __init__(self, base_url: str, repo, access_token: str):
        self.base = base_url.strip("/")
        self.repo = int(repo)
        self.token = access_token

    def merges(self, page):
        raise NotImplemented

    def issues(self, page):
        raise NotImplemented

    def commits(self, page):
        raise NotImplemented

    def commit_diff_lines(self, _hash):
        raise NotImplemented

    def branches(self, page):
        raise NotImplemented

    def single_commit(self, _hash):
        raise NotImplemented

    def single_issue(self, iid):
        raise NotImplemented

    def single_merge(self, mid):
        raise NotImplemented

    def project(self):
        raise NotImplemented


def from_diff_to_lines(diff: str):
    diff = diff.split("\n")
    add = 0
    subs = 0
    for l in diff:
        if len(l) and l[0] == "+":
            add += 1
        if len(l) and l[0] == "-":
            subs += 1
    return add, subs


class Gitlab(RemoteRepoFetcher):
    def __init__(self, base_url: str, repo, access_token: str):
        super(Gitlab, self).__init__(base_url, repo, access_token)

    def merges(self, page):
        return self.request("merge_requests", page)

    def issues(self, page):
        return self.request("issues", page)

    def commits(self, page):
        return self.request("repository/commits", page)

    def request(self, req_type: str, page=None):
        url = (
            self.base.strip("/")
            + ("/api/v4/projects/%d/" % self.repo)
            + req_type
            + (f"?page={page}&per_page=1000" if page else "")
        )
        print(url)
        try_cnt = 5
        resp = None
        while try_cnt:
            try:
                resp = requests.get(url, headers={"PRIVATE-TOKEN": self.token})
            except Exception as e:
                print("Request Error", e)
                time.sleep(5)
                try_cnt -= 1
            else:
                break
        if resp is None:
            return -1, {}
        return resp.status_code, resp.json()

    def commit_diff_lines(self, _hash: str):
        status, res = self.request(f"repository/commits/{_hash}/diff")
        if status == 200:
            diffs = []
            total_add = 0
            total_subs = 0
            for file in res:
                add, subs = from_diff_to_lines(file["diff"])
                total_add += add
                total_subs += subs
                diffs += [file["diff"]]
            return status, total_add, total_subs, diffs
        else:
            return status, -1, -1, []

    def branches(self, page):
        return self.request("repository/branches", page)

    def single_commit(self, _hash):
        return self.request(f"repository/commits/{_hash}")

    def single_issue(self, iid):
        return self.request(f"issues/{iid}")

    def single_merge(self, mid):
        return self.request(f"merge_requests/{mid}")

    def project(self):
        return self.request("")


type_map = {"gitlab": Gitlab}
