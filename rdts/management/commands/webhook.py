from django.core.management.base import BaseCommand, CommandError
from apscheduler.schedulers.blocking import BlockingScheduler
from rdts.models import *
from rms.models import *
import json

from rdts.webhook import push_action, issue_action, mr_action
from rdts.query_class import type_map


def now():
    return dt.datetime.timestamp(dt.datetime.now(pytz.timezone(TIME_ZONE)))


class Command(BaseCommand):
    help = "Run Schedule Tasks"

    def response(self):
        event = PendingWebhookRequests.objects.first()
        if not event:
            print("checked, no event")
            return
        if event.remote.type not in type_map:
            return

        req = type_map[event.remote.type](
            json.loads(event.remote.info)["base_url"],
            event.remote.remote_id,
            event.remote.access_token,
        )
        body = json.loads(event.body)
        print(body["object_kind"])
        if body["object_kind"] == "push":
            push_action(event.remote, body, req)
        elif body["object_kind"] == "merge_request":
            mr_action(event.remote, body, req)
        elif body["object_kind"] == "issue":
            issue_action(event.remote, body, req)
        event.delete()

    def handle(self, *args, **options):
        s = BlockingScheduler()
        self.stdout.write("Webhook Scheduler Initialized")
        s.add_job(self.response, "interval", seconds=0.4)
        s.start()
        # self.response()
