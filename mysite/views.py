from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.models import Group
import logging
import pdb


# Create your views here.

common_users = Group.objects.get_or_create(name='Common Users')[0]
site_admins = Group.objects.get_or_create(name='Site Admins')[0]

def custom_logout(request):
    if request.user.is_authenticated:
            logout(request)
    return redirect('index')

def is_site_admin(user):
    return user.groups.filter(name='Site Admins').exists()

def is_common_user(user):
    return user.groups.filter(name='Common Users').exists()

# def add_to_common_users(request):
#     return request

def remove_from_common_users(request):
    Group.objects.get(name='Common Users').user_set.remove(request.user)
    return render(request, 'index.html', {'user': request.user, 'is_site_admin': True, 'is_common_user': False})

def index(request):
    if request.user.is_authenticated:
        user = request.user
        if is_site_admin(user):
            return render(request, 'stafflogin.html', {'user': user, 'is_site_admin': True, 'is_common_user': False})
        elif is_common_user(user):
            return render(request, 'commonlogin.html', {'user': user, 'is_site_admin': False, 'is_common_user': True})
        else:
            logging.debug("please reeach here")
            request.user.groups.add(common_users)
            request.user.save()
            return render(request, 'commonlogin.html', {'user': request.user, 'is_site_admin': False, 'is_common_user': True})
    else:
        return render(request, 'index.html')

def disclaimer(request):
    return render(request, 'disclaimer.html')

def rules(request):
    return render(request, 'rules.html')