from django.views.decorators.csrf import csrf_exempt
from diabaApp import models
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
import io
import math, random , calendar
from datetime import datetime, timedelta
from django.template.loader import get_template
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, Count, F, Q
import json
from django.http import JsonResponse
from django.db.models import Max, Min
from django.db.models.functions import Cast, TruncMonth, Coalesce, ExtractMonth, Round, TruncDate
from django.utils import timezone
import numpy as np

import  requests
from diabaApp.serializer import CustomerDetailSerializer, CustomerAddressDetailSerializer, OrderDetailDataSerializer, \
    ProductOrderDetailSerializer, CartDetailSerializer, WishlistDetailSerializer


@csrf_exempt
def customer_profile_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        customer = python_data.get('customer')
        
        check_customer = models.CustomerDetail.objects.filter(id = customer).count()
        if check_customer == 1:
            customer_detail = models.CustomerDetail.objects.get(id = customer)
            customer_detail.email = python_data.get('email', customer_detail.email)
            customer_detail.mobileNumber = python_data.get('mobileNumber', customer_detail.mobileNumber)
            customer_detail.name = python_data.get('name', customer_detail.name)
            customer_detail.gender = python_data.get('gender', customer_detail.gender)
            customer_detail.save()

            serializer = CustomerDetailSerializer(customer_detail).data

            res = {
                'message':" Details update successfully.",
                'data':serializer
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res = {
                'message':"Customer id not found."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)


@csrf_exempt
def customer_address_create(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        customer = python_data.get('customer')
        recipient_name = python_data.get('recipient_name')
        street_address = python_data.get('street_address')
        city = python_data.get('city')
        region = python_data.get('region')
        postal_code = python_data.get('postal_code')
        country = python_data.get('country')
        address_type = python_data.get('address_type')
        mobile_number = python_data.get('mobile_number')
        
        # print(python_data, 'python_data')
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        check_customer = models.CustomerDetail.objects.filter(id = customer).count()
        
        if check_customer == 1:
            check_total_address = models.CustomerAddressDetail.objects.filter(customer_id = customer).count()
            if check_total_address == 0:
                is_default = 'True'
            else:
                is_default = python_data.get('is_default', 'False')

            address = models.CustomerAddressDetail.objects.create(
                customer_id = customer,
                recipient_name = recipient_name,
                street_address = street_address,
                city = city,
                region = region,
                postal_code = postal_code,
                country = country,
                address_type = address_type,
                mobile_number = mobile_number,
                is_default = is_default, 
                created_at = date_time
            ).save()

            
            customer_number = models.CustomerDetail.objects.get(id = customer)
            if customer_number.mobileNumber == None:
                # print('True Data', mobile_number)
                number_update = models.CustomerDetail.objects.get(id = customer)
                number_update.mobileNumber = mobile_number
                number_update.save()

            res={
                'message':"You have successfully added a new address."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        
        else:
            res = {
                'message':"Customer id not found."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)



@csrf_exempt
def customer_address_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        customer = python_data.get('customer')
        recipient_name = python_data.get('recipient_name')
        street_address = python_data.get('street_address')
        city = python_data.get('city')
        region = python_data.get('region')
        postal_code = python_data.get('postal_code')
        country = python_data.get('country')
        address_type = python_data.get('address_type')
        mobile_number = python_data.get('mobile_number')
        is_default = str(python_data.get('is_default'))
        # print(python_data, 'python_data')
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        check_customer = models.CustomerAddressDetail.objects.filter(id = id).count()
        if check_customer == 1:
            if is_default == 'True':
                get_all_address = models.CustomerAddressDetail.objects.filter(customer = customer)
                for address in get_all_address:
                    update_default = models.CustomerAddressDetail.objects.get(id = address.id)
                    update_default.is_default = 'False'
                    update_default.save()
            

            address = models.CustomerAddressDetail.objects.get(id = id)
            address.recipient_name = python_data.get('recipient_name', address.recipient_name)
            address.street_address = python_data.get('street_address', address.street_address)
            address.city = python_data.get('city', address.city)
            address.region = python_data.get('region', address.region)
            address.postal_code = python_data.get('postal_code', address.postal_code)
            address.country = python_data.get('country', address.country)
            address.address_type = python_data.get('address_type', address.address_type)
            address.mobile_number = python_data.get('mobile_number', address.mobile_number)
            address.is_default = python_data.get('is_default', address.is_default)
            address.save()

            res={
                'message':"You have successfully update a address."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        
        else:
            res = {
                'message':"Customer id not found."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)



@csrf_exempt
def customer_detail(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        customer = python_data.get('customer')
        
        check_customer = models.CustomerDetail.objects.filter(id = customer).count()
        if check_customer == 1:

            customer = models.CustomerDetail.objects.get(id = customer)
            serializer = CustomerDetailSerializer(customer).data
            
            all_address = models.CustomerAddressDetail.objects.filter(customer = customer)
            address_serializer = CustomerAddressDetailSerializer(all_address, many=True).data

            res = {
                'data':serializer,
                'address': address_serializer    
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res = {
                'message':"Customer id not found."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)


@csrf_exempt
def customer_detail_admin(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)
    id = python_data.get('id')
    check_customer = models.CustomerDetail.objects.filter(id = id).count()
    if check_customer == 1:

        customer = models.CustomerDetail.objects.get(id = id)
        serializer = CustomerDetailSerializer(customer).data
        
        all_address = models.CustomerAddressDetail.objects.filter(customer = id)
        address_serializer = CustomerAddressDetailSerializer(all_address, many=True).data

        list_order = []
        all_order_list = models.OrderDetail.objects.filter(customer = id)
        for order in all_order_list:
            order_get = models.OrderDetail.objects.get(id = order.id)
            order_data = OrderDetailDataSerializer(order_get).data

            product = models.ProductOrderDetail.objects.filter(order = order.id)
            product_data = ProductOrderDetailSerializer(product, many=True).data

            order_data.update({'product_data':product_data})
            list_order.append(order_data)

        get_cart = models.CartDetail.objects.filter(customer = id)
        cart_data = CartDetailSerializer(get_cart, many=True).data

        get_wishlist = models.WishlistDetail.objects.filter(customer = id)
        wishlist_data = WishlistDetailSerializer(get_wishlist, many=True).data


        res = {
            'data':serializer,
            'address': address_serializer,
            'order_data':list_order,
            'cart_data':cart_data,
            'wishlist_data':wishlist_data
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)

@csrf_exempt
def customer_list_admin(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        # print("python_data--all_product_list--->", python_data)

        today = timezone.now()

        page_number = int(python_data.get('page_number', 1))
        row_size = int(python_data.get('row_data', 10))
        last_row = row_size * page_number
        first_row = last_row - row_size
        
        search_key = python_data.get('search_key',None)
        country = python_data.get('country',None)

        filter_condition = Q()

        if country not in [None,'','null']:
            filter_condition &= Q(country = country)
        if search_key not in [None,'','null']:
            filter_condition &= Q(email__icontains = search_key)|Q(mobileNumber__icontains = search_key)|Q(name__icontains = search_key)

        total_records = models.CustomerDetail.objects.filter(filter_condition).count()
        all_customer = models.CustomerDetail.objects.filter(filter_condition).order_by('-id')[first_row:last_row]
        serializer = CustomerDetailSerializer(all_customer, many=True).data

        res = {
            'data':serializer,
            'total_records':total_records,
            'current_page':page_number,
            'total_pages': int(np.ceil(total_records/row_size))
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def customer_delete(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        # print(python_data ,'python_data')
        customer = python_data.get('user_id')

        login_data = models.CustomerLogin.objects.filter(customer= customer)
        login_data.delete()

        address_data = models.CustomerAddressDetail.objects.filter(customer= customer)
        address_data.delete()

        wishlist_data = models.WishlistDetail.objects.filter(customer= customer)
        wishlist_data.delete()

        cart_data = models.CartDetail.objects.filter(customer= customer)
        cart_data.delete()

        # order_data = models.OrderDetail.objects.filter(customer= customer)
        # for order in order_data:
        #     order = models.OrderDetail.objects.filter(id = order.id)
        #     tracking_data = models.OrderTracking.objects.filter(order = order.id)
        #     tracking_data.delete()
        #     order.delete()

        customer_data = models.CustomerDetail.objects.filter(id= customer)
        customer_data.delete()

        
        res={
            'message':"Your account has been deleted successfully."
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



@csrf_exempt
def customer_wishlist(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        customer = python_data.get('customer')
        wishlist = models.WishlistDetail.objects.filter(customer = customer).order_by('-id')
        wishlist_serializer = WishlistDetailSerializer(wishlist, many=True).data
    
        res={
            'data':wishlist_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


def calculate_shipping_cost(
        carton_length,
        carton_width,
        carton_height,
        carton_weight,
        quantity,
        price_by_air,
        price_by_ship,
        price_by_express
    ):

        # print("price_by_ship----->",price_by_ship)
        # Convert to float safely
        if carton_length != "-":
            L = float(carton_length or 0)
        else:
            L = 0 
        
        if carton_width != "-":
            W = float(carton_width or 0)
        else:
            W = 0 
        
        if carton_height != "-":
            H = float(carton_height or 0)
        else:
            H = 0 

        if carton_weight != "-":
            weight = float(carton_weight or 0)
        else:
            weight = 0 

        # weight = float(carton_weight or 0)
        qty = int(quantity or 0)

        #CBM per unit
        # print("L", L , "W", W, "H", H)
        cbm_per_unit = (L*W*H) / 1000000  # cm → m conversion

        # print("L=-=------>",L)
        # print("W=-=------>",W)
        # print("H=-=------>",H)
        #  Totals
        total_cbm = cbm_per_unit * qty
        # print(total_cbm, 'total_cbm')
        total_weight = weight * qty

        # print("total_cbm=-=------>",cbm_per_unit, qty )

        #Chargeable weights
        chargeable_air_weight = total_weight      # Billed per KG
        chargeable_express_weight = total_weight      # Billed per KG
        chargeable_sea_weight = total_cbm         # Billed per CBM

        # print("chargeable_sea_weight----->",chargeable_air_weight)

        #Final shipping costs
        # print(chargeable_sea_weight, 'chargeable_sea_weightchargeable_sea_weightchargeable_sea_weight')
        # print("total_cbm====>",total_cbm)
        # print("chargeable_air_weight====>",chargeable_air_weight)
        # print("chargeable_sea_weight====>",chargeable_sea_weight)

        # print("chargeable_air_weight * float(price_by_air or 0)====>",chargeable_air_weight * float(price_by_air or 0))
        # print("chargeable_sea_weight * float(price_by_ship or 0====>",chargeable_sea_weight * float(price_by_ship or 0))
        # print("chargeable_express_weight * float(price_by_express or 0====>",chargeable_express_weight * float(price_by_express or 0))

        total_air_cost = round(chargeable_air_weight * float(price_by_air or 0))
        total_sea_cost = round(chargeable_sea_weight * float(price_by_ship or 0),4)
        total_express_cost = round(chargeable_express_weight * float(price_by_express or 0),4)


        # print("total_sea_cost------->",total_air_cost)

        return {
            "cbm": math.ceil(round(total_cbm, 6)),
            "chargeable_air_weight": round(chargeable_air_weight),
            "chargeable_sea_weight": round(chargeable_sea_weight, 6),
            "total_air_cost": total_air_cost,
            "total_sea_cost": total_sea_cost,
            "total_express_cost":total_express_cost
        }


@csrf_exempt
def customer_wishlist_cart_list(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data=-=-customer_wishlist_cart_list--->",python_data)
        customer = python_data.get('customer')
        flag = python_data.get('flag')
        check_customer = models.CustomerDetail.objects.filter(id =customer).count()

        currencyCode = python_data.get('currencyCode',None)
        country = python_data.get('country','Egypt')
        ip_address = python_data.get('ip_address')
        promocode = python_data.get('promocode')

        try:
            if currencyCode not in [None,'','null']:
                country = models.CountryWithCurrency.objects.filter(currency_code = currencyCode).first().country_name
                # print("country--->",country)

            elif customer:
                user = models.CustomerDetail.objects.get(id = customer)
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
            

        if check_customer == 1:
            user = models.CustomerDetail.objects.get(id = customer)
            
            if flag == 'wishlist':
                wishlist_data = models.WishlistDetail.objects.filter(customer= customer)
                wishlist_serializer = WishlistDetailSerializer(wishlist_data, many=True).data

                res={
                    'data':wishlist_serializer
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
            
            elif flag == 'cart':
                
                cart_data = models.CartDetail.objects.filter(customer= customer,  product__status = 'Active')
                # cart_serializer = CartDetailSerializer(cart_data, many=True).data
                cart_data_list = []

                if not models.CountryWithCurrency.objects.filter(Q(country_calling_code = user.countryCode) | Q(country_name = user.country)).exists():
                    country = "Egypt"
                    for product in cart_data:
                        price_by_air = 0
                        price_by_ship = 0

                        # print("herere0-0-00-302-30--->",product)
                        per_product_cart_serializer = CartDetailSerializer(product,context = {'country':country}).data
                        quantity=product.quantity
                        product_total = float(quantity) * float(per_product_cart_serializer.get('price'))
                        per_product_cart_serializer['product_total'] = int(round(float(product_total)))
                        
                        cart_data_list.append(per_product_cart_serializer)

                    res={
                        'data':cart_data_list,
                        # 'data':cart_serializer,
                        # 'daily_price':daily_price,
                        # 'product_total':product_total,
                        # 'price_by_air':price_by_air,
                        # 'price_by_ship':price_by_ship
                        'message_en':'Cannot Place Order Outside Africa Continent',
                        'message_fr':'Impossible de passer commande en dehors du continent africain.'
                    }                    
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
                
                # print(user.countryCode, 'user.countryCode', user.country)
                # price_by = models.CountryWithCurrency.objects.filter(Q(country_calling_code = user.countryCode) | Q(country_name = user.country))
                price_by = models.CountryWithCurrency.objects.get(country_name = user.country)
                # print(price_by)
                price_by_air_rate = price_by.price_by_air
                price_by_ship_rate = price_by.price_by_ship
                price_by_express_shipping = price_by.express_shipping
                

                total_price = 0.0
                cart_data_list = []
                list_air = []
                list_ship = []
                list_express = []
                list_product_amount = []
                # count = 0
                for product in cart_data:
                    price_by_air = 0
                    price_by_ship = 0
                    price_by_express = 0

                    # print("herere0-0-00-302-30--->",product)

                    product = models.CartDetail.objects.get(id = product.id)

                    per_product_cart_serializer = CartDetailSerializer(product,context = {'country':country}).data

                    # print("per_product_cart_serializer-=-=---->",per_product_cart_serializer)
                    total_price += float(product.variant.price)
                    # print(product.shipping_via, 'product.shipping_via')
                    if product.shipping_via == "By Air":
                        
                        # print(currencyCode, 'price_by')

                        if currencyCode not in [None,'','null']:
                            if price_by.currency_code != "USD":
                                non_usd_rate = models.CurrencyConverter.objects.get(currency_code = price_by.currency_code).system_rate
                                usd_price_by_air = float(price_by_air_rate) / float(non_usd_rate)

                                if currencyCode != "USD":
                                    user_country_currency_rate = models.CurrencyConverter.objects.get(currency_code = price_by.currency_code).system_rate
                                    price_by_air = float(usd_price_by_air) * float(user_country_currency_rate)

                                else:
                                    price_by_air = usd_price_by_air
                                    
                            else:
                                if currencyCode != "USD":
                                    selected_currency_rate = models.CurrencyConverter.objects.get(currency_code = currencyCode).system_rate

                                    price_by_air = float(price_by_air_rate) * float(selected_currency_rate)

                                else:
                                    price_by_air = price_by_air_rate
                                    # print(price_by_air, 'price_by_air')

                        else:
                            price_by_air = price_by_air_rate
                            # print(price_by_air, 'price_by_air tyu' )

                        
                        # print(price_by_air,'price_by_air_rate')
                        per_product_cart_serializer['price_by_air']= round(float(price_by_air),2)
                        # list_air.append(price_by_air)


                    if product.shipping_via == "By Ship":
                        # print("user.countryCode---->",user.countryCode)
                        # print("user.country---->",user.country)
                        price_by = models.CountryWithCurrency.objects.get(country_name = user.country)
                        price_by_ship_rate = price_by.price_by_ship
                        # print(user.countryCode, user.country, 'price_by')
                        
                        if currencyCode not in [None,'','null']:
                            if price_by.currency_code != "USD":
                                non_usd_rate = models.CurrencyConverter.objects.get(currency_code = price_by.currency_code).system_rate
                                usd_price_by_ship = float(price_by_ship_rate) / float(non_usd_rate)
                                # print(price_by_ship_rate,"----usd_price_by_ship--->",usd_price_by_ship)

                                if currencyCode != "USD":
                                    user_country_currency_rate = models.CurrencyConverter.objects.get(currency_code = price_by.currency_code).system_rate
                                    price_by_ship = float(usd_price_by_ship) * float(user_country_currency_rate)
                                    # print("DATA from here---->1")

                                else:
                                    price_by_ship = usd_price_by_ship
                                    # print("DATA from here---->2")
                                    
                            else:
                                if currencyCode != "USD":
                                    selected_currency_rate = models.CurrencyConverter.objects.get(currency_code = currencyCode).system_rate

                                    price_by_ship = float(price_by_ship_rate) * float(selected_currency_rate)
                                    # print("DATA from here---->3")

                                else:
                                    price_by_ship = price_by_ship_rate
                                    # print("DATA from here---->4")

                        else:
                            price_by_ship = price_by_ship_rate
                            # print("DATA from here---->5")

                        # print(price_by_ship, 'price_by_ship_rateprice_by_ship_rateprice_by_ship_rate')
                        per_product_cart_serializer['price_by_ship'] = round(float(price_by_ship),2)
                        # list_ship.append(price_by_ship)
                    if product.shipping_via == "By Express":
                        
                        # print(currencyCode, 'price_by')

                        if currencyCode not in [None,'','null']:
                            if price_by.currency_code != "USD":
                                non_usd_rate = models.CurrencyConverter.objects.get(currency_code = price_by.currency_code).system_rate
                                usd_price_by_express = float(price_by_express_shipping) / float(non_usd_rate)

                                if currencyCode != "USD":
                                    user_country_currency_rate = models.CurrencyConverter.objects.get(currency_code = price_by.currency_code).system_rate
                                    price_by_express = float(usd_price_by_express) * float(user_country_currency_rate)

                                else:
                                    price_by_express = usd_price_by_express
                                    
                            else:
                                if currencyCode != "USD":
                                    selected_currency_rate = models.CurrencyConverter.objects.get(currency_code = currencyCode).system_rate

                                    price_by_express = float(price_by_express_shipping) * float(selected_currency_rate)

                                else:
                                    price_by_express = price_by_express_shipping
                                    # print(price_by_air, 'price_by_air')

                        else:
                            price_by_express = price_by_express_shipping
                            # print(price_by_air, 'price_by_air tyu' )

                        
                        # print(price_by_air,'price_by_air_rate')
                        per_product_cart_serializer['price_by_express']= round(float(price_by_express),2)
                    # print(price_by_express, 'price_by_expresspricvv afaf  product', product.product.carton_length, 'carton')
                    carton_length=product.product.carton_length
                    carton_width=product.product.carton_width
                    carton_height=product.product.carton_height
                    carton_weight=product.product.carton_weight
                    quantity=product.quantity
                    # print(carton_length, 'carton_length', carton_width,'carton_width',  carton_height, 'carton_height', carton_weight,'carton_weight',  quantity, 'quantity' )
                    # print("carton_length----->",carton_length)
                    # print("carton_width----->",carton_width)
                    # print("carton_height----->",carton_height)
                    # print("carton_weight----->",carton_weight)
                    # print("quantity----->",quantity)
                    # print("price_by_air----->",price_by_air)
                    # print("price_by_ship----->",price_by_ship)
                    shipping_cost_per_product = calculate_shipping_cost(carton_length,carton_width,carton_height,carton_weight,quantity,price_by_air,price_by_ship, price_by_express)
                    # print(shipping_cost_per_product, 'shipping_cost_per_product')
                    list_air.append(shipping_cost_per_product.get('total_air_cost'))
                    list_ship.append(shipping_cost_per_product.get('total_sea_cost'))
                    list_express.append(shipping_cost_per_product.get('total_express_cost'))
                    
                    product_total = float(quantity) * float(per_product_cart_serializer.get('price'))
                    list_product_amount.append(product_total)
                    
                    per_product_cart_serializer['shipping_cost_per_product'] = shipping_cost_per_product
                    per_product_cart_serializer['product_total'] = int(round(float(product_total)))

                    cart_data_list.append(per_product_cart_serializer)
                
                total_price = math.ceil(sum(list_product_amount))
                total_air = math.ceil(sum(list_air))
                total_ship = math.ceil(sum(list_ship))
                total_express = math.ceil(sum(list_express))

                # print(total_price, total_air, total_ship)
                if promocode:
                    check_promocode = models.PromocodeDetail.objects.filter(promocode = promocode).count()
                    if check_promocode == 1:
                        get_promocode = models.PromocodeDetail.objects.get(promocode = promocode)
                        discount = get_promocode.discount
                        # print(discount, 'discount')
                        discount_price = round(int(total_price) * int(discount)/100)
                        # print(total_price, 'total_price')
                        price_after_discount = math.ceil(total_price - discount_price)


                        amount_to_paid = math.ceil(price_after_discount + total_air + total_ship + total_express)
                        amount_to_paid_with_tax = math.ceil(amount_to_paid * 1.015)
                        # print(amount_to_paid_with_tax, 'amount_to_paid_with_tax')
                        
                        res={
                            'data':cart_data_list,
                            'total_price' :f"{total_price:,}".replace(",", " "),
                            'discount_price':f"{discount_price:,}".replace(",", " "), 
                            'discount_percentage': discount, 
                            'price_after_discount': f"{price_after_discount:,}".replace(",", " "),
                            'total_air' :  f"{total_air:,}".replace(",", " "),
                            'total_ship' :  f"{total_ship:,}".replace(",", " "),
                            'total_express' :  f"{total_express:,}".replace(",", " "),
                            'amount_to_paid_view': f"{amount_to_paid:,}".replace(",", " "),
                            'amount_to_paid_with_tax_view': f"{amount_to_paid_with_tax:,}".replace(",", " "),
                            'amount_to_paid': amount_to_paid,
                            'amount_to_paid_with_tax': amount_to_paid_with_tax,
                            'coupon_verify':True
                            }
                    else:
                        res={
                            'message':'Enter valid coupon.'
                        }
                        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
                else:
                    amount_to_paid = math.ceil(total_price + total_air + total_ship + total_express)
                    amount_to_paid_with_tax = math.ceil(amount_to_paid * 1.015)
                    # print(amount_to_paid_with_tax, 'amount_to_paid_with_tax')
                    
                    res={
                        'data':cart_data_list,
                        'total_price' :  f"{total_price:,}".replace(",", " "),
                        'total_air' :  f"{total_air:,}".replace(",", " "),
                        'total_ship' :  f"{total_ship:,}".replace(",", " "),
                        'total_express': f"{total_express:,}".replace(",", " "),
                        'amount_to_paid_view': f"{amount_to_paid:,}".replace(",", " "),
                        'amount_to_paid_with_tax_view': f"{amount_to_paid_with_tax:,}".replace(",", " "),
                        'amount_to_paid_with_tax': amount_to_paid_with_tax,
                        'amount_to_paid': amount_to_paid,
                        'coupon_verify':False

                        }
                
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
            
            else:
                res={
                    'message':'Something Went wrong.'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
        else:
            res={
                'message':'User not Found.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)


@csrf_exempt
def customer_cart_check(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        customer  = python_data.get('customer')
        
        all_product_data = list(set(models.CartDetail.objects.filter(customer= customer).values_list('product', flat=True)))
        reason_data = []
        for product in all_product_data:
            if product != None:
                get_minimun_qnt = int(models.ProductDetail.objects.filter(id = product).values_list('min_order_quantity', flat=True)[0])
                product_name = models.ProductDetail.objects.filter(id = product).values_list('product_name', flat=True)[0]
                # print(get_minimun_qnt,product, 'get_minimun_qnt')

                quantity_get = list(models.CartDetail.objects.filter(customer= customer, product = product).values_list('quantity', flat=True))
                total_quantity = sum(list(map(int, quantity_get)))
            

                if get_minimun_qnt > total_quantity:
                    add_quantity = get_minimun_qnt - total_quantity
                    # print(add_quantity, product)
                    product_name = product_name[:15] + '...' if len(product_name) > 15 else product_name


                    reason_data.append(product_name)

        if reason_data != []:
            final_reason = ', '.join(map(str, reason_data)) 
            message = f'You need to add more quantity of “{final_reason}” products to your cart before proceeding to payment.'
            status = 406
            res={
                'message':message,
                'flag':False
            }
        else:
            status=200
            res={
                'flag':True
            }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=status)



@csrf_exempt
def mobile_number_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        print("python_data--mobile_number_update-->",python_data)

        customer = python_data.get('customer',None)
        countryCode = python_data.get('countryCode',None)
        mobileNumber = python_data.get('mobileNumber',None)
        country = python_data.get('country',None)
        

        if customer in [None,'','null']:
            res = {
                'message':'Customer Not Found'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        else:
            if models.CustomerDetail.objects.filter(id = customer).exists():
                get_user = models.CustomerDetail.objects.get(id = customer)

                digits = '123456789' 
                OTP = ""
                for i in range(4):
                    OTP += digits[math.floor(random.random() * 9)]

                get_user.OTP = OTP
                get_user.country = country
                get_user.save()
                
                recipient = str(countryCode) + str(mobileNumber)
                # content = f'Your Diaba verification code is {OTP}. It will expire in 5 minutes. Do not share this code with anyone.'
                # result = send_sms(LOGIN, API_KEY, TOKEN, SUBJECT, SIGNATURE, recipient, content)
                
                url = "https://api.verifyway.com/api/v1/"
                headers = {
                    "Authorization": "Bearer 1515$iwLeuAjYrEcHnD8Rs2GymuXAefPF8M5fx7wV",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
                payload = {
                    "recipient": recipient,
                    "type": "otp",
                    "channel": "whatsapp",
                    "fallback": "no",
                    "code": OTP,
                    "lang": "en",
                }
                response = requests.post(url, json=payload, headers=headers)
                # print(response, 'responseresponse')

                res={
                    'message':"Verification code sent successfully.", 
                    'OTP':OTP
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
            
            else:
                res = {
                    'message':'Customer Not Found'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def mobile_number_update_verify(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        # print("python_data--mobile_number_update-->",python_data)

        customer = python_data.get('customer',None)
        countryCode = python_data.get('countryCode',None)
        mobileNumber = python_data.get('mobileNumber',None)
        name = python_data.get('name',None)

        OTP = python_data.get('OTP',None)

        if customer in [None,'','null']:
            res = {
                'message':'Customer Not Found'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        else:
            if models.CustomerDetail.objects.filter(id = customer).exists():
                get_user = models.CustomerDetail.objects.get(id = customer)

                if get_user.OTP == OTP:
                    get_user.countryCode = countryCode
                    get_user.mobileNumber = mobileNumber
                    get_user.name = name

                    get_user.save()
                    serializer = CustomerDetailSerializer(get_user).data
                    res={
                        'message':"Verification completed successfully.", 
                        'data':serializer
                    }
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
                else:
                    res={
                        'message':"OTP not Matched", 
                    }
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
            else:
                res = {
                    'message':'Customer Not Found'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def country_list_customer_filter(request):
    if request.method == "POST":
        country_list = list(
            models.CustomerDetail.objects
            .values_list('country', flat=True)
            .exclude(country__isnull=True)
            .exclude(country__exact="")
            .distinct()
            .order_by('country')
        )
        res={
            'data':country_list
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)