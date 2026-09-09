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
from diabaApp.serializer import InfluencerDetailSerializer, PromocodeDetailSerializer

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL




@csrf_exempt
def influencer_login(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        print(python_data, 'python_data')
        email = python_data.get('email')
        password = python_data.get('password')
        
        if models.InfluencerDetail.objects.filter(email = email).exists():
            check_user = models.InfluencerDetail.objects.filter(email = email, password = password).count()
            print(check_user, 'check_user')
            
            if check_user == 1:
                
                user = models.InfluencerDetail.objects.get(email = email, password = password)
                user_id = user.id
                res={
                    'message':'Login Successfully.',
                    'influencer_id':user_id
                }
                return JsonResponse(res, content_type= 'application/json', status=200)
            else:
                res={
                    'message':'Enter valid password.'
                }
                return JsonResponse(res, content_type= 'application/json', status=406)


        else:
            res={
                'message':'Influencer Not Found Contact Admin '
            }
            return JsonResponse(res, content_type= 'application/json', status=406)

@csrf_exempt
def influencer_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        print(python_data, 'python_data')
        email = python_data.get('email')
        countryCode = python_data.get('countryCode')
        mobileNumber = python_data.get('mobileNumber')
        name = python_data.get('name')
        commission = python_data.get('commission')
        id = python_data.get('id')

        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        check_email = models.InfluencerDetail.objects.filter(email = email).count()
        if check_email == 1:
            influencer = models.InfluencerDetail.objects.get(id = id)
            influencer.countryCode = python_data.get('countryCode', influencer.countryCode)
            influencer.mobileNumber = python_data.get('mobileNumber', influencer.mobileNumber)
            influencer.name = python_data.get('name', influencer.name)
            influencer.commission = python_data.get('commission', influencer.commission)
            influencer.country = python_data.get('country', influencer.country)
            influencer.password = python_data.get('password', influencer.password)
            influencer.save()

            res={
                'message':"Influencer update successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'message':"This email is already linked to an existing account. Please use another one."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)
        

@csrf_exempt
def influencer_status_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        id = python_data.get('id')
        status = python_data.get('status')
      

        check_email = models.InfluencerDetail.objects.filter(id = id).count()
        if check_email == 1:
            influencer = models.InfluencerDetail.objects.get(id = id)
            influencer.status = python_data.get('status', influencer.status)
            influencer.save()
            res={
                'message':"Influencer status update successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':"Something went Wrong."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)

                     
@csrf_exempt
def influencer_detail(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        influencer = python_data.get('influencer')
        
        if models.InfluencerDetail.objects.filter(id = influencer).exists():
            influencer_data = models.InfluencerDetail.objects.get(id = influencer)
            serializer = InfluencerDetailSerializer(influencer_data).data
                
            res = {
                'data': serializer 
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res={
                'message':"Influencer Not Found."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)


@csrf_exempt
def all_influencer_list(request):
    all_influencer = models.InfluencerDetail.objects.all().order_by('-id')
    serializer = InfluencerDetailSerializer(all_influencer, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def promocode_create(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        influencer = python_data.get('influencer')
        promocode = python_data.get('promocode')
        no_of_promocode = python_data.get('no_of_promocode')
        expiry_date = python_data.get('expiry_date')
        discount = python_data.get('discount')

        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        check_promocode = models.PromocodeDetail.objects.filter(promocode = promocode).count()
        if check_promocode == 0:
            promocode_create = models.PromocodeDetail.objects.create(
                influencer_id = influencer,
                promocode = promocode,
                no_of_promocode = no_of_promocode,
                remaining_promocode = no_of_promocode,
                expiry_date = expiry_date,
                discount = discount,
                status = 'Active',
                created_at = datetime.now()
            ).save()

            res={
                'message':"Promocode Create successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':"Promocode with this name already exists."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)

                        
@csrf_exempt
def all_promocode_list(request):
    all_promocode = models.PromocodeDetail.objects.all().order_by('-id')
    serializer = PromocodeDetailSerializer(all_promocode, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)

                        
@csrf_exempt
def promocode_list(request):
    all_promocode = models.PromocodeDetail.objects.filter(status = "Active").order_by('-id')
    serializer = PromocodeDetailSerializer(all_promocode, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def promocode_list_influencer(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))
    influencer = python_data.get('influencer')
    all_promocode = models.PromocodeDetail.objects.filter(influencer = influencer).order_by('-id')
    serializer = PromocodeDetailSerializer(all_promocode, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)



@csrf_exempt
def promocode_status_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        id = python_data.get('id')
        status = python_data.get('status')
      

        check_email = models.PromocodeDetail.objects.filter(id = id).count()
        if check_email == 1:
            promocode = models.PromocodeDetail.objects.get(id = id)
            promocode.status = python_data.get('status', promocode.status)
            promocode.save()
            res={
                'message':"promocode status update successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':"Something went Wrong."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
