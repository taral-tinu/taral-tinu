from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from customer.views import (AddressView, CodeView, ContactView, CountryView,
                            CustomerView, ECUserView)

router = DefaultRouter(trailing_slash=True)

router.register(r"customer",CustomerView,basename="customer")
router.register(r"contact",ContactView,basename="contact")
router.register(r"user",ECUserView,basename="user")
router.register(r"address",AddressView,basename="address")
router.register(r"code",CodeView,basename="code")
router.register(r"country",CountryView,basename="country")



urlpatterns = [
    # url(r"^customer/$",CustomerView.as_view(),name="customer")
    ]
urlpatterns += router.urls
