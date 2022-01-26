from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from customer.views import CustomerView

router = DefaultRouter(trailing_slash=True)

router.register(r"customer",CustomerView,basename="customer")

urlpatterns = [

    ]
urlpatterns += router.urls
