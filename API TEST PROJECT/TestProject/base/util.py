import os

from django.conf import settings
from django.core.cache import cache
from django.db import connection

from base.models import SysParameter


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
    sys_param_key = "sys_parameters"
    def get_sys_paramter(key):
        sys_parameters = None
        new_sys_parameter = {}
        if Util.get_cache(connection.tenant.schema_name, Util.sys_param_key) is None:
            sys_parameters = SysParameter.objects.all()
            Util.set_cache(connection.tenant.schema_name, Util.sys_param_key, sys_parameters, 3600)
        else:
            sys_parameters = Util.get_cache(connection.tenant.schema_name, Util.sys_param_key)
        sys_param = None
        for param in sys_parameters:
            if param.para_code == key:
                sys_param = param
                break

        if sys_param is None and key in new_sys_parameter.keys():
            sys_parameter = None
            sys_parameter = SysParameter.objects.create(para_code=key, para_value=new_sys_parameter[key][0], descr=new_sys_parameter[key][1], for_system=new_sys_parameter[key][2])
            Util.clear_cache(connection.tenant.schema_name, Util.sys_param_key)
            sys_parameters = SysParameter.objects.all()
            Util.set_cache(connection.tenant.schema_name, Util.sys_param_key, sys_parameters, 3600)
            sys_param = sys_parameter
        return sys_param
