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
from diabaApp.serializer import DailyPriceSerializer



@csrf_exempt
def file_update_test(request):
    if request.method == "POST":
        
        get_all_product = models.ProductDetail.objects.all().order_by('id')
        # get_all_product = models.ProductDetail.objects.filter(id = 260)
        for product in get_all_product:
            # print(product.product_image_1, 'product')
            for num in range(1, 9):
                field_name = f'product_image_{num}'

                
                image = getattr(product, field_name)
                print(field_name, 'fasfasf', image , 'product_image',product.id )

                # print(image, 'image')
                if image != None and image != 'null' and image != '':
                    # print('Test_data')
                    try:
                        img = Image.open(image)
                        if img.format == "AVIF":    
                            # print(img.format, 'Test data 1')    
                            if img.mode in ("RGBA", "LA"):
                                img = img.convert("RGB")

                            buffer = BytesIO()
                            img.save(buffer, format="JPEG", quality=90)
                            buffer.seek(0)

                            base_name, ext = os.path.splitext(image.name)
                            base_name = base_name.split("/")[-1]
                            jpg_name = base_name + ".jpg"
                            content = ContentFile(buffer.read(), name=jpg_name)
                            # print(content, 'field_name', field_name, 'base_nae', base_name )

                            save_data = models.ProductDetail.objects.get(id=product.id)

                            setattr(save_data, field_name, content)  # dynamic assignment
                            save_data.save()
                    except:
                        pass 
                
        res = {
                'message':'File save '
            }
        return HttpResponse(res, content_type= 'application/json', status=200)



@csrf_exempt
def model_file_update_test(request):
    if request.method == "POST":
        
        get_all_product = models.ProductModel.objects.all().order_by('-id')
        for product in get_all_product:
            image = product.model_image
            field_name = 'model_image'
            
            # print(image, 'image')
            if image != None and image != 'null' and image != '':
                try:
                    img = Image.open(image)
                    if img.format == "AVIF":        
                        if img.mode in ("RGBA", "LA"):
                            img = img.convert("RGB")

                        buffer = BytesIO()
                        img.save(buffer, format="JPEG", quality=90)
                        buffer.seek(0)

                        base_name, ext = os.path.splitext(image.name)
                        base_name = base_name.split("/")[-1]
                        jpg_name = base_name + ".jpg"
                        content = ContentFile(buffer.read(), name=jpg_name)
                        print(content, 'field_name', field_name, 'base_nae', base_name )

                        save_data = models.ProductModel.objects.get(id=product.id)

                        setattr(save_data, field_name, content)  # dynamic assignment
                        save_data.save()
                except:
                    pass
        res = {
                'message':'File save '
            }
        return HttpResponse(res, content_type= 'application/json', status=200)

@csrf_exempt
def variant_file_update_test(request):
    if request.method == "POST":
        count = 0
        get_all_product = models.ProductModelVariant.objects.all().order_by('id')
        for product in get_all_product:
            image = product.image
            field_name = 'image'
            
            # print(image, 'image')
            if image != None and image != 'null' and image != '':
                try:
                    img = Image.open(image)
                    if img.format == "AVIF":        
                        if img.mode in ("RGBA", "LA"):
                            img = img.convert("RGB")

                        buffer = BytesIO()
                        img.save(buffer, format="JPEG", quality=90)
                        buffer.seek(0)

                        base_name, ext = os.path.splitext(image.name)
                        base_name = base_name.split("/")[-1]
                        jpg_name = base_name + ".jpg"
                        content = ContentFile(buffer.read(), name=jpg_name)
                        print(content, 'field_name', field_name, 'base_nae', base_name )

                        save_data = models.ProductModelVariant.objects.get(id=product.id)

                        setattr(save_data, field_name, content)  # dynamic assignment
                        save_data.save()
                        count += 1
                        print(count, 'count')
                except:
                    pass
        res = {
                'message':'File save',
                'count':count
            }
        print(res)
        return HttpResponse(res, content_type= 'application/json', status=200)

@csrf_exempt
def product_value_update_test(request):
    
    all_product = models.ProductDetail.objects.all()
    list_data = []
    for product in all_product:
        product = models.ProductDetail.objects.get(id = product.id)
        carton_length = product.carton_length
        if carton_length == '-':       
            product.carton_length = 0 
            product.carton_width = 0 
            product.carton_height = 0 
            product.carton_weight = 0 
            product.save()
            
            data = {'carton_weight':product.carton_weight,'product':product.id } 
            list_data.append(data)
    
    res = {
        'data': list_data
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)
    