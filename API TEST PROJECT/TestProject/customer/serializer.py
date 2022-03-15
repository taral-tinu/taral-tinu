from dataclasses import fields

from base.models import CodeTable, Currency
from rest_framework import serializers
from TestProject.rest_config import BulkListSerializer, ModelObjectidField

from customer.models import Address, Contact, Country, Customer
from customer.models import User as ECUser


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
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
    customer_id = ModelObjectidField()
    contact_id = ModelObjectidField()
    language_id = ModelObjectidField(allow_null=True)

    class Meta:
        model = ECUser
        fields = ["id","customer_id","contact_id","language_id","username","password","is_power_user","is_deleted","is_active","sa_user_responsibilities"]
        # fields = "__all__"
        list_serializer_class = BulkListSerializer

    def create(self, validated_data):
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
