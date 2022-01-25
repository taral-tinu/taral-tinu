import pandas as pd
import xlrd
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

# from tenant_schemas.utils import schema_context


# class Command(BaseCommand):
# 	help = 'Generate user profile image.'

# 	def handle(self, *args, **options):
# 		# with schema_context('demo'):
# 		file = "C:/Users/admin/Downloads/MO06205-R1.xls"
# 		print(file)
# 		with transaction.atomic():
# 			start = 0
#             length = 50
# 			while True:
#     			customers = list(pd.read_excel(file).to_dict(orient="records"))[start:(start + length)]
# 				if len(customers) == 0:
# 					break
# 				for customer in customers:
# 						print("customer", customer)
