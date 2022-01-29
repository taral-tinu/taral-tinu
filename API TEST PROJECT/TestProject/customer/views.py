from base.models import CodeTable
from base.serializer import CodeSerializer
from django.shortcuts import render
from rest_framework import viewsets
from TestProject.rest_config import APIResponse

from customer.models import Address, Contact, Customer, ECUser
from customer.serializer import (AddressSerializer, ContactSerializer,
                                 CustomerSerializer, ECUserSerializer)

# Create your views here.


class ContactView(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    # create multiple objects
    def create(self, request):
        print(request.data,"contact")
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=0,message="data created")
class CustomerView(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    print('CCCC')

    # create multiple objects
    def create(self, request):
        print(request.data,"customer")
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=0,message="data inserted")

class AddressView(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    def create(self, request):
        # print(request.data,"address")
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=0,message="data inserted")


class ECUserView(viewsets.ModelViewSet):
    queryset = ECUser.objects.all()
    serializer_class = ECUserSerializer
    def create(self, request):
        print(request.data,"user")
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=0,message="data inserted")


# Create your views here.
class CodeView(viewsets.ModelViewSet):
    queryset = CodeTable.objects.all()
    serializer_class = CodeSerializer
    def create(self, request):
        print(request.data,"Code")
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=0,message="data inserted")
