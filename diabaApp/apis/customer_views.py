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
from diabaApp.utils import track_user_activity


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
        customer = python_data.get('user_id') or python_data.get('customer')

        check_customer = models.CustomerDetail.objects.filter(id=customer)
        if check_customer.exists():
            cust_obj = check_customer.first()
            cust_obj.is_deleted = True
            cust_obj.status = 'Inactive'
            cust_obj.deleted_at = datetime.now()
            cust_obj.save()

            # Clear temporary session data & cart
            models.CustomerLogin.objects.filter(customer=customer).delete()
            models.CartDetail.objects.filter(customer=customer).delete()

            res = {
                'status': True,
                'message': "Your account has been deleted successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'status': False,
                'message': "Customer not found."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=404)




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
        price_by_express,
        is_usd=None
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

        total_air_cost = round(chargeable_air_weight * float(price_by_air or 0), 2)
        total_sea_cost = round(chargeable_sea_weight * float(price_by_ship or 0), 2)
        total_express_cost = round(chargeable_express_weight * float(price_by_express or 0), 2)

        if is_usd is None:
            is_usd = (price_by_air and float(price_by_air) < 500) or (price_by_ship and float(price_by_ship) < 500) or (price_by_express and float(price_by_express) < 500)
        fmt_air = f"{total_air_cost:,.2f}".replace(',', ' ') if is_usd else f"{round(total_air_cost):,}".replace(',', ' ')
        fmt_sea = f"{total_sea_cost:,.2f}".replace(',', ' ') if is_usd else f"{round(total_sea_cost):,}".replace(',', ' ')
        fmt_exp = f"{total_express_cost:,.2f}".replace(',', ' ') if is_usd else f"{round(total_express_cost):,}".replace(',', ' ')
        return {
            "cbm": round(total_cbm, 6),
            "chargeable_air_weight": round(chargeable_air_weight, 2),
            "chargeable_sea_weight": round(chargeable_sea_weight, 6),
            "total_air_cost": total_air_cost if is_usd else round(total_air_cost),
            "total_sea_cost": total_sea_cost if is_usd else round(total_sea_cost),
            "total_express_cost": total_express_cost if is_usd else round(total_express_cost),
            "total_air_cost_view": fmt_air,
            "total_sea_cost_view": fmt_sea,
            "total_express_cost_view": fmt_exp,
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
            

        # Determine early if this is a USD cart (used throughout)
        if currencyCode in ['XOF', 'XAF', 'CDF', 'GNF']:
            is_usd_cart = False
        elif currencyCode == 'USD':
            is_usd_cart = True
        else:
            is_usd_cart = (country in ['Egypt', 'Libya', 'Liberia', 'Lesotho', 'Zambia', 'Kenya', 'Zimbabwe', 'Ghana', 'Uganda', 'The Gambia', 'Tunisia', 'Ethiopia', 'Tanzania', 'Swaziland', 'Eritrea', 'Djibouti', 'Sudan', 'South Sudan', 'Comoros', 'South Africa', 'Somalia', 'Cape Verde', 'Burundi', 'Sierra Leone', 'Botswana', 'Seychelles', 'Nigeria', 'Angola', 'Sao Tome and Principe', 'Namibia', 'Algeria', 'Mozambique', 'Morocco', 'Mauritius', 'Mauritania', 'Malawi', 'Madagascar', 'Libya', 'Liberia'])

        if check_customer == 1:
            user = models.CustomerDetail.objects.get(id = customer)
            
            if flag == 'wishlist':
                wishlist_data = models.WishlistDetail.objects.filter(customer= customer)
                wishlist_serializer = WishlistDetailSerializer(wishlist_data, many=True).data

                # Calculate tracking_amount for wishlist
                active_currency = str(currencyCode).upper().strip() if currencyCode not in [None, '', 'null'] else 'XOF'
                xof_conv = models.CurrencyConverter.objects.filter(currency_code="XOF").first()
                xof_rate = float(xof_conv.system_rate) if xof_conv and xof_conv.system_rate else 589.0
                if active_currency == "XOF":
                    tracking_amount = 1000
                else:
                    usd_tracking = 1000.0 / xof_rate
                    if active_currency == "USD":
                        tracking_amount = round(usd_tracking, 2)
                    else:
                        target_conv = models.CurrencyConverter.objects.filter(currency_code=active_currency).first()
                        target_rate = float(target_conv.system_rate) if target_conv and target_conv.system_rate else None
                        if target_rate:
                            converted_tracking = usd_tracking * target_rate
                            tracking_amount = round(converted_tracking, 2) if is_usd_cart else round(converted_tracking)
                        else:
                            tracking_amount = round(usd_tracking, 2) if is_usd_cart else 1000

                view_fmt_wl = (lambda v: f"{float(v):,.2f}".replace(",", " ")) if is_usd_cart else (lambda v: f"{round(float(v)):,}".replace(",", " "))

                res={
                    'data':wishlist_serializer,
                    'tracking_amount': tracking_amount,
                    'tracking_amount_view': view_fmt_wl(tracking_amount)
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
            
            elif flag == 'cart':
                
                cart_data = models.CartDetail.objects.filter(customer= customer,  product__status = 'Active')
                track_user_activity(
                    action_type='CHECKOUT_INITIATE',
                    customer_id=customer,
                    country=country,
                    metadata={'items_count': cart_data.count()},
                    ip_address=ip_address or request.META.get('REMOTE_ADDR')
                )
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
                        per_product_cart_serializer['product_total'] = round(float(product_total), 2) if is_usd_cart else round(float(product_total))
                        
                        cart_data_list.append(per_product_cart_serializer)

                    res={
                        'data':cart_data_list,
                        'tracking_amount': 1000 if not is_usd_cart else 1.7,
                        'tracking_amount_view': "1 000" if not is_usd_cart else "1.70",
                        'message_en':'Currently not serve in your region',
                        'message_fr':'Actuellement non desservi dans votre region'
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
                                non_usd_obj = models.CurrencyConverter.objects.filter(currency_code = price_by.currency_code).first()
                                non_usd_rate = float(non_usd_obj.system_rate) if non_usd_obj else 589.0
                                usd_price_by_air = float(price_by_air_rate) / non_usd_rate

                                if currencyCode != "USD":
                                    target_curr_obj = models.CurrencyConverter.objects.filter(currency_code = currencyCode).first()
                                    target_rate = float(target_curr_obj.system_rate) if target_curr_obj else 1.0
                                    price_by_air = float(usd_price_by_air) * target_rate
                                else:
                                    price_by_air = usd_price_by_air
                            else:
                                if currencyCode != "USD":
                                    target_curr_obj = models.CurrencyConverter.objects.filter(currency_code = currencyCode).first()
                                    target_rate = float(target_curr_obj.system_rate) if target_curr_obj else 1.0
                                    price_by_air = float(price_by_air_rate) * target_rate
                                else:
                                    price_by_air = price_by_air_rate
                        else:
                            price_by_air = price_by_air_rate

                        per_product_cart_serializer['price_by_air'] = round(float(price_by_air), 2) if is_usd_cart else round(float(price_by_air))
                        # list_air.append(price_by_air)


                    if product.shipping_via == "By Ship":
                        # print("user.countryCode---->",user.countryCode)
                        # print("user.country---->",user.country)
                        price_by = models.CountryWithCurrency.objects.get(country_name = user.country)
                        price_by_ship_rate = price_by.price_by_ship
                        # print(user.countryCode, user.country, 'price_by')
                        
                        if currencyCode not in [None,'','null']:
                            if price_by.currency_code != "USD":
                                non_usd_obj = models.CurrencyConverter.objects.filter(currency_code = price_by.currency_code).first()
                                non_usd_rate = float(non_usd_obj.system_rate) if non_usd_obj else 589.0
                                usd_price_by_ship = float(price_by_ship_rate) / non_usd_rate

                                if currencyCode != "USD":
                                    target_curr_obj = models.CurrencyConverter.objects.filter(currency_code = currencyCode).first()
                                    target_rate = float(target_curr_obj.system_rate) if target_curr_obj else 1.0
                                    price_by_ship = float(usd_price_by_ship) * target_rate
                                else:
                                    price_by_ship = usd_price_by_ship
                            else:
                                if currencyCode != "USD":
                                    target_curr_obj = models.CurrencyConverter.objects.filter(currency_code = currencyCode).first()
                                    target_rate = float(target_curr_obj.system_rate) if target_curr_obj else 1.0
                                    price_by_ship = float(price_by_ship_rate) * target_rate
                                else:
                                    price_by_ship = price_by_ship_rate
                        else:
                            price_by_ship = price_by_ship_rate

                        per_product_cart_serializer['price_by_ship'] = round(float(price_by_ship), 2) if is_usd_cart else round(float(price_by_ship))
                        # list_ship.append(price_by_ship)
                    if product.shipping_via == "By Express":
                        
                        # print(currencyCode, 'price_by')

                        if currencyCode not in [None,'','null']:
                            if price_by.currency_code != "USD":
                                non_usd_obj = models.CurrencyConverter.objects.filter(currency_code = price_by.currency_code).first()
                                non_usd_rate = float(non_usd_obj.system_rate) if non_usd_obj else 589.0
                                usd_price_by_express = float(price_by_express_shipping) / non_usd_rate

                                if currencyCode != "USD":
                                    target_curr_obj = models.CurrencyConverter.objects.filter(currency_code = currencyCode).first()
                                    target_rate = float(target_curr_obj.system_rate) if target_curr_obj else 1.0
                                    price_by_express = float(usd_price_by_express) * target_rate
                                else:
                                    price_by_express = usd_price_by_express
                            else:
                                if currencyCode != "USD":
                                    target_curr_obj = models.CurrencyConverter.objects.filter(currency_code = currencyCode).first()
                                    target_rate = float(target_curr_obj.system_rate) if target_curr_obj else 1.0
                                    price_by_express = float(price_by_express_shipping) * target_rate
                                else:
                                    price_by_express = price_by_express_shipping
                        else:
                            price_by_express = price_by_express_shipping

                        per_product_cart_serializer['price_by_express'] = round(float(price_by_express), 2) if is_usd_cart else round(float(price_by_express))
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
                    shipping_cost_per_product = calculate_shipping_cost(carton_length,carton_width,carton_height,carton_weight,quantity,price_by_air,price_by_ship, price_by_express, is_usd=is_usd_cart)
                    # print(shipping_cost_per_product, 'shipping_cost_per_product')
                    list_air.append(shipping_cost_per_product.get('total_air_cost'))
                    list_ship.append(shipping_cost_per_product.get('total_sea_cost'))
                    list_express.append(shipping_cost_per_product.get('total_express_cost'))
                    
                    product_total = float(quantity) * float(per_product_cart_serializer.get('price'))
                    list_product_amount.append(product_total)
                    
                    per_product_cart_serializer['shipping_cost_per_product'] = shipping_cost_per_product
                    per_product_cart_serializer['product_total'] = round(float(product_total), 2) if is_usd_cart else round(float(product_total))

                    cart_data_list.append(per_product_cart_serializer)
                
                is_usd_cart = (currencyCode == 'USD') or (currencyCode not in ['XOF', 'XAF', 'CDF', 'GNF'] and ((country == 'Egypt') or (price_by and getattr(price_by, 'currency_code', None) == 'USD') or (not price_by and country not in ['XOF', 'XAF', 'CDF', 'GNF'])))
                if is_usd_cart:
                    total_price = round(sum(list_product_amount), 2)
                    total_air = round(sum(list_air), 2)
                    total_ship = round(sum(list_ship), 2)
                    total_express = round(sum(list_express), 2)
                else:
                    total_price = round(sum(list_product_amount))
                    total_air = round(sum(list_air))
                    total_ship = round(sum(list_ship))
                    total_express = round(sum(list_express))

                # Calculate tracking_amount: fixed 1000 in XOF, converted accordingly for other currencies
                active_currency = str(currencyCode).upper().strip() if currencyCode not in [None, '', 'null'] else (getattr(price_by, 'currency_code', None) or ('USD' if is_usd_cart else 'XOF')).upper().strip()

                xof_conv = models.CurrencyConverter.objects.filter(currency_code="XOF").first()
                xof_rate = float(xof_conv.system_rate) if xof_conv and xof_conv.system_rate else 589.0

                if active_currency == "XOF":
                    tracking_amount = 1000
                else:
                    usd_tracking = 1000.0 / xof_rate
                    if active_currency == "USD":
                        tracking_amount = round(usd_tracking, 2)
                    else:
                        target_conv = models.CurrencyConverter.objects.filter(currency_code=active_currency).first()
                        target_rate = float(target_conv.system_rate) if target_conv and target_conv.system_rate else None
                        if target_rate:
                            converted_tracking = usd_tracking * target_rate
                            tracking_amount = round(converted_tracking, 2) if is_usd_cart else round(converted_tracking)
                        else:
                            tracking_amount = round(usd_tracking, 2) if is_usd_cart else 1000

                if promocode:
                    check_promocode = models.PromocodeDetail.objects.filter(promocode = promocode).count()
                    if check_promocode == 1:
                        get_promocode = models.PromocodeDetail.objects.get(promocode = promocode)
                        discount = get_promocode.discount
                        if is_usd_cart:
                            discount_price = round(float(total_price) * float(discount) / 100, 2)
                            price_after_discount = round(total_price - discount_price, 2)
                            amount_to_paid = round(price_after_discount + total_air + total_ship + total_express, 2)
                            amount_to_paid_with_tax = round(amount_to_paid * 1.025, 2)
                            view_fmt = lambda v: f"{float(v):,.2f}".replace(",", " ")
                        else:
                            discount_price = round(float(total_price) * float(discount) / 100)
                            price_after_discount = round(float(total_price) - float(discount_price))
                            amount_to_paid = round(float(price_after_discount) + float(total_air) + float(total_ship) + float(total_express))
                            amount_to_paid_with_tax = round(float(amount_to_paid) * 1.025)
                            view_fmt = lambda v: f"{round(float(v)):,}".replace(",", " ")

                        res={
                            'data':cart_data_list,
                            'total_price': view_fmt(total_price),
                            'discount_price': view_fmt(discount_price),
                            'discount_percentage': discount,
                            'price_after_discount': view_fmt(price_after_discount),
                            'total_air': view_fmt(total_air),
                            'total_ship': view_fmt(total_ship),
                            'total_express': view_fmt(total_express),
                            'tracking_amount': tracking_amount,
                            'tracking_amount_view': view_fmt(tracking_amount),
                            'amount_to_paid_view': view_fmt(amount_to_paid),
                            'amount_to_paid_with_tax_view': view_fmt(amount_to_paid_with_tax),
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
                    if is_usd_cart:
                        amount_to_paid = round(total_price + total_air + total_ship + total_express, 2)
                        amount_to_paid_with_tax = round(amount_to_paid * 1.025, 2)
                        view_fmt = lambda v: f"{float(v):,.2f}".replace(",", " ")
                    else:
                        amount_to_paid = round(float(total_price) + float(total_air) + float(total_ship) + float(total_express))
                        amount_to_paid_with_tax = round(float(amount_to_paid) * 1.025)
                        view_fmt = lambda v: f"{round(float(v)):,}".replace(",", " ")
                    print(tracking_amount, 'tracking_amount')
                    res={
                        'data':cart_data_list,
                        'total_price': view_fmt(total_price),
                        'total_air': view_fmt(total_air),
                        'total_ship': view_fmt(total_ship),
                        'total_express': view_fmt(total_express),
                        'tracking_amount': tracking_amount,
                        'tracking_amount_view': view_fmt(tracking_amount),
                        'amount_to_paid_view': view_fmt(amount_to_paid),
                        'amount_to_paid_with_tax_view': view_fmt(amount_to_paid_with_tax),
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