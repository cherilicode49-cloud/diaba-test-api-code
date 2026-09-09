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
from diabaApp.serializer import AppDynamicSettingSerializer, ProductDataSerializer, RecentlyViewProductSerializer, CategoryDetailSerializer, \
    AboutUsSerializer, PrivacyPolicySerializer, RefundPolicySerializer, TermsAndConditionSerializer, ImportantNoteSerializer, \
    IntroBannerSerializer
from django.db.models.functions import Random

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL


@csrf_exempt
def app_setting(request):
    if request.method == "POST":
        setting = models.AppDynamicSetting.objects.all().first()
        setting_serializer = AppDynamicSettingSerializer(setting).data
    

        res={
            'data':setting_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)


@csrf_exempt
def admin_app_dynamic_setting(request):
    if request.method == "POST":
        setting = models.AppDynamicSetting.objects.all().first()

        setting_serializer = AppDynamicSettingSerializer(setting).data

        res={
            'data':setting_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)


@csrf_exempt
def app_dyanmic_setting_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        print('pytohn_data---app_dyanmic_setting_update--->',python_data)

        # login_page = python_data.get('login_page',None)
        # otp_page = python_data.get('otp_page',None)
        # subscription_page = python_data.get('subscription_page',None)
        # ios_free_content = python_data.get('ios_free_content',None)
        app_version = python_data.get('app_version',None)
        release_note = python_data.get('release_note',None)

        if models.AppDynamicSetting.objects.all().count() > 0:
            setting = models.AppDynamicSetting.objects.all().first()

            # if not isinstance(login_page, str):
            #     setting.login_page = login_page
            # if not isinstance(otp_page, str):
            #     setting.otp_page = otp_page
            # if not isinstance(subscription_page, str):
            #     setting.subscription_page = subscription_page
                
            # setting.ios_free_content = python_data.get('ios_free_content',setting.ios_free_content)
            setting.release_note = python_data.get('release_note',setting.release_note)
            setting.app_version = python_data.get('app_version',setting.app_version)

            setting.save()

        else:
            models.AppDynamicSetting.objects.create(
                # login_page = login_page,
                # otp_page = otp_page,
                # subscription_page = subscription_page,
                # ios_free_content = ios_free_content,
                app_version = app_version,
                release_note = release_note,
            )

        res={
            'message':'Settings Updated'
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)



