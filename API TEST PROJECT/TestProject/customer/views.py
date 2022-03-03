from base.models import CodeTable
from base.serializer import CodeSerializer
from base.util import Util
from dateutil import parser
from django.shortcuts import render
from rest_framework import viewsets
from TestProject.rest_config import APIResponse

from customer.models import Address, Contact, Country, Customer
from customer.models import User as ECUser
from customer.serializer import (AddressSerializer, ContactSerializer,
                                 CountrySerializer, CustomerSerializer,
                                 ECUserSerializer)

# Create your views here.


class ContactView(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    # create multiple objects
    def create(self, request):
        print(request.data,"contact")
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=0,message="data created")
class CustomerView(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    # create multiple objects
    def create(self, request):
        code_ids = Util.get_codes("code_table")
        currency_code = Util.get_codes("currency")
        customer_data = []
        ec_contact_ids = [x["account_manager"] for x in request.data]
        contacts = Contact.objects.filter(ec_contact_id__in=ec_contact_ids).values("id","ec_contact_id")
        contact_ids = Util.get_dict_from_queryset("ec_contact_id","id",contacts)
        for customer in request.data:
            customer['customer_type'] = code_ids[customer['customer_type']] if customer['customer_type'] in code_ids else None
            customer['tax_number_type'] = code_ids[customer['tax_number_type']] if customer['tax_number_type'] in code_ids else None
            customer['status'] = code_ids[customer['status']] if customer['status'] in code_ids else None
            customer['invoice_lang'] =  code_ids[customer['invoice_lang']] if customer['invoice_lang'] in code_ids else None
            customer['invoice_delivery'] = code_ids[customer['invoice_delivery']] if customer['invoice_delivery'] in code_ids else None
            customer['currency'] = currency_code[customer['currency']] if customer['currency'] in currency_code else None
            customer['last_order_date'] = parser.parse(customer['last_order_date']) if customer['last_order_date'] else None
            if customer["last_order_date"] == "":
                # print("KKK")
                customer.pop("last_order_date")
            # print(customer["last_order_date"])
            customer['account_manager'] =None# contact_ids[customer['account_manager']] if customer['account_manager'] in contact_ids else None,
            customer_data.append(customer)
        serializer = self.get_serializer(data=customer_data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=0,message="data inserted")

class AddressView(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    def create(self, request):
        # print(request.data,"address")
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=0,message="data inserted")


class ECUserView(viewsets.ModelViewSet):
    queryset = ECUser.objects.all()
    serializer_class = ECUserSerializer
    def create(self, request):
        print(request.data,"user")
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=0,message="data inserted")


# Create your views here.
class CodeView(viewsets.ModelViewSet):
    queryset = CodeTable.objects.all()
    serializer_class = CodeSerializer
    def create(self, request):
        print(request.data,"Code")
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=0,message="data inserted")

class CountryView(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    def create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=0,message="data inserted")
