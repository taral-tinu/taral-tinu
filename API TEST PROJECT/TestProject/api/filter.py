import django
import django_filters
from django.contrib.auth.models import Group
from django.db.models import fields
from django_filters.filters import OrderingFilter

from .models import Scheduler, UserProfile


class UserFilter(django_filters.FilterSet):

    first_name = django_filters.CharFilter(field_name='user__first_name', lookup_expr='istartswith')
    last_name = django_filters.CharFilter(field_name='user__last_name', lookup_expr='istartswith')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='istartswith')
    usergroup = django_filters.CharFilter(field_name='user__usergroup__group__name', lookup_expr='istartswith')

    ordering = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('user__first_name', 'first_name1'),
            ('user__last_name', 'last_name'),
            ('user__username', 'last_name'),
            ('user__usergroup__group__name', 'usergroup'),
        ),
    )

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'username', 'usergroup']

class RoleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name",lookup_expr='istartswith')
    ordering = OrderingFilter(
        fields=(
            ("id","id"),
            ("name","name"),
),
)
    class Meta:
        model = Group
        fields = ["name"]

class CollectionActionFilter(django_filters.FilterSet):
    scheduler_name = django_filters.CharFilter(field_name="scheduler_name",lookup_expr='istartswith')
    created_on = django_filters.DateFilter(field_name="created_on")
    customer_name = django_filters.CharFilter(field_name="scheduler_item__invoice__company__name",lookup_expr='istartswith')

    ordering = OrderingFilter(
        fields=(
            ("id","id"),
            ("scheduler_name","scheduler_name"),
            ("created_on","created_on"),
            ("customer_name","scheduler_item__invoice__company__name"),
            ("total_invoice","total_invoice"),),)

    # class Meta:
    #     model = Scheduler
    #     fields = ["scheduler_name","created_on","customer_name",'total_invoice']

