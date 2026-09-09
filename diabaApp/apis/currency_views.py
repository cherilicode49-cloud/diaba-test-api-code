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
from diabaApp.serializer import AdminCountryWithCurrencyListSerializer, AdminCurrencyConverterSerializer

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL


@csrf_exempt
def create_countrywithcurrency(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        print("python_data--create_countrywithcurrency---->",python_data)

        country_calling_code = python_data.get('country_calling_code',None)
        country_name = python_data.get('country_name',None)
        currency_code = python_data.get('currency_code',None)
        currency_symbol = python_data.get('currency_symbol',None)
        country_iso_alphaTwo_key = python_data.get('country_iso_alphaTwo_key',None)

        bank_detail = python_data.get('bank_detail',None)
        cash_limit = python_data.get('cash_limit',None)


        if models.CountryWithCurrency.objects.filter(country_calling_code = country_calling_code).exists():
            res = {
                'message':'Country Calling Code already Used'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        if models.CountryWithCurrency.objects.filter(country_name = country_name).exists():
            res = {
                'message':'Country Name already Used'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        country_add = models.CountryWithCurrency.objects.create(
            country_calling_code = country_calling_code,
            country_name = country_name,
            currency_code = currency_code,
            currency_symbol = currency_symbol,
            country_iso_alphaTwo_key = country_iso_alphaTwo_key,
        )

        if bank_detail not in [None,'','null',{}]:
            bank_detail_create = models.CountryWiseBankDetail.objects.create(
                country_id = country_add.id,
                holder_name = bank_detail['holder_name'],
                bank_name = bank_detail['bank_name'],
                account_number = bank_detail['account_number'],
                branch_name = bank_detail['branch_name'],
                branch_code = bank_detail['branch_code'],
            )

        if cash_limit not in [None,'','null',{}]:
            cash_limit_create = models.CountryCashLimit.objects.create(
                country_id = country_add.id,
                cash_limit = cash_limit,
            )
        
        res = {
            'message':'Country Added Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def countrywithcurrency_list_admin(request):
    if request.method == "POST":
        countrywithcurrency_list = models.CountryWithCurrency.objects.all().order_by('-id')
        countrywithcurrency_list_serializer = AdminCountryWithCurrencyListSerializer(countrywithcurrency_list, many=True).data

        res = {
            'data':countrywithcurrency_list_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def update_countrywithcurrency(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        print("python_data--update_countrywithcurrency---->",python_data)

        id = python_data.get('id',None)
        country_calling_code = python_data.get('country_calling_code',None)
        country_name = python_data.get('country_name',None)
        currency_code = python_data.get('currency_code',None)
        currency_symbol = python_data.get('currency_symbol',None)
        country_iso_alphaTwo_key = python_data.get('country_iso_alphaTwo_key',None)
        cash_limit = python_data.get('cash_limit',None)

        bank_detail = python_data.get('bank_detail',None)

        if models.CountryWithCurrency.objects.filter(country_calling_code = country_calling_code).exclude(id = id).exists():
            res = {
                'message':'Country Calling Code already Used'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        if models.CountryWithCurrency.objects.filter(country_name = country_name).exclude(id = id).exists():
            res = {
                'message':'Country Name already Used'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

        get_countrywithcurrency = models.CountryWithCurrency.objects.get(id = id)
        get_countrywithcurrency.country_calling_code = country_calling_code
        get_countrywithcurrency.country_name = country_name
        get_countrywithcurrency.currency_code = currency_code
        get_countrywithcurrency.currency_symbol = currency_symbol
        get_countrywithcurrency.country_iso_alphaTwo_key = country_iso_alphaTwo_key

        get_countrywithcurrency.save()

        if bank_detail not in [None,'','null',{}]:
            if  models.CountryWiseBankDetail.objects.filter(country = get_countrywithcurrency.id).exists():
                get_bank_detail = models.CountryWiseBankDetail.objects.get(country = get_countrywithcurrency.id)
                get_bank_detail.holder_name = bank_detail['holder_name']
                get_bank_detail.bank_name = bank_detail['bank_name']
                get_bank_detail.account_number = bank_detail['account_number']
                get_bank_detail.branch_name = bank_detail['branch_name']
                get_bank_detail.branch_code = bank_detail['branch_code']
                get_bank_detail.save()
            else:
                bank_detail_create = models.CountryWiseBankDetail.objects.create(
                country_id = get_countrywithcurrency.id,
                holder_name = bank_detail['holder_name'],
                bank_name = bank_detail['bank_name'],
                account_number = bank_detail['account_number'],
                branch_name = bank_detail['branch_name'],
                branch_code = bank_detail['branch_code'],
            )
        else:
            if bank_detail == {}:
                if  models.CountryWiseBankDetail.objects.filter(country = get_countrywithcurrency.id).exists():
                    get_bank_detail = models.CountryWiseBankDetail.objects.get(country = get_countrywithcurrency.id)
                    get_bank_detail.delete()


        
        if cash_limit not in [None,'','null',{}]:
            if  models.CountryCashLimit.objects.filter(country = get_countrywithcurrency.id).exists():
                if cash_limit in [None,'','null',0]:
                    cash_limit = None
                    
                get_bank_detail = models.CountryCashLimit.objects.get(country = get_countrywithcurrency.id)
                get_bank_detail.cash_limit = cash_limit
                get_bank_detail.save()
            else:
                cash_limit_create = models.CountryCashLimit.objects.create(
                country_id = get_countrywithcurrency.id,
                cash_limit =cash_limit,
            )


        res = {
            'message':'Country Updated Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

    

@csrf_exempt
def delete_countrywithcurrency(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        print("python_data--delete_countrywithcurrency---->",python_data)

        id = python_data.get('id',None)

        try:
            get_countrywithcurrency = models.CountryWithCurrency(id = id)
            get_countrywithcurrency.delete()

            res = {
                'message':'Country Deleted Successfully'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

        except:
            res = {
                'message':'Country Does not Exist'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def update_countrywithcurrency_price_by(request):
    if request.method == "POST":

        python_data = JSONParser().parse(io.BytesIO(request.body))

        print("python_data--update_countrywithcurrency_price_by---->",python_data)

        prices = python_data.get('prices',None)

        for pr in prices:
            try:
                id = pr['country_id']
                price_by_air = pr.get('price_by_air',None)
                price_by_ship = pr.get('price_by_ship',None)
                express_shipping = pr.get('express_shipping',None)

                get_countrywithcurrency = models.CountryWithCurrency.objects.get(id = id)
                get_countrywithcurrency.price_by_air = price_by_air
                get_countrywithcurrency.price_by_ship = price_by_ship
                get_countrywithcurrency.express_shipping = express_shipping
                get_countrywithcurrency.save()

                if get_countrywithcurrency.price_by_air not in [None,'','null'] and get_countrywithcurrency.price_by_ship not in [None,'','null']:
                    get_countrywithcurrency.status = 'Active'
                    get_countrywithcurrency.save()

            except:
                res = {
                    'message':'Few Price has not updated due to server issue'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


        res = {
            'message':'Price By Updated Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
    



@csrf_exempt
def currency_coversion(request):
    if request.method == "POST":
        # python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data--currency_coversion---->",python_data)

        # url = "https://api.freecurrencyapi.com/v1/latest?apikey=fca_live_iQa2JUQuTqahib1SZyl54TBUkPUIY7UfIoGPGZ1z&base_curreency=USD"
        # url = "https://api.exchangerate.host/latest"

        endpoint = "convert"
        access_key = "f2fd2d4b28e2ea8b345524bf52fe8ff4"
        from_currency = "USD"
        to_currency = "INR"
        amount = 10

        # url = f"https://api.exchangerate.host/{endpoint}?access_key={access_key}&from={from_currency}&to={to_currency}&amount={amount}"

        # response = requests.get(url)
        # data = response.json()

        # print("Full Response:", data)

        # # Access conversion result
        # if data.get("result") is not None:
        #     print("Converted Amount:", data["result"])
        # else:
        #     print("Error:", data.get("error"))


        source = "USD"
        currencies = "XOF,XAF,INR"

        url = f"http://api.exchangerate.host/live?access_key={access_key}&source={source}&currencies={currencies}&format=1"

        response = requests.get(url)
        data = response.json()


        # response = requests.get(url)

        res={
            'data':response.json()
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def currency_rates(request):
    if request.method == "POST":
        convert_currency = models.CurrencyConverter.objects.all().order_by('-id')
        convert_currency_serializer = AdminCurrencyConverterSerializer(convert_currency, many=True).data

        res={
            'data':convert_currency_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def currency_rates_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        print("python_data--currency_rates_update---->",python_data)

        rates = python_data.get('rates', None)

        for rate in rates:
            currency_code = rate.get('currency_code', None)
            system_rate = rate.get('system_rate', None)

            if models.CurrencyConverter.objects.filter(currency_code = currency_code).exists():
                convert_currency = models.CurrencyConverter.objects.get(currency_code = currency_code)
                convert_currency.system_rate = system_rate
                convert_currency.save()
            
            else:
                res={
                    'message':f'{currency_code} - Currency not Found'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

        res={
            'message':'Currency Updated Sucesssfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)