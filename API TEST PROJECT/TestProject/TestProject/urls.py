
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^dt/accounts/", include('api.urls')),
    url(r"^dt/customer/", include('customer.urls')),
    # url(r"^dt/base/", include('base.urls')),
    url(r"^dt/sales/", include('sales.urls')),
    
    
]
urlpatterns += static(settings.RESOURCES_URL, document_root=settings.RESOURCES_ROOT)
