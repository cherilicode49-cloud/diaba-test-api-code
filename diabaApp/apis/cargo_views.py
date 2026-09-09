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
from diabaApp.serializer import CargoDetailSerializer, PaymentCargoSliderSerializer

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL




@csrf_exempt
def cargo_create(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        country = python_data.get('country')
        cargo_name = python_data.get('cargo_name')
        email = python_data.get('email')
        air_express_address = python_data.get('air_express_address')
        air_express_number = python_data.get('air_express_number')
        air_express_postal_code = python_data.get('air_express_postal_code')
        ship_address = python_data.get('ship_address')
        ship_number = python_data.get('ship_number')
        ship_postal_code = python_data.get('ship_postal_code')
        status = python_data.get('status')
        
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        create_cargo = models.CargoDetail.objects.create(
            country_id = country,
            cargo_name = cargo_name,
            email = email,
            air_express_address = air_express_address,
            air_express_number = air_express_number,
            air_express_postal_code = air_express_postal_code,
            ship_address = ship_address,
            ship_number = ship_number,
            ship_postal_code = ship_postal_code,
            status = "Active",
            created_at = date_time
        ).save()        
        res = {
            'message': 'Cargo Added Successfully.' 
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)



@csrf_exempt
def cargo_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        id = python_data.get('id')
        update = models.CargoDetail.objects.get(id = id)
        update.country_id = python_data.get('country', update.country)
        update.cargo_name = python_data.get('cargo_name', update.cargo_name)
        update.email = python_data.get('email', update.email)
        
        update.air_express_address = python_data.get('air_express_address', update.air_express_address)
        update.air_express_number = python_data.get('air_express_number', update.air_express_number)
        update.air_express_postal_code = python_data.get('air_express_postal_code', update.air_express_postal_code)
        update.ship_address = python_data.get('ship_address', update.ship_address)
        update.ship_number = python_data.get('ship_number', update.ship_number)
        update.ship_postal_code = python_data.get('ship_postal_code', update.ship_postal_code)
        update.status = python_data.get('status', update.status)
        update.save()        
        
        res = {
            'message': 'Cargo data update Successfully.' 
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def cargo_status_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        id = python_data.get('id')
        update = models.CargoDetail.objects.get(id = id)
        update.status = python_data.get('status', update.status)
        update.save()        
        
        res = {
            'message': 'Status update Successfully.' 
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def all_cargo_list(request):
    all_cargo = models.CargoDetail.objects.all()
    serialiser = CargoDetailSerializer(all_cargo, many=True).data
    res = {
        'data': serialiser 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def cargo_list_app(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))
    country_calling_code = python_data.get('country_calling_code')
    check_country = models.CountryWithCurrency.objects.filter(country_calling_code = country_calling_code).count()
    if check_country == 1:
        country = models.CountryWithCurrency.objects.get(country_calling_code = country_calling_code)    
        all_cargo = models.CargoDetail.objects.filter(is_cargo_for_all=True)
        serialiser = CargoDetailSerializer(all_cargo, many=True).data
        print(country, 'country')
        country_cargo = models.CargoDetail.objects.filter(country = country.id)
        country_serialiser = CargoDetailSerializer(country_cargo, many=True).data
        serialiser.extend(country_serialiser)
    else:
        all_cargo = models.CargoDetail.objects.filter(is_cargo_for_all=True)
        serialiser = CargoDetailSerializer(all_cargo, many=True).data

    res = {
        'data': serialiser 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def payment_cargo_banner_create(request):
    if request.method == "POST":
        python_data = {}
        for i,j in request.FILES.items():
            python_data.update({i:j})
        
        for i,j in request.POST.items():
            python_data.update({i:j})

        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        payment = models.PaymentCargoSlider.objects.create(
            banner = python_data.get('banner'),
            status = 'Active',
            created_at = date_time
        ).save()
        
        res = {
            'message':"Banner Added successfully."
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def payment_cargo_banner_update(request):
    if request.method == "POST":
        python_data = {}
        for i,j in request.FILES.items():
            python_data.update({i:j})
        
        for i,j in request.POST.items():
            python_data.update({i:j})

        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        id = python_data.get('id')
        check_payment = models.PaymentCargoSlider.objects.filter(id = id).count()
        if check_payment == 1:
            payment = models.PaymentCargoSlider.objects.get(id = id)
            if type(python_data.get('banner')) != str:
                payment.banner = python_data.get('banner', payment.banner)
            payment.status = python_data.get('status', payment.status)
            payment.save()
        
            res = {
                'message':"Banner update successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        else:
            res = {
                'message':"Something went wrong."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def payment_cargo_banner_status_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        check_payment = models.PaymentCargoSlider.objects.filter(id = id).count()
        if check_payment == 1:
            payment = models.PaymentCargoSlider.objects.get(id = id)
            payment.status = python_data.get('status', payment.status)
            payment.save()
        
            res = {
                'message':"Banner update Successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        else:
            res = {
                'message':"Something went wrong."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def all_payment_cargo_banner_list(request):
    if request.method == "POST":
        
        payment_data = models.PaymentCargoSlider.objects.all()
        serialser = PaymentCargoSliderSerializer(payment_data, many=True).data
        res = {
            'data':serialser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


