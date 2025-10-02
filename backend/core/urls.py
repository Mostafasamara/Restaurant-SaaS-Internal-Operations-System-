from django.contrib import admin
from django.urls import path, include

# Import to trigger admin customization
import core.admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/sales/', include('sales.urls')),
]
