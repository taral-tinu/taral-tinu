from dataclasses import fields

from base.models import CodeTable
from rest_framework import serializers

from customer.models import Address, Contact, Customer, ECUser


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"

class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeTable
        fields = "__all__"

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"

class ECUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ECUser
        fields = "__all__"
