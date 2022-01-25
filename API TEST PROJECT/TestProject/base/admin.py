from django.contrib import admin

# Register your models here.

from .models import CodeTable,Currency

admin.site.register(CodeTable)
admin.site.register(Currency)
