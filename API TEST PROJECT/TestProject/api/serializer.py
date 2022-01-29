import ast
from tokenize import group
from urllib import request

from base.models import *
from base.models import CodeTable, Currency
from customer.models import *
from django.contrib.auth.models import Group, User
from django.db.models.signals import pre_save
from django.forms import fields
from rest_framework import serializers
# from TestProject.signals import DeleteOldFile
from sales.models import *
from TestProject.rest_config import LocalDateTime, RepresentFilePath
from TestProject.util import Util

from .models import UserGroup, UserProfile


class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id","name"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name","is_active"]

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    profile_image = RepresentFilePath(required=False)
    class Meta:
        model = UserProfile
        fields = ["user","profile_image","theme","display_row","default_page"]

    def update(self,instance,validated_data):
        user_data = validated_data.pop("user")
        user_serializer = self.fields['user']
        if "profile_image" in validated_data:
            Util.delete_old_file(instance.profile_image.path)
        user_serializer.update(instance.user,user_data)
        return super().update(instance, validated_data)


class UserRoleSerializer(serializers.ModelSerializer):
    role_ids = serializers.ListField(write_only=True)
    class Meta:
        model = User
        fields = ("first_name","last_name","email","is_active","role_ids")

    def create(self, validated_data):
        role_ids = validated_data.pop("role_ids")
        user = User.objects.create(**validated_data)
        user_group = [UserGroup(user=user,group_id=group_id) for group_id in role_ids]
        UserGroup.objects.bulk_create(user_group)
        return user

class UserListSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user__first_name')
    last_name = serializers.CharField(source='user__last_name')
    username = serializers.CharField(source='user__username')
    usergroup = serializers.CharField(source='user__usergroup__group__name',read_only=True)
    roles = serializers.ListField(write_only=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email","username","is_active","usergroup","roles"]

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["name"]



class InvoiceSerializer(serializers.ModelSerializer):
    invoice_date = LocalDateTime(required=True,source="invoice_created_on")
    invoice_amount = serializers.DecimalField(max_digits=12,decimal_places=4,source="outstanding_amount")
    paid_amount = serializers.DecimalField(max_digits=12,decimal_places=4,source="currency_outstanding_amount")
    # currency_outstanding_amount = serializers.DecimalField(max_digits=12,decimal_places=4,source="currency_outstanding_amount")
    invoice_status = serializers.CharField(source="status__name")
    # customer_type = serializers.CharField(source="company__customer_type")
    # company_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Invoice
        # fields = "__all__"
        fields =["invoice_number","invoice_amount","paid_amount","invoice_date","invoice_due_date","invoice_status"]


class SchedulerDetailSerializer(serializers.ModelSerializer):
    total_invoice = serializers.IntegerField(source="total_invoices",read_only=True)
    customer_name = serializers.CharField(source="customer",read_only=True)
    total_reminder = serializers.IntegerField(source="total_reminders",read_only=True)
    invoice_amount = serializers.DecimalField(max_digits=12,decimal_places=4,source="invoices_amount",read_only=True)
    paid_amount = serializers.DecimalField(max_digits=12,decimal_places=4,source="total_paid_amount",read_only=True)
    customer = serializers.CharField(source="scheduler_item__invoice__company__name",read_only=True)
    created_on = LocalDateTime(read_only=True)
    last_reminder = LocalDateTime(read_only=True)

    class Meta:
        model = Scheduler
        fields = ["id","scheduler_name","customer_name","total_invoice","total_reminder","invoice_amount","paid_amount","customer","created_on","last_reminder"]

class SchdulerItemSerializer(serializers.ModelSerializer):
    invoice = InvoiceSerializer(many=True)
    class Meta:
        model = SchedulerItem
        fields=["invoice"]

class SchdulerSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer",read_only=True)
    total_invoice = serializers.IntegerField(source="total_invoices",read_only=True)
    # total_reminder = serializers.IntegerField(source="total_reminders",read_only=True)
    created_on = LocalDateTime()
    # next_action_date =  LocalDateTime(read_only=True)
    # scheduler = SchdulerItemSerializer(many=True,source="scheduler_item")
    # legal_status = serializers.CharField(read_only=True)

    class Meta:
        model = Scheduler
        fields = ["id","scheduler_name","customer_name","total_invoice","created_on"]


class ActionSerializer(serializers.ModelSerializer):
    scheduler_name = serializers.CharField(source="scheduler.scheduler_name",read_only=True)
    created_by = serializers.CharField(source="action_by__username",read_only=True)
    action_date = LocalDateTime(required=False)
    # action_type = serializers.CharField(source="action_type",write_only=True)
    # next_action_date = LocalDateTime(required=False)
    attachment = serializers.CharField(read_only=True)

    class Meta:
        model = CollectionAction
        fields = ["id","scheduler_name","scheduler","created_by","action_by","action_type","action_date","reference","summary","attachment"]
        extra_kwargs = {
            'scheduler': {'write_only': True},
            'action_by': {'write_only': True},
        }

    # def create(self,validate_data):
    #     scheduler= validate_data.get("scheduler")
    #     Scheduler.objects.filter(id=scheduler.id).update(status="call_done")
    #     return super().create(validate_data)

class SchedulerItemSerializer(serializers.ModelSerializer):
    invoice = InvoiceSerializer(many=True,source="invoice.pk")
    class Meta:
        model = SchedulerItem
        fields = ["invoice"]

class CreateSchedulerSerializer(serializers.ModelSerializer):
    scheduler = SchdulerSerializer()
    invoice = InvoiceSerializer(many=True)
    class Meta:
        model = SchedulerItem
        fields = ["scheduler","invoice"]

    def create(self, validated_data):
        scheduler_data = validated_data.pop("scheduler")
        invoice_data = validated_data.pop("invoice")
        scheduler_serializer = self.fields['scheduler']
        schedulerid = scheduler_serializer.create(scheduler_data)
        invoice_serializer = self.fields["invoice"]
        invoices = invoice_serializer.create(invoice_data)
        scheduler_item = SchedulerItem.objects.create(scheduler=schedulerid)
        for invoice in invoices:
            scheduler_item.invoice.add(invoice)
        return scheduler_item

    def update(self, instance, validated_data):
        scheduler_data = validated_data.pop("scheduler")
        invoice_data = scheduler_data.pop("total_invoice")
        scheduler_serializer = self.fields['scheduler']
        invoice_serializer = self.fields['scheduler']["total_invoice"]
        customer_data = invoice_data.pop("company")
        customer_serializer = self.fields['scheduler']["total_invoice"]["company"]
        scheduler_serializer.update(instance.scheduler, scheduler_data)
        invoice_serializer.update(instance.scheduler.total_invoice,invoice_data)
        customer_serializer.update(instance.scheduler.total_invoice.company, customer_data)

        return super().update(instance, validated_data)
