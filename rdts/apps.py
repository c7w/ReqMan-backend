from django.apps import AppConfig
from rdts.gitlab_query import init_query
import os


def init_schedule():
    from .models import RemoteRepo
    print(RemoteRepo)

class RdtsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rdts"

    def ready(self):
        # prevent double initialization
        run_once = os.environ.get('RDTS_RUN_ONCE_FLAG')
        if run_once is not None:
            return
        os.environ['RDTS_RUN_ONCE_FLAG'] = 'True'

        init_schedule()
