from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Customize Django Admin branding
admin.site.site_header = "ASTA Adoption Center Administration"
admin.site.site_title = "ASTA Admin Portal"
admin.site.index_title = "Welcome to ASTA Pet Adoption & Rescue Platform"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pets.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
