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
        user_file = pd.read_csv("D:/TnuTaral/users.csv")
        user_file = json.loads(user_file.to_json(orient='records',date_format = 'iso'))
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        start = 0
        length = 1
        # contacts = Contact.objects.filter().values("id","code")
        # contacts = get_code_ids("code","id",contacts)
        codes = CodeTable.objects.filter().values("id","code")
        code_ids = get_code_ids("code","id",codes)
        while True:
            users = user_file[start:(start + length)]
            if len(users) == 0:
                    break
            addresses_data  = []
            for user in users:
                # print(user,"user")
                addresses_data.append({
                    # 'company': user['companyId'],
                    'username': user['UserName'],
                    'password': user['Password'],
                    # 'contact': user['companyId'],
                    # 'language': get_code_ids[user['LanguageId']] if user['LanguageId'] else None, #codetable
                    'is_power_user': True if user['IsPowerUser'] == 1 else False,
                    'is_deleted': True if user['isDeleted'] == 1 else False,
                    'is_active': True if  user['IsActive'] == 1 else False,


                    })

            # #--------------call API ------------------------
            # print(customer_data,"customer_data")
            start += length
            time.sleep(1)
            url = 'http://127.0.0.1:8000/dt/customer/user/'
            response = requests.post(url, data=json.dumps(addresses_data), headers=headers)
            print(response,"response")
        print("==> data inserted finished")


def get_code_ids(key, val, records):
        dict = {}
        for record in records:
            dict[record[key]] = record[val]
        return dict
