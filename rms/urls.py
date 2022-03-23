from rest_framework.routers import DefaultRouter
from rms.views import RMSViewSet

router = DefaultRouter()
router.register("", RMSViewSet, basename="RMS")

urlpatterns = router.urls
