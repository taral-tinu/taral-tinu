import ast
import time
from tokenize import group
from urllib import request

from base.models import *
from base.models import CodeTable, Currency
from customer.models import *
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.forms import fields
from rest_framework import serializers
from TestProject.rest_config import LocalDateTime, RepresentFilePath
from TestProject.util import Util

# from TestProject.signals import DeleteOldFile
from sales.models import *

# class InvoiceSerializer(serializers.ModelSerializer):
#     invoice_date = LocalDateTime(required=True,source="invoice_created_on")
#     invoice_amount = serializers.DecimalField(max_digits=12,decimal_places=4,source="outstanding_amount")
#     paid_amount = serializers.DecimalField(max_digits=12,decimal_places=4,source="amount_paid")
#     # currency_outstanding_amount = serializers.DecimalField(max_digits=12,decimal_places=4,source="currency_outstanding_amount")
#     invoice_status = serializers.CharField(source="status__name")
#     # customer_type = serializers.CharField(source="company__customer_type")
#     # company_id = serializers.IntegerField(write_only=True)
#     class Meta:
#         model = Invoice
#         # fields = "__all__"
#         fields =["invoice_number","invoice_amount","paid_amount","invoice_date","invoice_due_date","invoice_status"]


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

# class SchdulerItemSerializer(serializers.ModelSerializer):
#     invoice = InvoiceSerializer(many=True)
#     class Meta:
#         model = SchedulerItem
#         fields=["invoice"]

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
    # scheduler_name = serializers.CharField(source="scheduler.scheduler_name",read_only=True)
    # created_by = serializers.CharField(source="action_by__username",read_only=True)
    # action_date = LocalDateTime(required=False)
    # action_type = serializers.CharField(source="action_type",write_only=True)
    # next_action_date = LocalDateTime(required=False)
    # attachment = serializers.CharField(read_only=True)
    scheduler_item_id = serializers.IntegerField(write_only=True)
    action_by_id = serializers.IntegerField(write_only=True)
    action_by = serializers.CharField(read_only=True)


    class Meta:
        model = ActionReport
        fields = ["id","action_by","action_by_id","scheduler_item_id","action_type","action_date","summary","reference"]
        # fields = ["id","scheduler_name","scheduler","created_by","action_by","action_type","action_date","reference","summary","attachment"]
        # extra_kwargs = {
        #     'scheduler_item_id': {'write_only': True},
        #     'action_by_id': {'write_only': True},
        # }

    # def create(self,validate_data):
    #     scheduler= validate_data.get("scheduler")
    #     Scheduler.objects.filter(id=scheduler.id).update(status="call_done")
    #     return super().create(validate_data)

# class SchedulerItemSerializer(serializers.ModelSerializer):
#     invoice = InvoiceSerializer(many=True,source="invoice.pk")
#     class Meta:
#         model = SchedulerItem
#         fields = ["invoice"]

# class CreateSchedulerSerializer(serializers.ModelSerializer):
#     scheduler = SchdulerSerializer()
#     invoice = InvoiceSerializer(many=True)
#     class Meta:
#         model = SchedulerItem
#         fields = ["scheduler","invoice"]

#     def create(self, validated_data):
#         scheduler_data = validated_data.pop("scheduler")
#         invoice_data = validated_data.pop("invoice")
#         scheduler_serializer = self.fields['scheduler']
#         schedulerid = scheduler_serializer.create(scheduler_data)
#         invoice_serializer = self.fields["invoice"]
#         invoices = invoice_serializer.create(invoice_data)
#         scheduler_item = SchedulerItem.objects.create(scheduler=schedulerid)
#         for invoice in invoices:
#             scheduler_item.invoice.add(invoice)
#         return scheduler_item

#     def update(self, instance, validated_data):
#         scheduler_data = validated_data.pop("scheduler")
#         invoice_data = scheduler_data.pop("total_invoice")
#         scheduler_serializer = self.fields['scheduler']
#         invoice_serializer = self.fields['scheduler']["total_invoice"]
#         customer_data = invoice_data.pop("company")
#         customer_serializer = self.fields['scheduler']["total_invoice"]["company"]
#         scheduler_serializer.update(instance.scheduler, scheduler_data)
#         invoice_serializer.update(instance.scheduler.total_invoice,invoice_data)
#         customer_serializer.update(instance.scheduler.total_invoice.company, customer_data)

