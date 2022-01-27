# -*- coding: utf-8 -*-
# from base.models import *
# from products.models import *
import datetime
import json
import time
from datetime import date, datetime

import pandas as pd
import requests
import xlrd
from base.models import CodeTable
from customer.models import Customer
from dateutil import parser
from django.core.management.base import BaseCommand
from django.http import response


# from base.util import Util
class Command(BaseCommand):
    help = ""
    def handle(self, *args, **options):
        code_file = pd.read_csv("D:/TnuTaral/codes.xlsx")
        code_file = json.loads(code_file.to_json(orient='records',date_format = 'iso'))
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        start = 0
        length = 1
        total_records = len(code_file)
        while True:
            codes = code_file[start:(start + length)]
            if len(codes) == 0:
                    break
            code_data  = []
            for code in codes:
                print(code,"code")
                code_data.append({
                    'code': code['Code'],
                    'name': code['ShortDescription'],
                    'desc': code['UsageDescription'],
                    })

            # #--------------call API ------------------------
            # print(customer_data,"customer_data")
            start += length
            time.sleep(1)
            url = 'http://127.0.0.1:8000/dt/customer/code/'
            response = requests.post(url, data=json.dumps(code_data,cls=DateEncoder), headers=headers)
            print(response,"response")
        print("==> data inserted finished")


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)
