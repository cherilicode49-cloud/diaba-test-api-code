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
def add_to_wishlist(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        customer = python_data.get('customer')
        product = python_data.get('product')

        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        check_customer = models.CustomerDetail.objects.filter(id =customer).count()
        if check_customer == 1:
            check_product = models.ProductDetail.objects.filter(id = product).count()
            if check_product == 1:
                check_wishlist = models.WishlistDetail.objects.filter(customer= customer,product=product).count()
                if check_wishlist == 0:
                    create = models.WishlistDetail.objects.create(
                        customer_id= customer,
                        product_id=product,
                        created_at = date_time
                    ).save()
                    
                    res={
                        'message':"Product successfully added to your wishlist."
                    }
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

                if check_wishlist == 1:
                    delete_data = models.WishlistDetail.objects.get(customer_id= customer,product_id=product)
                    delete_data.delete()

                    res={
                        'message':"Product removed from your wishlist."
                    }
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

                else:
                    res={
                        'message':"Something Went Wrong."
                    }
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
            else:
                res={
                    'message':"Please Enter Valid Product."
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
        else:
            res={
                'message':"Please Enter Valid Customer."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)


@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))


        all_cart = python_data.get('cart')

        for cart in all_cart:
            customer = cart.get('customer')
            product = cart.get('product')
            variant = cart.get('variant')
            quantity = cart.get('quantity')
            shipping_via = cart.get('shipping_via')

            # print(python_data, 'python_data')
            now = datetime.now()
            date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

            check_customer = models.CustomerDetail.objects.filter(id =customer).count()
            if check_customer == 1:
                check_product = models.ProductDetail.objects.filter(id = product).count()
                if check_product == 1:
                    check_cart = models.CartDetail.objects.filter(customer= customer,product=product, variant = variant).count()
                    # print(check_cart, 'check_cartcheck_cart')
                    if check_cart == 0:
                        create = models.CartDetail.objects.create(
                            customer_id= customer,
                            product_id=product,
                            variant_id =variant,
                            quantity = quantity,
                            shipping_via = shipping_via,
                            created_at = date_time
                        ).save()
                        
                        res={
                            'message':"Product successfully added to your cart."
                        }
                        # return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

                    if check_cart == 1:
                        cart_id = models.CartDetail.objects.filter(customer= customer,product=product, variant = variant).values_list('id', flat=True)[0]
                        variant_quantity = models.CartDetail.objects.filter(id = cart_id).values_list('quantity', flat=True)[0]
                        # print(variant_quantity, 'variant_quantity')
                        add_variant = int(variant_quantity) + quantity

                        cart_update = models.CartDetail.objects.get(id = cart_id)
                        cart_update.quantity = add_variant
                        cart_update.save()
                        
                        res={
                            'message':"Product successfully added to your cart."
                        }
                        # return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

@csrf_exempt
def product_remove_from_cart(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        cart = python_data.get('cart')
        
        check_cart = models.CartDetail.objects.filter(id= cart).count()
        if check_cart == 1:
            cart_data = models.CartDetail.objects.get(id = cart)
            cart_data.delete()

            res={
                'message':"Product Remove From Cart."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':"Someting went wrong."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
