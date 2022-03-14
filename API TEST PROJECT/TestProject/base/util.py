import datetime
import os

import pytz
from customer.models import Country
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.utils import timezone

from base.models import CodeTable, Currency

# from

# from dateutil import tz
class Util(object):
    @staticmethod
    def set_cache(key, value, time=3600):
        cache.set(key, value, time)

    @staticmethod
    def get_cache(key):
        if cache.has_key(key):
            return cache.get(key)
        return None

    @staticmethod
    def clear_cache(key):
        if cache.has_key(key):
            cache.delete(key)

    @staticmethod
    def get_resource_path(resource, resource_name):
        resource_path = os.path.join(settings.RESOURCES_ROOT, "resources")
        if resource == "profile":
            resource_path = os.path.join(resource_path, "profile_image")
        if resource_name:
            resource_path = os.path.join(resource_path, resource_name)
        return resource_path

    @staticmethod
    def get_resource_url(resource, resource_name):
        resource_url = settings.RESOURCES_URL + "resources/"
        if resource == "profile":
            resource_url += "profile_image/"
        resource_url += resource_name
        return resource_url

    @staticmethod
    def delete_old_file(path_file):
        if os.path.exists(path_file):
            os.remove(path_file)

    @staticmethod
    def get_dict_from_queryset(key_name, val, records):
        dict = {}
        for record in records:
            dict[record[key_name]] = record[val]

        return dict

    @staticmethod
    def get_utc_datetime(local_datetime, has_time):
        naive_datetime = None
        current_time_zone = timezone.get_current_timezone_name()
        local_time = pytz.timezone(current_time_zone)

        if has_time:
            naive_datetime = datetime.datetime.strptime(local_datetime, "%d/%m/%Y %H:%M")
        else:
            naive_datetime = datetime.datetime.strptime(local_datetime, "%d/%m/%Y")

        local_datetime = local_time.localize(naive_datetime, is_dst=None)
        utc_datetime = local_datetime.astimezone(pytz.utc)
        return utc_datetime

    @staticmethod
    def get_codes(code):
        codes = None
        if Util.get_cache(code) is None:
            if code == "code_table":
                print("code_table")
                codes = CodeTable.objects.values("code","id")
                Util.set_cache("code_table", codes, 3600)
            elif code == "currency":
                print("currency")
                codes = Currency.objects.values("code","id")
                Util.set_cache("currency", codes, 3600)
            elif code == "country":
                print("country")
                codes = Country.objects.values("code","id")
                Util.set_cache("country", codes, 3600)
        else:
            codes = Util.get_cache(code)
        # print("KKKKKKKKK")
        dict = Util.get_dict_from_queryset("code","id",codes)
        return dict
