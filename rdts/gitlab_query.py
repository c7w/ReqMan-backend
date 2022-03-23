import requests
from apscheduler.schedulers.background import BackgroundScheduler

TYPES = ['secoder_gitlab']

obj = 'original'

class Gitlab:
        def request(self, base: str, repo: int, access_token: str, type: str):
            url = base.strip('/') + ('/api/v4/projects/%d/repository/' % repo) + type
            resp = requests.get(url, headers={
                'PRIVATE-TOKEN': access_token
            })
            return resp.status_code, resp.json


def test_task(txt):
    print("hello!", obj, txt)

def add_query_task(txt: str):
    # s = BackgroundScheduler()
    # s.add_job(test_task, 'interval', seconds=2, args=('arg',))
    # s.start()
    pass

def init_query():
    pass

