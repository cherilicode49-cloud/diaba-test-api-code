from django.views.decorators.csrf import csrf_exempt
from diabaApp import models
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
import io
import math, random , calendar
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Sum, Count, F, Q, ExpressionWrapper,  OuterRef, Subquery
from django.db.models.functions import Cast, TruncMonth, Coalesce, ExtractMonth, Round, TruncDate
from django.db.models.fields import FloatField
from firebase_admin import messaging
import requests
from django.template.loader import get_template
from django.core.mail import send_mail
from django.http import JsonResponse
from django.db import connection, transaction
import uuid
import json
import openpyxl, requests
from django.utils import timezone
from django.db.models import Max, Min
from googletrans import Translator
from django.core.files.base import ContentFile, File
from PIL import Image
from io import BytesIO
import os 
from diabaApp.serializer import AdminDetailSerializer, AdminModuleRightsDetailSerializer, AdminCountrySerializer


@csrf_exempt
def sub_admin_register(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        email = python_data.get('email')
        countryCode = python_data.get('countryCode')
        mobileNumber = python_data.get('mobileNumber')
        name = python_data.get('name')
        password = python_data.get('password')


        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        # digits = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' 
        # password = ""
        # for i in range(6):
        #     password += digits[math.floor(random.random() * 52)]

        # # password = "abcdef"

        role_id = models.Role.objects.filter(roleName = "subadmin").first().id
        
        check_email = models.AdminDetail.objects.filter(email = email).count()
        if check_email == 0:
            create_customer = models.AdminDetail.objects.create(
                email = email,
                countryCode = countryCode,
                mobileNumber = mobileNumber,
                name = name,
                userType_id = role_id,
                password = password,
                status = 'Inactive',
                created_at = datetime.now()
            ).save()

            
            try:
                context = {
                    'subadmin_email':email,
                    'subadmin_password': password, 
                    'subadmin_name':name,
                    'current_year':datetime.now().year
                    }
                htmlgen = get_template("sub_admin_registration.html").render(context)
                # send_mail('Diaba - Team Onboarding',"password",'settings.EMAIL_HOST_USER',[email], fail_silently=False, html_message=htmlgen)

                send_mail(
                    subject='Diaba - Team Onboarding',
                    message='password',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                    html_message=htmlgen
                )
                
                # print("MAIL SENT SUCCESSFULLY-=-=-=-=-=-=-=-")
            except Exception as e:
                print("print------>",e)
                
        
            res={
                'message':"Sub Admin registerd successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'message':"This email is already linked to an existing account. Please use another one."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)


@csrf_exempt
def sub_admin_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        email = python_data.get('email')
        countryCode = python_data.get('countryCode')
        mobileNumber = python_data.get('mobileNumber')
        name = python_data.get('name')
        password = python_data.get('password')
        
        check_email = models.AdminDetail.objects.filter(email = email).count()
        if check_email == 1:
            sub_admin_update = models.AdminDetail.objects.get(email = email)
            
            sub_admin_update.countryCode =python_data.get('countryCode', sub_admin_update.countryCode)
            sub_admin_update.mobileNumber =python_data.get('mobileNumber', sub_admin_update.mobileNumber)
            sub_admin_update.name =python_data.get('name', sub_admin_update.name)
            sub_admin_update.password =python_data.get('password', sub_admin_update.password)
            sub_admin_update.status = python_data.get('status', sub_admin_update.status)
            sub_admin_update.save()
        
            res={
                'message':"Sub Admin update successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'message':"This email is already linked to an existing account. Please use another one."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)


@csrf_exempt
def sub_admin_list(request):
    if request.method == "POST":
        admin_list = models.AdminDetail.objects.filter(userType__roleName = 'subadmin').order_by('-id')
        admin_list_serializer = AdminDetailSerializer(admin_list, many=True).data

        res={
            'data':admin_list_serializer
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def sub_admin_module_rights_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        data = python_data.get('data')
        print(python_data, 'python_data')
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        ## Dashboard
        check_dashboard = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'dashboard').count()
        if check_dashboard == 0:
            dashboard = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'dashboard',
                view = data['dashboard']['view'],
                create = data['dashboard']['create'],
                update = data['dashboard']['update'],
                delete = data['dashboard']['delete'],
                last_update = date_time
                ).save()
        else:
            dashboard_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'dashboard')
            dashboard_update.view = data['dashboard']['view']
            dashboard_update.create = data['dashboard']['create']
            dashboard_update.update = data['dashboard']['update']
            dashboard_update.delete = data['dashboard']['delete']
            dashboard_update.last_update = date_time
            dashboard_update.save()

        ### Vendor
        check_vendor = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'vendor').count()
        if check_vendor == 0:
            vendor = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'vendor',
                view = data['vendor']['view'],
                create = data['vendor']['create'],
                update = data['vendor']['update'],
                delete = data['vendor']['delete'],
                last_update = date_time
                ).save()
        else:
            vendor_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'vendor')
            vendor_update.view = data['vendor']['view']
            vendor_update.create = data['vendor']['create']
            vendor_update.update = data['vendor']['update']
            vendor_update.delete = data['vendor']['delete']
            vendor_update.last_update = date_time
            vendor_update.save()

        ### product
        check_product = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'product').count()
        if check_product == 0:
            product = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'product',
                view = data['product']['view'],
                create = data['product']['create'],
                update = data['product']['update'],
                delete = data['product']['delete'],
                last_update = date_time
                ).save()
        else:
            product_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'product')
            product_update.view = data['product']['view']
            product_update.create = data['product']['create']
            product_update.update = data['product']['update']
            product_update.delete = data['product']['delete']
            product_update.last_update = date_time
            product_update.save()
        
        ## categories
        check_categories = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'categories').count()
        if check_categories == 0:
            categories = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'categories',
                view = data['categories']['view'],
                create = data['categories']['create'],
                update = data['categories']['update'],
                delete = data['categories']['delete'],
                last_update = date_time
                ).save()
        else:
            categories_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'categories')
            categories_update.view = data['categories']['view']
            categories_update.create = data['categories']['create']
            categories_update.update = data['categories']['update']
            categories_update.delete = data['categories']['delete']
            categories_update.last_update = date_time
            categories_update.save()
        

        ## support
        check_support = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'support').count()
        if check_support == 0:
            support = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'support',
                view = data['support']['view'],
                create = data['support']['create'],
                update = data['support']['update'],
                delete = data['support']['delete'],
                last_update = date_time
                ).save()
        else:
            support_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'support')
            support_update.view = data['support']['view']
            support_update.create = data['support']['create']
            support_update.update = data['support']['update']
            support_update.delete = data['support']['delete']
            support_update.last_update = date_time
            support_update.save()

        
        ## chatAgent
        check_chatAgent = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'chatAgent').count()
        if check_chatAgent == 0:
            chatAgent = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'chatAgent',
                view = data['chatAgent']['view'],
                create = data['chatAgent']['create'],
                update = data['chatAgent']['update'],
                delete = data['chatAgent']['delete'],
                last_update = date_time
                ).save()
        else:
            chatAgent_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'chatAgent')
            chatAgent_update.view = data['chatAgent']['view']
            chatAgent_update.create = data['chatAgent']['create']
            chatAgent_update.update = data['chatAgent']['update']
            chatAgent_update.delete = data['chatAgent']['delete']
            chatAgent_update.last_update = date_time
            chatAgent_update.save()
        
        
        ## settings
        check_settings = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'settings').count()
        if check_settings == 0:
            settings = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'settings',
                view = data['settings']['view'],
                create = data['settings']['create'],
                update = data['settings']['update'],
                delete = data['settings']['delete'],
                last_update = date_time
                ).save()
        else:
            settings_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'settings')
            settings_update.view = data['settings']['view']
            settings_update.create = data['settings']['create']
            settings_update.update = data['settings']['update']
            settings_update.delete = data['settings']['delete']
            settings_update.last_update = date_time
            settings_update.save()


        ## order
        check_order = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'order').count()
        if check_order == 0:
            order = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'order',
                view = data['order']['view'],
                create = data['order']['create'],
                update = data['order']['update'],
                delete = data['order']['delete'],
                last_update = date_time
                ).save()
        else:
            order_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'order')
            order_update.view = data['order']['view']
            order_update.create = data['order']['create']
            order_update.update = data['order']['update']
            order_update.delete = data['order']['delete']
            order_update.last_update = date_time
            order_update.save()


        ## user
        check_user = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'user').count()
        if check_user == 0:
            user = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'user',
                view = data['user']['view'],
                create = data['user']['create'],
                update = data['user']['update'],
                delete = data['user']['delete'],
                last_update = date_time
                ).save()
        else:
            user_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'user')
            user_update.view = data['user']['view']
            user_update.create = data['user']['create']
            user_update.update = data['user']['update']
            user_update.delete = data['user']['delete']
            user_update.last_update = date_time
            user_update.save()


         ## transaction
        # check_transaction = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'transaction').count()
        # if check_transaction == 0:
        #     transaction = models.AdminModuleRightsDetail.objects.create(
        #         admin_id = id, 
        #         module_name= 'transaction',
        #         view = data['transaction']['view'],
        #         create = data['transaction']['create'],
        #         update = data['transaction']['update'],
        #         delete = data['transaction']['delete'],
        #         last_update = date_time
        #         ).save()
        # else:
        #     transaction_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'transaction')
        #     transaction_update.view = data['transaction']['view']
        #     transaction_update.create = data['transaction']['create']
        #     transaction_update.update = data['transaction']['update']
        #     transaction_update.delete = data['transaction']['delete']
        #     transaction_update.last_update = date_time
        #     transaction_update.save()

         # tags
        check_tags = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'tags').count()
        if check_tags == 0:
            if data['tags']:
                tags = models.AdminModuleRightsDetail.objects.create(
                    admin_id = id, 
                    module_name= 'tags',
                    view = data['tags']['view'],
                    create = data['tags']['create'],
                    update = data['tags']['update'],
                    delete = data['tags']['delete'],
                    last_update = date_time
                    ).save()
        else:
            tags_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'tags')
            tags_update.view = data['tags']['view']
            tags_update.create = data['tags']['create']
            tags_update.update = data['tags']['update']
            tags_update.delete = data['tags']['delete']
            tags_update.last_update = date_time
            tags_update.save()
         
         # influencer
        check_influencer = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'influencer').count()
        if check_influencer == 0:
            if data['influencer']:
                influencer = models.AdminModuleRightsDetail.objects.create(
                    admin_id = id, 
                    module_name= 'influencer',
                    view = data['influencer']['view'],
                    create = data['influencer']['create'],
                    update = data['influencer']['update'],
                    delete = data['influencer']['delete'],
                    last_update = date_time
                    ).save()
        else:
            influencer_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'influencer')
            influencer_update.view = data['influencer']['view']
            influencer_update.create = data['influencer']['create']
            influencer_update.update = data['influencer']['update']
            influencer_update.delete = data['influencer']['delete']
            influencer_update.last_update = date_time
            influencer_update.save()
        
         # promocode
        check_promocode = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'promocode').count()
        if check_promocode == 0:
            if data['promocode']:
                promocode = models.AdminModuleRightsDetail.objects.create(
                    admin_id = id, 
                    module_name= 'promocode',
                    view = data['promocode']['view'],
                    create = data['promocode']['create'],
                    update = data['promocode']['update'],
                    delete = data['promocode']['delete'],
                    last_update = date_time
                    ).save()
        else:
            promocode_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'promocode')
            promocode_update.view = data['promocode']['view']
            promocode_update.create = data['promocode']['create']
            promocode_update.update = data['promocode']['update']
            promocode_update.delete = data['promocode']['delete']
            promocode_update.last_update = date_time
            promocode_update.save()
        
         # warehouse
        check_warehouse = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'warehouse').count()
        if check_warehouse == 0:
            if data['warehouse']:
                warehouse = models.AdminModuleRightsDetail.objects.create(
                    admin_id = id, 
                    module_name= 'warehouse',
                    view = data['warehouse']['view'],
                    create = data['warehouse']['create'],
                    update = data['warehouse']['update'],
                    delete = data['warehouse']['delete'],
                    last_update = date_time
                    ).save()
        else:
            warehouse_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'warehouse')
            warehouse_update.view = data['warehouse']['view']
            warehouse_update.create = data['warehouse']['create']
            warehouse_update.update = data['warehouse']['update']
            warehouse_update.delete = data['warehouse']['delete']
            warehouse_update.last_update = date_time
            warehouse_update.save()
        
         # cargo
        check_cargo = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'cargo').count()
        if check_cargo == 0:
            if data['cargo']:
                cargo = models.AdminModuleRightsDetail.objects.create(
                    admin_id = id, 
                    module_name= 'cargo',
                    view = data['cargo']['view'],
                    create = data['cargo']['create'],
                    update = data['cargo']['update'],
                    delete = data['cargo']['delete'],
                    last_update = date_time
                    ).save()
        else:
            cargo_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'cargo')
            cargo_update.view = data['cargo']['view']
            cargo_update.create = data['cargo']['create']
            cargo_update.update = data['cargo']['update']
            cargo_update.delete = data['cargo']['delete']
            cargo_update.last_update = date_time
            cargo_update.save()
        
         # country
        check_country = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'country').count()
        if check_country == 0:
            if data['country']:
                country = models.AdminModuleRightsDetail.objects.create(
                    admin_id = id, 
                    module_name= 'country',
                    view = data['country']['view'],
                    create = data['country']['create'],
                    update = data['country']['update'],
                    delete = data['country']['delete'],
                    last_update = date_time
                    ).save()
        else:
            country_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'country')
            country_update.view = data['country']['view']
            country_update.create = data['country']['create']
            country_update.update = data['country']['update']
            country_update.delete = data['country']['delete']
            country_update.last_update = date_time
            country_update.save()
        
         # inquiry
        check_inquiry = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'inquiry').count()
        if check_inquiry == 0:
            if data['inquiry']:
                inquiry = models.AdminModuleRightsDetail.objects.create(
                    admin_id = id, 
                    module_name= 'inquiry',
                    view = data['inquiry']['view'],
                    create = data['inquiry']['create'],
                    update = data['inquiry']['update'],
                    delete = data['inquiry']['delete'],
                    last_update = date_time
                    ).save()
        else:
            inquiry_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'inquiry')
            inquiry_update.view = data['inquiry']['view']
            inquiry_update.create = data['inquiry']['create']
            inquiry_update.update = data['inquiry']['update']
            inquiry_update.delete = data['inquiry']['delete']
            inquiry_update.last_update = date_time
            inquiry_update.save()

        res={
            'message':'User Rights update successfully.' 
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def sub_admin_module_rights_list(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        admin_rights = models.AdminModuleRightsDetail.objects.filter(admin = id)
        rights_serialiser = AdminModuleRightsDetailSerializer(admin_rights, many=True).data
        res={
            'data': rights_serialiser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def sub_admin_module_rights(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        module_name = python_data.get('module_name')
        print(python_data, 'python_data')
        admin_rights = models.AdminModuleRightsDetail.objects.get(admin = id, module_name = module_name)
        rights_serialiser = AdminModuleRightsDetailSerializer(admin_rights).data
        res={
            'data': rights_serialiser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def sub_admin_status_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        status = python_data.get('status')
        
        message = 'SubAdmin Status update.'
        if status == 'Active':
            check_rights = models.AdminModuleRightsDetail.objects.filter(admin = id).count()
            if check_rights == 0:
                status = 'Inactive'
                message = 'Please complete the admin rights submission first.'

            else:
                status = 'Active'
                message = 'SubAdmin Status update.'

        
        sub_admin_update = models.AdminDetail.objects.get(id =id )
        sub_admin_update.status = status
        sub_admin_update.save()

        res={
            'message':message
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def sub_admin_delete(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')

        if models.AdminDetail.objects.filter(id = id).exists():
            sub_admin_delete = models.AdminDetail.objects.filter(id = id).delete()
            res={
                'message':'Sub Admin Deleted Successfully'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res = {
                'message':'Sub Admin Not Found'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)


@csrf_exempt
def subadmin_credentials_resend(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        if models.AdminDetail.objects.filter(id = id).exists():
            sub_admin = models.AdminDetail.objects.get(id = id)
            try:
                context = {
                    'subadmin_email':sub_admin.email,
                    'subadmin_password': sub_admin.password, 
                    'subadmin_name':sub_admin.name,
                    'current_year':datetime.now().year
                    }
                htmlgen = get_template("resend_subadmin_creds.html").render(context)
                send_mail(
                    subject='Diaba - Login Credentials',
                    message='password',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[sub_admin.email],
                    fail_silently=False,
                    html_message=htmlgen
                )
            except Exception as e:
                print("print------>",e)
            res={
                'message':"Sub Admin credentials resent successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'message':'Sub Admin Not Found'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)    


@csrf_exempt
def country_list_admin(request):
    if request.method == "POST":
        country = models.Country.objects.all()
        serializer = AdminCountrySerializer(country, many=True).data

        res = {
            'data':serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


