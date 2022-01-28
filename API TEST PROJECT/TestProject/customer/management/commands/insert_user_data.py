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
        user_file = pd.read_csv("D:/TnuTaral/users.csv")
        user_file = json.loads(user_file.to_json(orient='records'))
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        start = 0
        length = 1
        codes = CodeTable.objects.filter().values("id","code")
        code_ids = get_dict("code","id",codes)
        while True:
            users = user_file[start:(start + length)]
            ec_contact_ids = [x["ecContactId"] for x in users]
            contacts = Contact.objects.filter(ec_contact_id__in=ec_contact_ids).values("id","ec_contact_id")
            contact_ids = get_dict("ec_contact_id","id",contacts)
            ec_customer_ids = [x["eccompanyId"] for x in users]
            customers = Customer.objects.filter(ec_customer_id__in=ec_customer_ids).values("id","ec_customer_id")
            customer_ids = get_dict("ec_customer_id","id",customers)
            if len(users) == 0:
                    break
            users_data  = []
            for user in users:
                users_data.append({
                    'company': customer_ids[user['eccompanyId']] if user['eccompanyId'] in customer_ids else None,
                    'username': user['UserName'],
                    'password': user['Password'],
                    'contact': contact_ids[user['ecContactId']] if user['ecContactId'] in contact_ids else None,
                    'language': code_ids[user['LanguageId']] if user['LanguageId'] in code_ids else None,
                    'is_power_user': True if user['IsPowerUser'] == 1 else False,
                    'is_deleted': True if user['isDeleted'] == 1 else False,
                    'is_active': True if  user['IsActive'] == 1 else False,


                    })

            # #--------------call API ------------------------
            print(users_data,"users_data")
            start += length
            time.sleep(1)
            url = 'http://127.0.0.1:8000/dt/customer/user/'
            response = requests.post(url, data=json.dumps(users_data), headers=headers)
            print(response,"response")
        print("==> data inserted finished")


def get_dict(key, val, records):
        dict = {}
        for record in records:
            dict[record[key]] = record[val]
        return dict
