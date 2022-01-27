from django.contrib import admin

from .models import CodeTable, Currency

# Register your models here.


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["name","symbol"]

class CodeAdmin(admin.ModelAdmin):
    list_display = ["name","code"]

admin.site.register(CodeTable,CodeAdmin)
admin.site.register(Currency,CurrencyAdmin)

