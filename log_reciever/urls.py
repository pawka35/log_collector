"""
URL configuration for log_reciever project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from logs_collector.views import export_logs_csv, log_list, receive_log, view_log_html


urlpatterns = [
    path('', log_list, name='log_list'),
    path('admin/', admin.site.urls),
    path('receiver', receive_log, name='receive_log'),
    path('logs/<int:pk>/html', view_log_html, name='view_log_html'),
    path('logs/export', export_logs_csv, name='export_logs_csv'),
]
