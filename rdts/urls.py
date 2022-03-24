from rest_framework.routers import DefaultRouter
from rdts.views import RDTSViewSet

router = DefaultRouter()
router.register("", RDTSViewSet, basename="RDTS")

urlpatterns = router.urls
