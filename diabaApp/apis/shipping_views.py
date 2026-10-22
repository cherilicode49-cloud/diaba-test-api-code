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
from diabaApp.serializer import DeliveryDayDetailSerializer

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL




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
def get_shipping_cost(request):
    data = JSONParser().parse(io.BytesIO(request.body))

    # print("data--get_shipping_cost-->", data)

    carton_length = data.get("carton_length")
    carton_width = data.get("carton_width")
    carton_height = data.get("carton_height")
    carton_weight = data.get("carton_weight")
    quantity = data.get("quantity") or 1

    # Fallback dimensions/weight from product or variant if missing
    product_id = data.get("product_id") or data.get("product")
    variant_id = data.get("variant_id") or data.get("variant")
    if variant_id and not product_id:
        try:
            variant_obj = models.ProductModelVariant.objects.filter(id=variant_id).first()
            if variant_obj and hasattr(variant_obj, 'model') and hasattr(variant_obj.model, 'product'):
                product_id = variant_obj.model.product.id
        except Exception:
            pass

    if product_id:
        try:
            product_obj = models.ProductDetail.objects.filter(id=product_id).first()
            if product_obj:
                if carton_length in [None, '', '-', 0, '0']:
                    carton_length = product_obj.carton_length
                if carton_width in [None, '', '-', 0, '0']:
                    carton_width = product_obj.carton_width
                if carton_height in [None, '', '-', 0, '0']:
                    carton_height = product_obj.carton_height
                if carton_weight in [None, '', '-', 0, '0']:
                    carton_weight = product_obj.carton_weight
        except Exception:
            pass

    # Destination country & customer resolution (same logic as customer_views.py & serializer.py)
    customer_id = data.get("customer") or data.get("customer_id") or data.get("user_id")
    customer_obj = None
    if customer_id:
        try:
            customer_obj = models.CustomerDetail.objects.filter(id=customer_id).first()
        except Exception:
            customer_obj = None

    country_name = (
        data.get("delivery_country")
        or data.get("country")
        or data.get("country_name")
        or (customer_obj.country if customer_obj else None)
    )
    country_calling_code = (
        data.get("countryCode")
        or data.get("country_code")
        or (customer_obj.countryCode if customer_obj else None)
    )
    target_currency = (
        data.get("currency")
        or data.get("currency_code")
        or data.get("currencyCode")
    )

    # Resolve CountryWithCurrency
    price_by = None
    if country_name:
        price_by = models.CountryWithCurrency.objects.filter(country_name__iexact=str(country_name).strip()).first()
    if not price_by and country_calling_code:
        price_by = models.CountryWithCurrency.objects.filter(country_calling_code=str(country_calling_code).strip()).first()
    if not price_by and target_currency:
        price_by = models.CountryWithCurrency.objects.filter(currency_code=str(target_currency).strip()).first()

    price_by_air = data.get("price_by_air")
    price_by_ship = data.get("price_by_ship")
    price_by_express = data.get("price_by_express")

    if price_by:
        price_by_air_rate = float(price_by.price_by_air or 0)
        price_by_ship_rate = float(price_by.price_by_ship or 0)
        price_by_express_shipping = float(price_by.express_shipping or 0)

        currency_code = target_currency or price_by.currency_code

        # Currency Conversion logic (identical to customer_views.py)
        if currency_code and currency_code != price_by.currency_code:
            try:
                if price_by.currency_code != "USD":
                    non_usd_obj = models.CurrencyConverter.objects.filter(currency_code=price_by.currency_code).first()
                    non_usd_rate = float(non_usd_obj.system_rate) if non_usd_obj else 1.0
                    usd_air = price_by_air_rate / non_usd_rate
                    usd_ship = price_by_ship_rate / non_usd_rate
                    usd_express = price_by_express_shipping / non_usd_rate

                    if currency_code != "USD":
                        user_curr = models.CurrencyConverter.objects.filter(currency_code=currency_code).first()
                        user_rate = float(user_curr.system_rate) if user_curr else 1.0
                        calc_air = usd_air * user_rate
                        calc_ship = usd_ship * user_rate
                        calc_express = usd_express * user_rate
                    else:
                        calc_air = usd_air
                        calc_ship = usd_ship
                        calc_express = usd_express
                else:
                    if currency_code != "USD":
                        user_curr = models.CurrencyConverter.objects.filter(currency_code=currency_code).first()
                        user_rate = float(user_curr.system_rate) if user_curr else 1.0
                        calc_air = price_by_air_rate * user_rate
                        calc_ship = price_by_ship_rate * user_rate
                        calc_express = price_by_express_shipping * user_rate
                    else:
                        calc_air = price_by_air_rate
                        calc_ship = price_by_ship_rate
                        calc_express = price_by_express_shipping
            except Exception:
                calc_air = price_by_air_rate
                calc_ship = price_by_ship_rate
                calc_express = price_by_express_shipping
        else:
            calc_air = price_by_air_rate
            calc_ship = price_by_ship_rate
            calc_express = price_by_express_shipping

        # Check if incoming rates from frontend are invalid, missing, or unconverted (< 500 when currency is CFA)
        def is_rate_invalid(passed_val, calculated_val, curr):
            if passed_val in [None, '', '-', 0, '0', 0.0, 'null']:
                return True
            try:
                val = float(passed_val)
                if val <= 0:
                    return True
                # If CFA currency (XOF/XAF) or high-unit currency and rate is tiny (< 500) while db rate is >= 500
                if curr in ['XOF', 'XAF', 'CDF', 'GNF'] and val < 500 and calculated_val >= 500:
                    return True
            except (ValueError, TypeError):
                return True
            return False

        if is_rate_invalid(price_by_air, calc_air, currency_code):
            price_by_air = calc_air
        if is_rate_invalid(price_by_ship, calc_ship, currency_code):
            price_by_ship = calc_ship
        if is_rate_invalid(price_by_express, calc_express, currency_code):
            price_by_express = calc_express
    else:
        # Fallback if country record not found but currency indicates CFA and rates are small USD numbers
        curr = target_currency
        if curr in ['XOF', 'XAF']:
            try:
                conv = models.CurrencyConverter.objects.filter(currency_code=curr).first()
                rate = float(conv.system_rate) if conv else 565.0
                if price_by_air and 0 < float(price_by_air) < 500:
                    price_by_air = float(price_by_air) * rate
                if price_by_ship and 0 < float(price_by_ship) < 500:
                    price_by_ship = float(price_by_ship) * rate
                if price_by_express and 0 < float(price_by_express) < 500:
                    price_by_express = float(price_by_express) * rate
            except Exception:
                pass

    result = calculate_shipping_cost(
        carton_length=carton_length,
        carton_width=carton_width,
        carton_height=carton_height,
        carton_weight=carton_weight,
        quantity=quantity,
        price_by_air=price_by_air,
        price_by_ship=price_by_ship,
        price_by_express=price_by_express,
    )

    total_air_cost_view = f"{result.get('total_air_cost'):,}".replace(',', ' ')
    total_sea_cost_view = f"{result.get('total_sea_cost'):,}".replace(',', ' ')
    total_express_cost_view = f"{result.get('total_express_cost'):,}".replace(',', ' ')

    result["total_air_cost_view"] = total_air_cost_view
    result["total_sea_cost_view"] = total_sea_cost_view
    result["total_express_cost_view"] = total_express_cost_view
    result["price_by_air"] = round(float(price_by_air or 0), 2)
    result["price_by_ship"] = round(float(price_by_ship or 0), 2)
    result["price_by_express"] = round(float(price_by_express or 0), 2)

    res = {
        'data': result
    }
    # print("res-=-=---->", res)
    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

@csrf_exempt
def delivery_days_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        update_data = models.DeliveryDayDetail.objects.get(id = id)
        update_data.express_delivery = python_data.get('express_delivery', update_data.express_delivery)
        update_data.air_delivery = python_data.get('air_delivery', update_data.air_delivery)
        update_data.ship_delivery = python_data.get('ship_delivery', update_data.ship_delivery)
        update_data.save()

        res = {
            'message':'Delivery days updated Succesfully.'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def all_delivery_days_list(request):
    if request.method == "POST":
        delivery_data = models.DeliveryDayDetail.objects.first()
        serialser = DeliveryDayDetailSerializer(delivery_data).data
        res = {
            'data':serialser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)