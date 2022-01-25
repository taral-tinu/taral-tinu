from django.contrib import admin

# Register your models here.
from .models import Scheduler,SchedulerItem,Invoice,CollectionAction

admin.site.register(Scheduler)
admin.site.register(SchedulerItem)
admin.site.register(Invoice)
admin.site.register(CollectionAction)
