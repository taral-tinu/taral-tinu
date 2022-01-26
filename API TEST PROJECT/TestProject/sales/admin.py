from django.contrib import admin

# Register your models here.
from .models import (CollectionAction, Invoice, InvoiceOrder, Scheduler,
                     SchedulerItem)

admin.site.register(Scheduler)
admin.site.register(SchedulerItem)
admin.site.register(Invoice)
admin.site.register(CollectionAction)
admin.site.register(InvoiceOrder)
