from django.contrib import admin
from django.urls import path, include, re_path

from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.http import HttpResponse
from django.urls import re_path


def favicon(request):
    return HttpResponse(status=204)




def home(request):
    return JsonResponse({"message": "Welcome to the Gepixelt  REST API!"})


urlpatterns = [
    path("", home),
    re_path(r'^favicon.ico$', favicon),
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('auth/', include('auths.urls')),
        path('products/', include('products.urls')),
        path('payment/', include('payments.urls')),
        path('orders/', include('orders.urls')),
        path('dashboard/', include('dashboard.urls')),
        path('weekly/', include('weekorder.urls')),
        
    ])),
 ]
