from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'main' # Добавяме namespace

urlpatterns = [
    path('', views.index, name='index'),
    path('generate/', views.generate_qr, name='generate_qr'),
    path('scan/', views.scan_qr, name='scan_qr'),
    path('history/', views.history, name='history'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)