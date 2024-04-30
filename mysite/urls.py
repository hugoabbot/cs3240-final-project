"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from django.views.generic import TemplateView
# from .views import custom_logout, add_to_common_users, remove_from_common_users
from .views import custom_logout, remove_from_common_users, index
from django.contrib.auth.views import LogoutView
from .views import custom_logout
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('accounts/', include('allauth.urls')),
    path('logout/', custom_logout, name="custom_logout"),
    path('disclaimer/', TemplateView.as_view(template_name="disclaimer.html"), name='disclaimer'),
    # path('add_to_common_users_group/', add_to_common_users, name="add_to_common_users"),
    path('remove_from_common_users_group/', remove_from_common_users, name="remove_from_common_users"),
    #path('reports/', ReportCreateView.as_view(), name='report_form')
    path('reports/', include('reports.urls')),
  #  path('report/', views.report_form_view, name='report_form'),
    path('rules/', TemplateView.as_view(template_name="rules.html"), name='rules'),

    path('commonlogin/', TemplateView.as_view(template_name="commonlogin.html"), name='commonlogin' ),
    path('stafflogin/', TemplateView.as_view(template_name="stafflogin.html"), name='stafflogin'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
