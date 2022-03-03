from django.contrib import admin

# Register your models here.
from .models import ActionReport, Invoice, InvoiceOrder, Scheduler

admin.site.register(Scheduler)
admin.site.register(Invoice)
admin.site.register(ActionReport)
admin.site.register(InvoiceOrder)
# admin.site.register(SchedulerInvoice)

class SchedulerItemAdmin(admin.ModelAdmin):
    list_display = ["scheduler","customer"]


# admin.site.register(SchedulerItem,SchedulerItemAdmin)