#         return super().update(instance, validated_data)


class SchedulerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheduler
        fields = "__all__"


class InvoiceCreateSerializer(serializers.ModelSerializer):
    sheduler = SchedulerSerializer(many=True)
    class Meta:
        model = Invoice
        fields = "__all__"


    def update(self, instance, validated_data):
        print("data",validated_data)
        # instance.description = validated_data["description"]
        instance.meta_data = validated_data["meta_data"]

        if isinstance(self._kwargs["data"], dict):
            instance.save()

        return instance


class BulkListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        # print(validated_data,"LL")
        result = [self.child.create(attrs) for attrs in validated_data]

        try:
            self.child.Meta.model.objects.bulk_create(result)
        except IntegrityError as e:
            raise ValidationError(e)

        # update_project_last_modified(result)

        return result

    def update(self, instances, validated_data):
        # print("validated_data",validated_data)
        instance_hash = {index: instance for index, instance in enumerate(instances)}

        result = [
            self.child.update(instance_hash[index], attrs)
            for index, attrs in enumerate(validated_data)
        ]

        writable_fields = [
            x
            for x in self.child.Meta.fields
            if x not in self.child.Meta.read_only_fields
        ]

        try:
            self.child.Meta.model.objects.bulk_update(result, writable_fields)
        except IntegrityError as e:
            raise ValidationError(e)

        # update_project_last_modified(result)

        return result


    # def to_internal_value(self, data):
    #     # print(data,"data")
    #     # self.child.instance = self.instance.get(id=item['id'])
    #     # self.child.initial_data = item
    #     # validated = self.child.run_validation(item)
    #     return data
class TaskSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()

    def create(self, validated_data):
        instance = Invoice(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            invoices = instance.save()
        return instance

    def update(self, instance, validated_data):
        # print(instance,"validated_data")
        instance.invoice_value = validated_data["invoice_value"]
        # instance.name = validated_data["name"]

        if isinstance(self._kwargs["data"], dict):
            instance.save()

        return instance
    class Meta:
        model = Invoice
        fields = ["invoice_value"]
        # fields = '__all__'
        read_only_fields = ("id", )
        list_serializer_class = BulkListSerializer

class UpdateTaskSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
            # print(instance,"validated_data")
        instance.invoice_value = validated_data["invoice_value"]
        if validated_data.get("last_rem_date"):
            instance.last_rem_date = validated_data["last_rem_date"]



        if isinstance(self._kwargs["data"], dict):
            instance.save()

        return instance
    class Meta:
        model = Invoice
        fields = ["invoice_value","last_rem_date"]
        read_only_fields = ("id", )
        list_serializer_class = BulkListSerializer

class InvoiceSerializer(serializers.ModelSerializer):
    last_reminder_date = LocalDateTime(source="last_rem_date",read_only=True)
    customer_name = serializers.CharField(read_only=True)

    # customer_name = serializers.CharField(source="customer__name",read_only=True)
    country = serializers.CharField(read_only=True)
    # invoice_amount = serializers.DecimalField(read_only=True,source="invoice_value",max_digits=12,decimal_places=3)
    invoice_amount = serializers.DecimalField(read_only=True,max_digits=12,decimal_places=3)
    total_reminder = serializers.IntegerField(read_only=True)
    invoice_created_on = LocalDateTime(read_only=True)
    # status = serializers.CharField(source="status__desc",read_only=True)
    status = serializers.CharField(read_only=True)

    action_status = serializers.CharField(read_only=True)
    # action_status = serializers.CharField(source="collectioninvoice_invoice__action__action_status")
    action_date = LocalDateTime(read_only=True)
    # action_date = serializers.CharField(source="collectioninvoice_invoice__action__action_date")

    is_finished = serializers.BooleanField()

    # scheduler_item_id = serializers.IntegerField(source="scheduler_invoice__scheduler_item__id")
    # invoiceorder_invoice = InvoiceOrderSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ["id","invoice_number","payment_tracking_number",
        "country","invoice_created_on","is_legal","status","action_status","action_date",
        "last_reminder_date","amount_paid","invoice_amount","customer_id","customer_name","total_reminder","is_finished"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance:
            if "action_status" in representation and representation['action_status']:
                representation['action_status'] = dict(action_status)[representation['action_status']]
            if representation["is_finished"] == True:
                representation['action_status'] = "Finished"
            return representation
