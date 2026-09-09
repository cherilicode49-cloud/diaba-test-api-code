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
from diabaApp.serializer import ProductRequestSerializer



@csrf_exempt
def product_request_create(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
    
    for i,j in request.POST.items():
        python_data.update({i:j})

    print(python_data, "python_data")
    vendor = python_data.get('vendor')
    product_name = python_data.get('product_name')
    category = python_data.get('category')
    subcategory = python_data.get('subcategory')
    category_description = python_data.get('category_description')
    description = python_data.get('description')
    product_image_1 = python_data.get('product_image_1')
    product_image_2 = python_data.get('product_image_2')
    
    product = models.ProductRequest.objects.create(
        vendor_id = vendor,
        product_name = product_name,
        category = category,
        subcategory = subcategory,
        category_description = category_description,
        description = description,
        product_image_1 = product_image_1,
        product_image_2 = product_image_2,
        status = 'pending'
    ).save()

    res = {
        'message':'Product Request Submite successfully.'        
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)



@csrf_exempt
def vendor_product_request_list(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)
    vendor = python_data.get('vendor')

    product_list = models.ProductRequest.objects.filter(vendor =vendor)
    serializer = ProductRequestSerializer(product_list, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def all_product_request_list(request):
    
    product_list = models.ProductRequest.objects.all()
    serializer = ProductRequestSerializer(product_list, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def product_request_status_update(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)
    product = python_data.get('product')

    request_form = models.ProductRequest.objects.get(id = product)
    request_form.status = python_data.get('status', request_form.status)
    request_form.save()

    res = {
        'message':'Product Request status update successfully.'        
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)
