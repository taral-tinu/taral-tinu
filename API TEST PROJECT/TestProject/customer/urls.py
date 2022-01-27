from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from customer.views import (AddressView, CodeView, ContactView, CustomerView,
                            ECUserView)

router = DefaultRouter(trailing_slash=True)

router.register(r"customer",CustomerView,basename="customer")
router.register(r"contact",ContactView,basename="contact")
router.register(r"user",AddressView,basename="user")
router.register(r"code",ECUserView,basename="code")
router.register(r"code",CodeView,basename="code")


urlpatterns = [

    ]
urlpatterns += router.urls