@csrf_exempt
def app_dashboard(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)

    currencyCode = python_data.get('currencyCode',None)
    countryCallingCode = python_data.get('countryCallingCode',None)
    country = python_data.get('countryName','Egypt')
    ip_address = python_data.get('ip_address')
    user_id = python_data.get('user_id')
    country_id = python_data.get('country_id', None)

    page_number = python_data.get('page_number',1)

    # f("python_data--app_dashboard_dummy-->",python_data)
    
    try:
        if currencyCode not in [None,'','null']:
            country = models.CountryWithCurrency.objects.filter(currency_code = currencyCode).first().country_name
        elif countryCallingCode not in [None,'','null']:
            country = models.CountryWithCurrency.objects.filter(country_calling_code = countryCallingCode).first().country_name
            
        elif user_id:
            user = models.CustomerDetail.objects.get(id = user_id)
            countryCode = user.countryCode

            if models.CountryWithCurrency.objects.filter(country_calling_code = countryCode).exists():
                country = models.CountryWithCurrency.objects.get(country_calling_code = countryCode).country_name
            else:
                if country not in [None,'','null']:
                    country = country
                else:
                    try:
                        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                        response = response.json()
                        country = response.get("country_name")
                        # print("response====>",response)

                        if country in [None,'','null']:
                            country = "Egypt"

                    except Exception as e:
                        # print("Errroooorrr----->",e)
                        country = "Egypt"
                    

        else:
            if country in [None,'','null']:
                try:
                    response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                    response = response.json()
                    country = response.get("country_name")
                    # print("response====>",response)

                    if country in [None,'','null']:
                        country = "Egypt"

                except Exception as e:
                    # print("Errroooorrr----->",e)
                    country = "Egypt"
            else:
                country = country
    except Exception as e:
        # print("Error-=-=-=--->",e)
        country = 'Egypt'

   

    page_record = 20
    last_row = page_record * page_number
    first_row = last_row - page_record

    # get_country_name = models.ProductCountry.objects.filter(id = country_id)
    # available_country_name = get_country_name.name

    if country_id != None:
        total_pages =  math.ceil(models.ProductDetail.objects.filter(status='Active',available_country = country_id).order_by('-id').count()/page_record)
        
        list_data = []

        all_product_data = models.ProductDetail.objects.filter(status='Active', available_country = country_id).exclude(category__category='Intimate Universe and Comfort').order_by(Random())[first_row:last_row]
        product_serializer = ProductDataSerializer(all_product_data, many=True, context = {'country':country}).data
        

        if user_id and page_number == 1:
            product = models.RecentlyViewProduct.objects.filter(customer = user_id, product__status = 'Active', product__available_country = country_id).order_by('-id')[:5]
            recently_serializer = RecentlyViewProductSerializer(product, many=True, context = {'country':country}).data
            res = {
                'product_list': product_serializer,
                'total_pages':total_pages,
                'recently_view':recently_serializer,
                'recently_title':'Recently Browsed',
                'recently_title_fr':'Consulté récemment'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res = {
                'product_list': product_serializer,
                'total_pages':total_pages,
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
    else:
        total_pages =  math.ceil(models.ProductDetail.objects.filter(status='Active').order_by('-id').count()/page_record)
        
        list_data = []

        all_product_data = models.ProductDetail.objects.filter(status='Active').exclude(category__category='Intimate Universe and Comfort').order_by(Random())[first_row:last_row]
        product_serializer = ProductDataSerializer(all_product_data, many=True, context = {'country':country}).data
        

        if user_id and page_number == 1:
            product = models.RecentlyViewProduct.objects.filter(customer = user_id, product__status = 'Active').order_by('-id')[:5]
            recently_serializer = RecentlyViewProductSerializer(product, many=True, context = {'country':country}).data
            res = {
                'product_list': product_serializer,
                'total_pages':total_pages,
                'recently_view':recently_serializer,
                'recently_title':'Recently Browsed',
                'recently_title_fr':'Consulté récemment'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res = {
                'product_list': product_serializer,
                'total_pages':total_pages,
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def app_dashboard_category(request):
    list_category = []    
    all_category = models.CategoryDetail.objects.filter(status = 'Active').exclude(category='Intimate Universe and Comfort')
    for category in all_category:
        check_subcategory_count = models.SubCategoryDetail.objects.filter(category = category.id).count()
        if check_subcategory_count > 0:
            category_data = models.CategoryDetail.objects.get(id = category.id)
            category_serializer = CategoryDetailSerializer(category_data).data
            list_category.append(category_serializer)
        
    res = {
        'data':list_category,  
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def about_us_list(request):
    if request.method == "POST":
        
        about_us = models.AboutUs.objects.all().first()
        about_us_serializer = AboutUsSerializer(about_us).data

        res={
            'data':about_us_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def about_us_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=----about_us_update=--->", python_data)

        id = python_data.get('id',None)
        about_us = python_data.get('about_us',None)

        get_about_us = models.AboutUs.objects.get(id = id)
        get_about_us.about_us = about_us
        get_about_us.save()

        res={
            'message':'About Us Updated Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def privacy_policy_list(request):
    if request.method == "POST":
        get_privacy_policy = models.PrivacyPolicy.objects.all().first()
        get_privacy_policy_serializer = PrivacyPolicySerializer(get_privacy_policy).data

        res={
            'data':get_privacy_policy_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def privacy_policy_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=----privacy_policy_update=--->", python_data)

        id = python_data.get('id',None)
        privacy_policy = python_data.get('privacy_policy',None)

        get_privacy_policy = models.PrivacyPolicy.objects.get(id = id)
        get_privacy_policy.privacy_policy = privacy_policy
        get_privacy_policy.save()

        res={
            'message':'About Us Updated Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def refund_policy_list(request):
    if request.method == "POST":
        get_refund_policy = models.RefundPolicy.objects.all().first()
        get_refund_policy_serializer = RefundPolicySerializer(get_refund_policy).data

        res={
            'data':get_refund_policy_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def refund_policy_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=----refund_policy_update=--->", python_data)

        id = python_data.get('id',None)
        refund_policy = python_data.get('refund_policy',None)

        get_refund_policy = models.RefundPolicy.objects.get(id = id)
        get_refund_policy.refund_policy = refund_policy
        get_refund_policy.save()

        res={
            'message':'Refund Policy Updated Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def terms_and_condition_list(request):
    if request.method == "POST":
        get_terms_and_condition = models.TermsAndCondition.objects.all().first()
        get_terms_and_condition_serializer = TermsAndConditionSerializer(get_terms_and_condition).data

        res={
            'data':get_terms_and_condition_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def terms_and_condition_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=----terms_and_condition=--->", python_data)

        id = python_data.get('id',None)
        terms_and_condition = python_data.get('terms_and_condition',None)

        get_privacy_policy = models.TermsAndCondition.objects.get(id = id)
        get_privacy_policy.terms_and_condition = terms_and_condition
        get_privacy_policy.save()

        res={
            'message':'Refund Policy Updated Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def important_note_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        note_update = models.ImportantNote.objects.get(id = id)
        note_update.note = python_data.get('note', note_update.note)
        note_update.note_french = python_data.get('note_french', note_update.note_french)
        note_update.status = python_data.get('status', note_update.status)
        note_update.save()
       
        res = {
            'message':'Note update.'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
 
@csrf_exempt
def important_note_list(request):
    if request.method == "POST":
        important_note = models.ImportantNote.objects.all().first()
        note_serialser = ImportantNoteSerializer(important_note).data
        res = {
            'data':note_serialser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def intro_banner_update(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
 
    for i,j in request.POST.items():
        python_data.update({i:j})
   
    id = python_data.get('id')
    banner = python_data.get('banner')
 
 
    banner_update = models.IntroBanner.objects.get(id = id)
    if type(banner) != str:
        banner_update.banner = banner
    banner_update.save()
   
    res = {
        'message':"Updated successfully."        
        }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def intro_banner_data(request):
    if request.method == 'POST':
        project_list = models.IntroBanner.objects.all().first()
       
        serialiser = IntroBannerSerializer(project_list).data
        res = {
            'data':serialiser        
            }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)  
