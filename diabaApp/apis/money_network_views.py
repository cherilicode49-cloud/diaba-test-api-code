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
from django.http import JsonResponse

import requests
from django.template.loader import get_template
from django.core.mail import send_mail
from diabaApp.serializer import CountryWiseBankDetailSerializer, MoneyNetworkSerializer

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL

@csrf_exempt
def all_money_network_list(request):
    list_data = []
    all_country = models.CountryMoneyNetwork.objects.all()
    for country in all_country:
        country = models.CountryMoneyNetwork.objects.get(id = country.id)
        country_dict = {}
        title = country.country_name
        key = country.key

        all_network = models.MoneyNetwork.objects.filter(country = country.id).order_by('id')
        serializer = MoneyNetworkSerializer(all_network, many=True).data
        country_dict.update({'title':title, 'key':key, 'options':serializer})
        list_data.append(country_dict)

    res = {
        'data': list_data 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def money_network_list(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        country_key = python_data.get('country_key')
        amount = python_data.get('amount')
        print(python_data, 'python_data')
        all_network = models.MoneyNetwork.objects.filter(country__key = country_key, status="Active").order_by('id')
        serializer = MoneyNetworkSerializer(all_network, many=True).data
                
        check_cash_record = models.CountryCashLimit.objects.filter(country__country_iso_alphaTwo_key = country_key).count()
        if check_cash_record == 1:
            cash_record = models.CountryCashLimit.objects.get(country__country_iso_alphaTwo_key = country_key)
            print(cash_record, int(cash_record.cash_limit))
            if int(cash_record.cash_limit) > int(amount):
                print(True)
                all_network = models.MoneyNetwork.objects.filter(country__key = country_key,status="Active").exclude(value__in = ["cash","bank"]).order_by('id')
                serializer = MoneyNetworkSerializer(all_network, many=True).data
            else:
                print(False)
                all_network = models.MoneyNetwork.objects.filter(country__key = country_key,status="Active").order_by('id')
                serializer = MoneyNetworkSerializer(all_network, many=True).data
                
                print("serializer---->",serializer)

                bank_detail  = models.CountryWiseBankDetail.objects.filter(country__country_iso_alphaTwo_key = country_key).order_by('id').first()
                bank_detail_serializer = CountryWiseBankDetailSerializer(bank_detail).data

                [item.update({'bank_detail': bank_detail_serializer}) for item in serializer if item.get('value') == 'bank']

                print("serializer--->",serializer)
            

        else:
           serializer = [{
            "label": "Inquiry",
            "value": "cash",
            "icon": "https://diaba-live.s3.eu-west-3.amazonaws.com/image/network_icon/ic_cash_EG9Hcsv.png",
            }]

        if serializer == []:
           serializer = [{
            "label": "Inquiry",
            "value": "cash",
            "icon": "https://diaba-live.s3.eu-west-3.amazonaws.com/image/network_icon/ic_cash_EG9Hcsv.png",
            }]
            
                
        res = {
            'data': serializer 
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)
