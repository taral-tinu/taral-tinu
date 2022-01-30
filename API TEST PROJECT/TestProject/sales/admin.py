from django.contrib import admin

# Register your models here.
from .models import (CollectionActionReport, Invoice, InvoiceOrder, Scheduler,SchedulerInvoice,
                     SchedulerItem)

admin.site.register(Scheduler)
admin.site.register(Invoice)
admin.site.register(CollectionActionReport)
admin.site.register(InvoiceOrder)
admin.site.register(SchedulerInvoice)

class SchedulerItemAdmin(admin.ModelAdmin):
    list_display = ["scheduler","customer"]
    
    
admin.site.register(SchedulerItem,SchedulerItemAdmin)
