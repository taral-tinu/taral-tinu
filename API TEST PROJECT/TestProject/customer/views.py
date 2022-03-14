from datetime import datetime
from locale import currency

from base.models import CodeTable, Currency
from base.serializer import CodeSerializer
from base.util import Util
from dateutil import parser
from django.core.exceptions import ValidationError
from django.shortcuts import render
from rest_framework import generics, viewsets
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
        print("Call")
        # if isinstance(request.data, list):
        #   for item in request.data:

        # codes = CodeTable.objects.filter().values("id","code")
        # code_ids = Util.get_dict_from_queryset("code","id",codes)
        # currency = Currency.objects.filter().values("id","code")
        # currency_code = Util.get_dict_from_queryset("code","id",currency)

        code_ids = Util.get_codes("code_table")
        currency_code = Util.get_codes("currency")

        customer_data = []
        ec_contact_ids = [x["account_manager"] for x in request.data]
        contacts = Contact.objects.filter(ec_contact_id__in=ec_contact_ids).values("id","ec_contact_id")
        contact_ids = Util.get_dict_from_queryset("ec_contact_id","id",contacts)
        # if isinstance(request.data, list):
        for request in request.data:
            last_order_date = parser.parse(request['last_order_date']) if request['last_order_date'] else None
            request['customer_type_id'] = int(code_ids[request['customer_type']]) if request['customer_type'] in code_ids else None
            request['tax_number_type_id'] = int(code_ids[request['tax_number_type']]) if request['tax_number_type'] in code_ids else None
            request['status_id'] = int(code_ids[request['status']]) if request['status'] in code_ids else None
            request['invoice_lang_id'] =  int(code_ids[request['invoice_lang']]) if request['invoice_lang'] in code_ids else None
            request['invoice_delivery_id'] = int(code_ids[request['invoice_delivery']]) if request['invoice_delivery'] in code_ids else None
            request['currency_id'] = int(currency_code[request['currency']]) if request['currency'] in currency_code else None
            if request["last_order_date"] == "" or request["last_order_date"] is None:
                request.pop("last_order_date")

            else:
                request['last_order_date'] = last_order_date.strftime("%Y-%m-%d %H:%M")
            request['account_manager_id'] = None #contact_ids[request['account_manager']] if request['account_manager'] in contact_ids else None,
            customer_data.append(request)
        print(customer_data,"customer_data")
        serializer = self.get_serializer(data=customer_data, many=True)
        serializer.is_valid(raise_exception=True)
        # print(serializer,"serializer")
        self.perform_create(serializer)
        return APIResponse(serializer.data)

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
        # print(request.data,"user")
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
