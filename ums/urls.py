from django.urls import path, include
from ums.views import UserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("", UserViewSet, basename="user")

urlpatterns = router.urls
