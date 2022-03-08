from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from sales.views import CollectionInvoiceView, SchedulerView

router = DefaultRouter(trailing_slash=True)

# router.register(r'action', ActionView, basename='actions')

collection_actions = CollectionInvoiceView.as_view({"get":"list"})
# actions = ActionView.as_view({"get":"list"})
router.register(r'scheduler', SchedulerView, basename='scheduler')

urlpatterns = [

    url(r"^collection_actions/$",collection_actions,name="collection-actions"),
    # url(r"actions",actions,name="actions"),

    ]
urlpatterns += router.urls
