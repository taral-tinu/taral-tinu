from msilib.schema import CustomAction
from sqlite3 import Cursor

from django.contrib import admin

# Register your models here.
from .models import Contact, Country, Customer, ECUser, State

admin.site.register(Customer)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(ECUser)
admin.site.register(Contact)

