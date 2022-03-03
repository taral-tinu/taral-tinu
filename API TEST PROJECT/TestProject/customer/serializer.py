from dataclasses import fields

from base.models import CodeTable
from base.serializer import BulkListSerializer
from rest_framework import serializers

from customer.models import Address, Contact, Country, Customer
from customer.models import User as ECUser


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
        list_serializer_class = BulkListSerializer

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"
        list_serializer_class = BulkListSerializer

class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeTable
        fields = "__all__"
        list_serializer_class = BulkListSerializer

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        list_serializer_class = BulkListSerializer

class ECUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ECUser
        fields = "__all__"
        list_serializer_class = BulkListSerializer
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"
        list_serializer_class = BulkListSerializer
