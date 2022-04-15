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
            + (f"?page={page}" if page else "")
        )
        print(url)
        resp = requests.get(url, headers={"PRIVATE-TOKEN": self.token})
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


type_map = {"gitlab": Gitlab}
