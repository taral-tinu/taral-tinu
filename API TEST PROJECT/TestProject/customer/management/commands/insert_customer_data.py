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
        customer_file = pd.read_excel("D:/TnuTaral/Customer.xlsx")
        customer_file = json.loads(customer_file.to_json(orient='records',date_format = 'iso'))
        print(type(customer_file[0]["LastOrderdate"]))
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        start = 0
        length = 10
        total_records = len(customer_file)
        while True:
            customers = customer_file[start:(start + length)]
            customer_data  = []
            for customer in customers:
                customer_data.append({
                    'ec_customer_id': customer['ecCustomerId'],
                    'company_name': customer['companyName'],
                    'initials': customer['Initials'],
                    'customer_type': customer['TypeCode'], #codetabel
                    'tax_number_type': customer['TaxNumberTypeCode'], #codetabel
                    'is_always_vat': True if customer['IsAlwaysVAT'] else False,
                    'status': customer['StatusIdCode'], #codetabel
                    'account_manager': customer['AccountManagerId'],
                    'is_deleted': True if customer['IsDeleted'] else False,
                    'is_allow_send_mail': True if customer['IsAllowSendMail'] else False,
                    'last_order_date': parser.parse(customer['LastOrderdate']) if customer['LastOrderdate'] else "",
                    'invoice_lang': customer['InvoiceLangCode'],
                    'account_number': customer['AccountNumber'],
                    'invoice_prefrence': customer['InvoicePrefrence'],
                    'invoice_postage': customer['InvoicePostage'],
                    'is_sales_review': True if  customer['IsSalesReview'] else False,
                    'is_vat_verified': True if customer['IsVATVerified'] else False,
                    'currency': customer['CurrencySymbol'],
                    'is_deliver_invoice_by_post': True if customer['isDeliverInvoiceByPost'] else False,
                    'is_duplicate': True if customer['IsDuplicate'] else False,
                    'is_exclude_vat': True if customer['IsExcludeVAT'] else False,
                    'is_student': True if customer['IsStudent'] else False,
                    'invoice_delivery': customer['InvoiceDelivery'], #codetabel
                    'sa_company_competence': customer['sa_company_competence'],
                    'sa_ec_customer': customer['sa_ec_customer'],
                    'is_peppol_verfied': True if  customer['isPeppolVerfied'] else False,
                    'peppol_address': customer['peppol_address'],
                    'is_teacher': True if customer['IsTeacher'] else False,
                    'is_student_team': True if customer['IsStudentTeam'] else False,
                    'is_call_report_attached': True if customer['is_call_report_attached'] else False
                })

            #--------------call API ------------------------
            print(customer_data,"customer_data")
            start += length
            time.sleep(1)
            url = 'http://127.0.0.1:8000/dt/customer/customer/'
            response = requests.post(url, data=json.dumps(customer_data,cls=DateEncoder), headers=headers)
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
