from atexit import register

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (CollectionAction, ContentPermission, Country, Customer,
                     GroupPermission, Invoice, MainMenu, PagePermission,
                     Scheduler, SchedulerItem, UserGroup, UserProfile)


class MainMenuAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "icon", "parent_id", "sequence", "menu_code")


class PagePermissionAdmin(admin.ModelAdmin):
    list_display = ("menu", "act_name", "act_code")


class ContentPermissionAdmin(admin.ModelAdmin):
    list_display = ("content_group", "content_name", "sequence")

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number","company")

class CollectionActionAdmin(admin.ModelAdmin):
    list_display = ("action_type",)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("is_active")

@admin.register(SchedulerItem)
class SchedulerItemAdmin(admin.ModelAdmin):
    list_display = ["scheduler","customer"]

@admin.register(Scheduler)
class SchedulerItemAdmin(admin.ModelAdmin):
    list_display = ["scheduler_name","created_on","status"]


admin.site.register(Invoice,InvoiceAdmin)
admin.site.register(Customer)
admin.site.register(CollectionAction,CollectionActionAdmin)
# admin.site.register(Scheduler)
# admin.site.register(SchedulerItem)
admin.site.register(Country)
# admin.site.register(UserProfile)
admin.site.register(GroupPermission)
admin.site.register(UserGroup)
admin.site.register(MainMenu, MainMenuAdmin)
admin.site.register(PagePermission, PagePermissionAdmin)
admin.site.register(ContentPermission, ContentPermissionAdmin)

# @admin.register(UserProfile)
# class UserAdmin(admin.ModelAdmin):

#     list_display  = ("user","image_tag")
