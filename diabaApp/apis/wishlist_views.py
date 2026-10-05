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
from diabaApp.utils import track_user_activity



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
                prod_obj = models.ProductDetail.objects.filter(id=product).first()
                product_name = prod_obj.product_name if prod_obj else None

                check_wishlist = models.WishlistDetail.objects.filter(customer= customer,product=product).count()
                if check_wishlist == 0:
                    create = models.WishlistDetail.objects.create(
                        customer_id= customer,
                        product_id=product,
                        created_at = date_time
                    ).save()
                    
                    track_user_activity(
                        action_type='PRODUCT_WISHLIST',
                        customer_id=customer,
                        product_id=product,
                        product_name=product_name,
                        metadata={'action': 'added_to_wishlist'},
                        ip_address=request.META.get('REMOTE_ADDR')
                    )

                    res={
                        'message':"Product successfully added to your wishlist."
                    }
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

                if check_wishlist == 1:
                    delete_data = models.WishlistDetail.objects.get(customer_id= customer,product_id=product)
                    delete_data.delete()

                    track_user_activity(
                        action_type='PRODUCT_WISHLIST',
                        customer_id=customer,
                        product_id=product,
                        product_name=product_name,
                        metadata={'action': 'removed_from_wishlist'},
                        ip_address=request.META.get('REMOTE_ADDR')
                    )

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
                    prod_obj = models.ProductDetail.objects.filter(id=product).first()
                    product_name = prod_obj.product_name if prod_obj else None

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
                        
                        track_user_activity(
                            action_type='ADD_TO_CART',
                            customer_id=customer,
                            product_id=product,
                            product_name=product_name,
                            metadata={'variant_id': variant, 'quantity': quantity, 'shipping_via': shipping_via},
                            ip_address=request.META.get('REMOTE_ADDR')
                        )

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
                        
                        track_user_activity(
                            action_type='ADD_TO_CART',
                            customer_id=customer,
                            product_id=product,
                            product_name=product_name,
                            metadata={'variant_id': variant, 'quantity': add_variant, 'shipping_via': shipping_via, 'action': 'update_qty'},
                            ip_address=request.META.get('REMOTE_ADDR')
                        )

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
            customer_id = cart_data.customer_id
            product_id = cart_data.product_id
            product_name = cart_data.product.product_name if cart_data.product else None

            track_user_activity(
                action_type='REMOVE_FROM_CART',
                customer_id=customer_id,
                product_id=product_id,
                product_name=product_name,
                metadata={'cart_id': cart, 'quantity': cart_data.quantity},
                ip_address=request.META.get('REMOTE_ADDR')
            )

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

