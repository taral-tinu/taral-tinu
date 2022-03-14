from django.shortcuts import render
from rest_framework import viewsets
from TestProject.rest_config import APIResponse

from base.models import CodeTable
from base.serializer import CodeSerializer


# Create your views here.
class CodeView(viewsets.ModelViewSet):
    queryset = CodeTable.objects.all()
    serializer_class = CodeSerializer
    def create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=0,message="data created")
