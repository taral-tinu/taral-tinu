from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from base.views import (ActionView, CollectionActionView, InvoiceView,
                    GetMenus, LegalActionView, RoleListView,CustomerReminder,
                    SchedulerDetailView, SchedulerView, UserListView, UserRole,
                    UserView)

# router = DefaultRouter(trailing_slash=True)

# router.register(r'user', UserView, basename='user')
# router.register(r'role', UserRole, basename='role')
# router.register(r'collection_action', CollectionActionView, basename='collection_action')
# router.register(r'legal_actions', LegalActionView, basename='legal_actions')
# router.register(r'actions', ActionView, basename='actions')
# router.register(r'scheduler', SchedulerView, basename='scheduler')
# router.register(r'invoice',InvoiceView, basename="invoice")
# collection_actions = CollectionActionView.as_view({"get":"list"})
# invoices = InvoiceView.as_view({"get":"list"})


# urlpatterns = [
#     url(r"^get_menu/$", GetMenus.as_view(), name="all_menu"),
#     url(r"^roles/$", RoleListView.as_view(), name="roles"),
#     url(r"^users/$", UserListView.as_view(), name="users"),

#     # #-----------------CollectionAction----------------

#     url(r"^collection_actions/$",collection_actions,name="collection-actions"),
#     # url(r"^collections/$", ActionListView.as_view(), name="collections"),
#     url(r"^reminder_details/$", SchedulerDetailView.as_view(), name="reminder_details"),
#     url(r"^invoices/$", invoices, name="invoices"),
#     url(r"^customer_reminder/$", CustomerReminder.as_view(), name="customer_reminder"),
#     # url(r"^create_action/$", CreateActionView.as_view(), name="create_action"),

#     #++++++++++
#     # url(r"scheduler_data/$",SchedulerDataFromEC.as_view(),name="scheduler_data")

#     ]
# urlpatterns += router.urls
