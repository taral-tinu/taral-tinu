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
    def create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=0,message="data created")
class CustomerView(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    def create(self, request):
        code_ids = Util.get_codes("code_table")
        currency_code = Util.get_codes("currency")

        customer_data = []
        ec_contact_ids = [x["account_manager"] for x in request.data]
        contacts = Contact.objects.filter(ec_contact_id__in=ec_contact_ids).values("id","ec_contact_id")
        contact_ids = Util.get_dict_from_queryset("ec_contact_id","id",contacts)
        for request in request.data:
            last_order_date = parser.parse(request['last_order_date']) if request['last_order_date'] else None
            request['customer_type'] = code_ids[request['customer_type']] if request['customer_type'] in code_ids else None
            request['tax_number_type'] = code_ids[request['tax_number_type']] if request['tax_number_type'] in code_ids else None
            request['status'] = code_ids[request['status']] if request['status'] in code_ids else None
            request['invoice_lang'] =  code_ids[request['invoice_lang']] if request['invoice_lang'] in code_ids else None
            request['invoice_delivery'] = code_ids[request['invoice_delivery']] if request['invoice_delivery'] in code_ids else None
            request['currency'] = currency_code[request['currency']] if request['currency'] in currency_code else None
            if request["last_order_date"] == "" or request["last_order_date"] is None:
                request.pop("last_order_date")

            else:
                request['last_order_date'] = last_order_date.strftime("%Y-%m-%d %H:%M")
                account_manager = contact_ids[request['account_manager']] if request['account_manager'] in contact_ids else None
            request['account_manager'] = account_manager[0], #contact_ids[request['account_manager']] if request['account_manager'] in contact_ids else None,
            customer_data.append(request)
        serializer = self.get_serializer(data=customer_data,  many=isinstance(customer_data,list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(serializer.data)

class AddressView(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    def create(self, request):
        code_ids = Util.get_codes("code_table")
        country_ids = Util.get_codes("country")
        ec_customer_ids = [x["customer"] for x in request.data]
        customers = Customer.objects.filter(ec_customer_id__in=ec_customer_ids).values("id","ec_customer_id")
        customer_ids = Util.get_dict_from_queryset("ec_customer_id","id",customers)
        addresses_data = []
        for address in request.data:
            address['customer'] = customer_ids[address['customer']] if address['customer'] in customer_ids else None
            address['state']= code_ids[address['state']] if address['state'] in code_ids else None
            address['country'] = country_ids[address['country']] if address['country'] in country_ids else None
            address['address_type'] = code_ids[address['address_type']] if address['address_type'] in code_ids else None
            addresses_data.append(address)
        # print(addresses_data,"address")
        serializer = self.get_serializer(data=addresses_data, many=isinstance(addresses_data,list))
        serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        return APIResponse(code=0,message="data inserted")


class ECUserView(viewsets.ModelViewSet):
    queryset = (ECUser.objects.values("id",
                                      "customer_id",
                                      "contact_id",
                                      "language_id",
                                      "username",
                                      "password",
                                      "is_power_user",
                                      "is_deleted",
                                      "is_active",
                                      "sa_user_responsibilities"))
    serializer_class = ECUserSerializer

    def create(self, request):
        code_ids = Util.get_codes("code_table")
        ec_contact_ids = [x["contact_id"] for x in request.data]
        contacts = Contact.objects.filter(ec_contact_id__in=ec_contact_ids).values("id","ec_contact_id")
        contact_ids = Util.get_dict_from_queryset("ec_contact_id","id",contacts)
        ec_customer_ids = [x["customer_id"] for x in request.data]
        customers = Customer.objects.filter(ec_customer_id__in=ec_customer_ids).values("id","ec_customer_id")
        customer_ids = Util.get_dict_from_queryset("ec_customer_id","id",customers)
        users_data =[]
        for user in request.data:
            customer_id = customer_ids[user['customer_id']] if user['customer_id'] in customer_ids else None
            user['customer_id'] = customer_id
            user['contact_id'] = contact_ids[user['contact_id']] if user['contact_id'] in contact_ids else None
            user["language_id"] = code_ids[user['language_id']] if user['language_id'] in code_ids else None
            users_data.append(user)
        serializer = self.get_serializer(data=users_data, many=True)
        serializer.is_valid(raise_exception=True)
        # print(serializer,"serializer")
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
