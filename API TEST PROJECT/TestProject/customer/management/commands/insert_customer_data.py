# -*- coding: utf-8 -*-
# from base.models import *
# from products.models import *
import datetime
import json
import time
from datetime import date, datetime

import pandas as pd
import requests
from base.models import CodeTable, Currency
from customer.models import Contact
from dateutil import parser
from django.core.management.base import BaseCommand


# from base.util import Util
class Command(BaseCommand):
    help = ""
    def handle(self, *args, **options):
        customers = pd.read_excel("D:/TnuTaral/ECdata/Customers2.xlsx")
        customers = json.loads(customers.to_json(orient='records',date_format = 'iso'))
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        start = 0
        length = 75
        while True:
            customer_data = customers[start:(start + length)]
            if len(customer_data) == 0:
                break
            # print(customer_data,"customer_data")
            start += length
            time.sleep(1)
            url = 'http://192.168.1.247:8001/dt/customer/customer/'
            response = requests.post(url, data=json.dumps(customer_data,cls=DateEncoder), headers=headers)
            print(response,"response",start)
        print("==> data inserted finished")


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)

def get_dict(key_name, val, records):
        code_ids = {}
        for record in records:
            code_ids[record[key_name]] = record[val]

        return code_ids
