import os

# from api.signals import DeleteOldFile
from django.conf import settings
from django.core.cache import cache


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



