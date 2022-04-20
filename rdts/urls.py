from rest_framework.routers import DefaultRouter
from rdts.views import RDTSViewSet, webhook
from django.urls import path

router = DefaultRouter()
router.register("", RDTSViewSet, basename="RDTS")

urlpatterns = router.urls + [path("webhook/", webhook)]
