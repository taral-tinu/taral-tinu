from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from .views import (  CollectionActionView,LegalActionView,ActionView,
                      SchedulerView,
                     GetMenus,  RoleListView,
                      UserListView, UserRole,InvoiceView,
                    UserView)

router = DefaultRouter(trailing_slash=True)

router.register(r'user', UserView, basename='user')
router.register(r'role', UserRole, basename='role')
router.register(r'collection_actions', CollectionActionView, basename='collection_actions')
router.register(r'legal_actions', LegalActionView, basename='legal_actions')
router.register(r'actions', ActionView, basename='actions')
router.register(r'scheduler', SchedulerView, basename='scheduler')
router.register(r'invoice',InvoiceView, basename="invoice")



urlpatterns = [
    url(r"^get_menu/$", GetMenus.as_view(), name="all_menu"),
    url(r"^roles/$", RoleListView.as_view(), name="roles"),
    url(r"^users/$", UserListView.as_view(), name="users"),

    # #-----------------CollectionAction----------------

    # url(r"^collection_actions/$", CollectionActionView.as_view(), name="collection_actions"),
    # url(r"^collections/$", ActionListView.as_view(), name="collections"),
    # url(r"^reminder_details/$", SchedulerDetailView.as_view(), name="reminder_details"),
    # url(r"^customer_invoice/$", CustomerInvoice.as_view(), name="customer_invoice"),
    # url(r"^customer_reminder/$", CustomerReminder.as_view(), name="customer_reminder"),
    # url(r"^create_action/$", CreateActionView.as_view(), name="create_action"),

    #++++++++++
    # url(r"scheduler_data/$",SchedulerDataFromEC.as_view(),name="scheduler_data")

    ]
urlpatterns += router.urls
