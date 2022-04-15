from django.core.management.base import BaseCommand, CommandError
from apscheduler.schedulers.blocking import BlockingScheduler
from rdts.models import *
from rms.models import *
import json

from rdts.webhook import push_action, issue_action, mr_action


class Command(BaseCommand):
    help = "Run Schedule Tasks"

    def response(self):
        event = PendingWebhookRequests.objects.first()
        if not event:
            return
        body = json.loads(event.body)
        if body["object_kind"] == "push":
            push_action(event.remote, body)
        elif body["object_kind"] == "merge_request":
            mr_action(event.remote, body)
        elif body["object_kind"] == "issue":
            issue_action(event.body, body)

    def handle(self, *args, **options):
        s = BlockingScheduler()
        self.stdout.write("Webhook Scheduler Initialized")
        s.add_job(self.response, "interval", seconds=0.5)
        s.start()
