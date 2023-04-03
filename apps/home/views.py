# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import JsonResponse
import json
import random
import string


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

@login_required(login_url='/login/')
def create_users(request):
    """
        DOCs:
    """
    err=''
    pwd = ''.join(random.choice(string.printable) for i in range(12))

    requestData = json.loads(request.POST.get("data"))
    if requestData['permissao'] == "admin":
        superUsr = True
    else:
        superUsr = False
    try:
        User = get_user_model().objects.create_user(
            username=requestData['name'],
            email=requestData['email'],
            password=pwd,
            is_staff=True,
            is_superuser=superUsr,
            is_active=requestData['status']
        )
        result='success'
    except Exception as e:
        err=str(e)
        if "duplicate key value violates unique constraint" in str(e):
            result='Usuário e/ou email já existe'
        else:
            result='Algo deu errado ao criar o usuário'

    return JsonResponse({'msg': result,'pwd':pwd,'err':err})

@login_required(login_url="/login/")
def delete_user(request):
    requestData = json.loads(request.POST.get("data"))

    User = get_user_model().objects.get(id=requestData['id'])

    User.delete()

    return JsonResponse({'msg': 'success'})

@login_required(login_url="/login/")
def update_user(request):
    requestData = json.loads(request.POST.get("data"))

    User = get_user_model()
    userUpdate = User.objects.get(id=requestData['id'])

    #   <option value="1">Usuário Comum</option>
    #                 <option value="2">Editor</option>
    #                 <option value="3">Admin</option>
    if requestData['permissao'] == '1':
        staff = 0
        admin = 0
    elif requestData['permissao'] == '2':
        staff = 1
        admin = 0
    elif requestData['permissao'] == '3':
        staff = 1
        admin = 1

    userUpdate.first_name = requestData['name']
    userUpdate.email = requestData['email']
    userUpdate.username = requestData['username']
    userUpdate.is_superuser = admin
    userUpdate.is_staff = staff
    userUpdate.is_active = requestData['status']

    userUpdate.save()

    return JsonResponse({'msg': 'success'})

@login_required(login_url="/login/")
def get_users(request):

    User = get_user_model()
    users = User.objects.all() \
        .values('id', 'last_login', 'is_superuser', 'username', 'first_name', 'last_name',
                'email', 'is_staff', 'is_active')

    return JsonResponse(
        {
            'data': list(users)
        }
    )
