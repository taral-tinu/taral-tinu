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
from customer.models import Contact
from dateutil import parser
from django.core.management.base import BaseCommand
from django.http import response


# from base.util import Util
class Command(BaseCommand):
    help = ""
    def handle(self, *args, **options):
        countries_file = pd.read_csv("D:/TnuTaral/country.csv")
        countries_file = json.loads(countries_file.to_json(orient='records',date_format = 'iso'))
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        start = 0
        length = 50
        while True:
            countries = countries_file[start:(start + length)]
            if len(countries) == 0:
                    break
            countries_data  = []
            for country in countries:
                print(country,"country")
                countries_data.append({
                    'name': country['Name'] if country['Name'] else "",
                    'code': country['Initial'] if country['Initial'] else "",
                    })

            # #--------------call API ------------------------
            # print(countries_data,"customer_data")
            start += length
            time.sleep(1)
            url = 'http://192.168.1.247:8001/dt/customer/country/'
            response = requests.post(url, data=json.dumps(countries_data), headers=headers)
            print(response,"response")
        print("==> data inserted finished")


def get_code_ids(key, val, records):
        dict = {}
        for record in records:
            dict[record[key]] = record[val]
        return dict
