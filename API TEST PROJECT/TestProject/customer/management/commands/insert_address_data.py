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
from customer.models import Country, Customer
from dateutil import parser
from django.core.management.base import BaseCommand
from django.http import response


# from base.util import Util
class Command(BaseCommand):
    help = ""
    def handle(self, *args, **options):
        address_file = pd.read_csv("D:/TnuTaral/addresses.csv")
        address_file = json.loads(address_file.to_json(orient='records',date_format = 'iso'))
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        start = 0
        length = 1
        countries = Country.objects.filter().values("id","code")
        country_ids = get_dict("code","id",countries)
        codes = CodeTable.objects.filter().values("id","code")
        code_ids = get_dict("code","id",codes)
        while True:
            addresses = address_file[start:(start + length)]
            if len(addresses) == 0:
                    break
            addresses_data  = []
            for address in addresses:
                print(address,"code")
                addresses_data.append({
                    'ec_address_id': address['companyId'],
                    'street_name': address['StreetName'],
                    'street_no': address['StreetNo'],
                    'street_address1': address['StreetAddress1'],
                    'street_address2': address['StreetAddress2'],
                    'city': address['City'],
                    'postal_code': address['PostalCode'],
                    'state': address['StateId'],
                    'other_state': address['OtherState'],
                    # 'country': country_ids[address['AddressTypeCode']] if address['AddressTypeCode'] in country_ids else None,#address['CountryCode'],
                    'address_type': codes[address['AddressTypeCode']] if address['AddressTypeCode'] in codes else None,
                    'is_deleted': address['IsDeleted'],
                    'address_name': address['AddressName'],
                    'contact_name': address['ContactName'],
                    'box_no': address['BoxNo'],
                    'is_primary': address['isPrimary'],
                    'email': address['email'],
                    'phone': address['Phone'],
                    'fax': address['Fax'],


                    })

            # #--------------call API ------------------------
            # print(customer_data,"customer_data")
            start += length
            time.sleep(1)
            # url = 'http://127.0.0.1:8000/dt/customer/address/'
            # response = requests.post(url, data=json.dumps(addresses_data,cls=DateEncoder), headers=headers)
            # print(response,"response")
        print("==> data inserted finished")


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)

def get_dict(key, val, records):
        dict = {}
        for record in records:
            dict[record[key]] = record[val]
        return dict
