from msilib.schema import CustomAction
from sqlite3 import Cursor
from django.contrib import admin

# Register your models here.
from .models import Customer,Country,State,User,Contact

admin.site.register(Customer)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(User)
admin.site.register(Contact)

