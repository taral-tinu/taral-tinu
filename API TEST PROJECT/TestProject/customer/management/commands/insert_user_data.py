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
from customer.models import Contact, Customer
from dateutil import parser
from django.core.management.base import BaseCommand
from django.http import response


# from base.util import Util
class Command(BaseCommand):
    help = ""
    def handle(self, *args, **options):
        user_file = pd.read_excel("D:/TnuTaral/ECdata/users.xlsx")
        user_file = json.loads(user_file.to_json(orient='records'))
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        start = 0
        length = 25
        while True:
            users_data = user_file[start:(start + length)]
            if len(users_data) == 0:
                    break
            start += length
            time.sleep(1)
            url = 'http://192.168.1.247:8001/dt/customer/user/'
            response = requests.post(url, data=json.dumps(users_data), headers=headers)
            print(response,"response",start)
        print("==> data inserted finished")


def get_dict(key, val, records):
        dict = {}
        for record in records:
            dict[record[key]] = record[val]
        return dict
