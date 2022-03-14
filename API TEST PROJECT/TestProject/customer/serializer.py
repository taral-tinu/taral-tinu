from dataclasses import fields

from base.models import CodeTable, Currency
from rest_framework import serializers
from TestProject.rest_config import BulkListSerializer, ModelObjectidField

from customer.models import Address, Contact, Country, Customer
from customer.models import User as ECUser


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["ec_customer_id","name","account_manager_id","account_number",
                  "initials","customer_type_id","tax_number_type_id","vat_no","invoice_prefrence",
                  "invoice_postage","is_sales_review","is_vat_verified","sa_company_competence"
                  ,"sa_ec_customer","peppol_address","status_id","last_order_date","is_allow_send_mail",
                  "invoice_lang_id","is_deleted","is_duplicate",
                  "is_exclude_vat","is_deliver_invoice_by_post","is_student",
                  "is_peppol_verfied","is_always_vat","is_teacher","is_student_team",
                  "is_call_report_attached","currency_id","invoice_delivery_id"
                  ]
        # fields = "__all__"
        list_serializer_class = BulkListSerializer

    def create(self, validated_data):
        instance = Customer(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance



class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"
        list_serializer_class = BulkListSerializer

    def create(self, validated_data):
        instance = Contact(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance

class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeTable
        fields = "__all__"
        list_serializer_class = BulkListSerializer

    def create(self, validated_data):
        instance = CodeTable(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        list_serializer_class = BulkListSerializer

    def create(self, validated_data):
        instance = Address(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance

class ECUserSerializer(serializers.ModelSerializer):
    # customer_id = serializers.IntegerField(write_only=True)
    # language_id = serializers.IntegerField(write_only=True)
    # contact_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ECUser
        fields = ["customer_id","username","password","language_id",
                  "contact_id","is_power_user","is_deleted","is_active",
                  "sa_user_responsibilities"]
        # read_only_fields = ("id", "customer","contact","language")
        # fields = "__all__"
        list_serializer_class = BulkListSerializer

    def create(self, validated_data):
        # print(validated_data,"validated_data")
        instance = ECUser(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"
        list_serializer_class = BulkListSerializer

    def create(self, validated_data):
        instance = Country(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance
