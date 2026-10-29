# lovnish/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Custom Admin Site Branding
admin.site.site_header = "Lovnish ID Card Generator Admin"
admin.site.site_title = "Lovnish Admin Portal"
admin.site.index_title = "Welcome to Lovnish ID Card Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
