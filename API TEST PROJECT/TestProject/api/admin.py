
from django.contrib import admin

from api.models import (ContentPermission, GroupPermission, MainMenu, PagePermission,
                       UserGroup)



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

admin.site.register(GroupPermission)
admin.site.register(UserGroup)
admin.site.register(MainMenu, MainMenuAdmin)
admin.site.register(PagePermission, PagePermissionAdmin)
admin.site.register(ContentPermission, ContentPermissionAdmin)

