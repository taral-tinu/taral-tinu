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
        contact_file = pd.read_csv("D:/TnuTaral/contacts1.csv")
        contact_file = json.loads(contact_file.to_json(orient='records',date_format = 'iso'))
        # print(contact_file,"customer_file")
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        start = 0
        length = 10
        total_records = len(contact_file)
        while True:
            contacts = contact_file[start:(start + length)]
            if len(contacts) == 0:
                    break
            contact_data  = []
            for contact in contacts:
                # print(contact,"contact")
                contact_data.append({
                    'ec_contact_id': contact['ecContactId'],
                    'first_name': contact['FirstName'],
                    'last_name': contact['LastName'],
                    'job_title': contact['JobTitle'],
                    'is_deleted': True if contact['IsDeleted'] else False,
                    })

            # #--------------call API ------------------------
            # print(contact_data,"contact_data")
            start += length
            time.sleep(1)
            url = 'http://127.0.0.1:8000/dt/customer/contact/'
            response = requests.post(url, data=json.dumps(contact_data,cls=DateEncoder), headers=headers)
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

def get_code_ids(key, val, records):
        dict = {}
        for record in records:
            dict[record[key]] = record[val]
        return dict
