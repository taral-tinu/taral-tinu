from django.shortcuts import render
from rest_framework import viewsets
from TestProject.rest_config import APIResponse

from customer.models import Customer
from customer.serializer import CustomerSerializer

# Create your views here.



class CustomerView(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    print('KKKKKKKKKKKKKKKKKKKK')

    # create multiple objects
    def create(self, request):
        print(request.data,"LLLLLLLLLLLLLL")
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        return APIResponse(code=0,message="data created")
