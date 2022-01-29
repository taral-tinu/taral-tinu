from types import CodeType

from dateutil import tz
from django.utils import timezone
from rest_framework import pagination, serializers
from rest_framework.response import Response
from rest_framework.views import exception_handler

from TestProject.util import Util


class CustomPagination(pagination.PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    page_query_param = 'page'

    def get_paginated_response(self, data):
        # print("PPPPPP")
        return Response({
            'totalRecords': self.page.paginator.count,
            'data': data
        })


class APIResponse(Response):

    def __init__(self, data="", code=1, message=""):
        print('IIIIIIIII')
        super().__init__({'code':code, 'data':data,'message':message})


def custom_exception_handler(exc, context):
    print("CCCCC")
    
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        print("RRRRR")
        response.data['status_code'] = response.status_code
        response.data['code'] = 0
        response.data['message'] = "Error occurred"

    return response

# represet absolute file path
class RepresentFilePath(serializers.FileField):
    def to_representation(self, instance):
        request = self.context.get('request')
        instance = str(instance)
        img_src = Util.get_resource_url("profile",instance) if instance else ""
        return request.build_absolute_uri(img_src.strip())

class LocalDateTime(serializers.DateTimeField):
    def to_representation(self, instance):
        current_time_zone = timezone.get_current_timezone_name()
        from_zone = tz.gettz("UTC")
        to_zone = tz.gettz(current_time_zone)
        utctime = instance.replace(tzinfo=from_zone)
        new_time = utctime.astimezone(to_zone)
        return new_time.strftime("%d/%m/%Y %H:%M")

