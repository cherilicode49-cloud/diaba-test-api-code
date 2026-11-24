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

from diabaApp.serializer import DeliveryDayDetailSerializer, AvailableCountryForDeliverySerializer



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



        total_air_cost = round(chargeable_air_weight * float(price_by_air or 0), 2)

        total_sea_cost = round(chargeable_sea_weight * float(price_by_ship or 0), 2)

        total_express_cost = round(chargeable_express_weight * float(price_by_express or 0), 2)



        return {

            "cbm": round(total_cbm, 6),

            "chargeable_air_weight": round(chargeable_air_weight, 2),

            "chargeable_sea_weight": round(chargeable_sea_weight, 6),

            "total_air_cost": total_air_cost,

            "total_sea_cost": total_sea_cost,

            "total_express_cost": total_express_cost

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



    # Fallback dimensions/weight from variant or product if missing
    product_id = data.get("product_id") or data.get("product")
    variant_id = data.get("variant_id") or data.get("variant")

    variant_obj = None
    if variant_id:
        try:
            variant_obj = models.ProductModelVariant.objects.filter(id=variant_id).first()
            if variant_obj and not product_id:
                if variant_obj.product_id:
                    product_id = variant_obj.product_id
                elif hasattr(variant_obj, 'model') and hasattr(variant_obj.model, 'product'):
                    product_id = variant_obj.model.product.id
        except Exception:
            pass

    if variant_obj:
        if carton_length in [None, '', '-', 0, '0'] and variant_obj.carton_length:
            carton_length = variant_obj.carton_length
        if carton_width in [None, '', '-', 0, '0'] and variant_obj.carton_width:
            carton_width = variant_obj.carton_width
        if carton_height in [None, '', '-', 0, '0'] and variant_obj.carton_height:
            carton_height = variant_obj.carton_height
        if carton_weight in [None, '', '-', 0, '0'] and variant_obj.carton_weight:
            carton_weight = variant_obj.carton_weight

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

    if not country_name or str(country_name).strip() in ['None', '', 'null']:

        country_name = "Egypt"



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

    if not price_by:

        price_by = models.CountryWithCurrency.objects.filter(country_name="Egypt").first()



    # Always safely initialize currency_code

    if target_currency:

        currency_code = str(target_currency).strip().upper()

    elif price_by and price_by.currency_code:

        currency_code = price_by.currency_code

    elif country_name and str(country_name).strip().lower() == 'egypt':

        currency_code = "USD"

    else:

        currency_code = "USD"



    price_by_air = data.get("price_by_air")

    price_by_ship = data.get("price_by_ship")

    price_by_express = data.get("price_by_express")



    if price_by:

        price_by_air_rate = float(price_by.price_by_air or 0)

        price_by_ship_rate = float(price_by.price_by_ship or 0)

        price_by_express_shipping = float(price_by.express_shipping or 0)



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



    air_cost = float(result.get('total_air_cost') or 0)

    sea_cost = float(result.get('total_sea_cost') or 0)

    express_cost = float(result.get('total_express_cost') or 0)



    is_usd = (currency_code == 'USD') or (price_by and getattr(price_by, 'currency_code', None) == 'USD') or (str(country_name).strip().lower() == 'egypt')



    if is_usd:
        result["total_air_cost"] = round(air_cost, 2)
        result["total_sea_cost"] = round(sea_cost, 2)
        result["total_express_cost"] = round(express_cost, 2)
        result["total_air_cost_view"] = f"{round(air_cost, 2):,.2f}".replace(',', ' ')
        result["total_sea_cost_view"] = f"{round(sea_cost, 2):,.2f}".replace(',', ' ')
        result["total_express_cost_view"] = f"{round(express_cost, 2):,.2f}".replace(',', ' ')
        result["price_by_air"] = round(float(price_by_air or 0), 2)
        result["price_by_ship"] = round(float(price_by_ship or 0), 2)
        result["price_by_express"] = round(float(price_by_express or 0), 2)
    else:
        int_air = round(air_cost)
        int_sea = round(sea_cost)
        int_express = round(express_cost)
        result["total_air_cost"] = int_air
        result["total_sea_cost"] = int_sea
        result["total_express_cost"] = int_express
        result["total_air_cost_view"] = f"{int_air:,}".replace(',', ' ')
        result["total_sea_cost_view"] = f"{int_sea:,}".replace(',', ' ')
        result["total_express_cost_view"] = f"{int_express:,}".replace(',', ' ')
        result["price_by_air"] = round(float(price_by_air or 0))
        result["price_by_ship"] = round(float(price_by_ship or 0))
        result["price_by_express"] = round(float(price_by_express or 0))
    
    # print(result, 'result')

    res = {

        'data': result

    }

    # print("res-=-=---->", res)

    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)



@csrf_exempt
def delivery_days_update(request):
    """
    Update Delivery Days.
    Updates shipping delivery days configuration by record ID or by country.
    Accepts express_delivery, air_delivery, ship_delivery days and optional country.
    """
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        country_val = python_data.get('country') or python_data.get('country_id')

        update_data = None
        if id:
            update_data = models.DeliveryDayDetail.objects.filter(id = id).first()
        elif country_val:
            if str(country_val).isdigit():
                update_data = models.DeliveryDayDetail.objects.filter(country__id=int(country_val)).first()
            if not update_data:
                update_data = models.DeliveryDayDetail.objects.filter(country__country_name__iexact=str(country_val).strip()).first()

        if not update_data:
            res = {'message': 'Delivery day detail record not found.'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=404)

        update_data.express_delivery = python_data.get('express_delivery', update_data.express_delivery)
        update_data.air_delivery = python_data.get('air_delivery', update_data.air_delivery)
        update_data.ship_delivery = python_data.get('ship_delivery', update_data.ship_delivery)
        if country_val:
            if str(country_val).isdigit():
                update_data.country_id = int(country_val)
            else:
                c_obj = models.CountryWithCurrency.objects.filter(country_name__iexact=str(country_val).strip()).first()
                if c_obj:
                    update_data.country = c_obj
        update_data.save()

        res = {
            'message':'Delivery days updated Succesfully.',
            'data': DeliveryDayDetailSerializer(update_data).data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def all_delivery_days_list(request):
    """
    Get Delivery Days (App / Public).
    Returns delivery days configuration. If country is provided in body, returns country-specific delivery days; otherwise returns default delivery days.
    """
    if request.method == "POST":
        country = None
        if request.body:
            try:
                python_data = JSONParser().parse(io.BytesIO(request.body))
                country = python_data.get('country') or python_data.get('countryName') or python_data.get('country_id')
            except Exception:
                pass

        if country:
            delivery_data = models.DeliveryDayDetail.objects.filter(
                models.Q(country__id=country) if str(country).isdigit() else models.Q(country__country_name__iexact=country)
            ).first()
            if not delivery_data:
                delivery_data = models.DeliveryDayDetail.objects.first()
        else:
            delivery_data = models.DeliveryDayDetail.objects.first()

        if delivery_data:
            serialser = DeliveryDayDetailSerializer(delivery_data).data
        else:
            serialser = {
                'express_delivery': 10,
                'air_delivery': 25,
                'ship_delivery': 90,
                'country': None,
                'country_name': None
            }

        res = {
            'data':serialser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def delivery_day_detail_list_admin(request):
    """
    List Delivery Day Details (Admin).
    Returns list of all delivery day details per country with currency and shipping method timeframes.
    Supports optional search or country filtering in query params or POST body.
    """
    if request.method in ["POST", "GET"]:
        python_data = {}
        if request.body:
            try:
                python_data = JSONParser().parse(io.BytesIO(request.body))
            except Exception:
                pass

        search = python_data.get('search') or request.GET.get('search')
        country = python_data.get('country') or python_data.get('country_id') or request.GET.get('country')

        queryset = models.DeliveryDayDetail.objects.all().select_related('country').order_by('-id')

        if search:
            queryset = queryset.filter(
                Q(country__country_name__icontains=search) |
                Q(country__country_calling_code__icontains=search) |
                Q(country__currency_code__icontains=search)
            )

        if country:
            if str(country).isdigit():
                queryset = queryset.filter(country__id=int(country))
            else:
                queryset = queryset.filter(country__country_name__iexact=str(country).strip())

        serializer = DeliveryDayDetailSerializer(queryset, many=True).data
        res = {
            'data': serializer,
            'total_count': queryset.count(),
            'message': 'Delivery day details fetched successfully.'
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

    res = {'message': 'Invalid request method.'}
    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=405)


@csrf_exempt
def delivery_day_detail_add_admin(request):
    """
    Add Delivery Day Detail (Admin).
    Creates a new delivery day timeframe record for a country with express_delivery, air_delivery, and ship_delivery days.
    """
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body)) if request.body else {}

        country_val = python_data.get('country') or python_data.get('country_id') or python_data.get('countryName')
        if not country_val:
            res = {'message': 'Country is required.'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        c_obj = None
        if str(country_val).isdigit():
            c_obj = models.CountryWithCurrency.objects.filter(id=int(country_val)).first()
        if not c_obj:
            c_obj = models.CountryWithCurrency.objects.filter(
                Q(country_name__iexact=str(country_val).strip()) |
                Q(country_iso_alphaTwo_key__iexact=str(country_val).strip())
            ).first()

        if not c_obj:
            res = {'message': f'Country "{country_val}" not found in CountryWithCurrency.'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        existing = models.DeliveryDayDetail.objects.filter(country=c_obj).first()
        if existing:
            res = {
                'message': f'Delivery day detail already exists for {c_obj.country_name}.',
                'data': DeliveryDayDetailSerializer(existing).data
            }
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        express_delivery = python_data.get('express_delivery', 10)
        air_delivery = python_data.get('air_delivery', 25)
        ship_delivery = python_data.get('ship_delivery', 90)

        new_detail = models.DeliveryDayDetail.objects.create(
            country=c_obj,
            express_delivery=express_delivery,
            air_delivery=air_delivery,
            ship_delivery=ship_delivery
        )

        serializer = DeliveryDayDetailSerializer(new_detail).data
        res = {
            'message': 'Delivery day detail added successfully.',
            'data': serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

    res = {'message': 'Invalid request method.'}
    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=405)


@csrf_exempt
def delivery_day_detail_update_admin(request):
    """
    Update Delivery Day Detail (Admin).
    Updates express_delivery, air_delivery, ship_delivery days or reassigns country for an existing record by id.
    """
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body)) if request.body else {}

        detail_id = python_data.get('id')
        country_val = python_data.get('country') or python_data.get('country_id') or python_data.get('countryName')

        detail_obj = None
        if detail_id:
            detail_obj = models.DeliveryDayDetail.objects.filter(id=detail_id).first()
        elif country_val:
            if str(country_val).isdigit():
                detail_obj = models.DeliveryDayDetail.objects.filter(country__id=int(country_val)).first()
            if not detail_obj:
                detail_obj = models.DeliveryDayDetail.objects.filter(country__country_name__iexact=str(country_val).strip()).first()

        if not detail_obj:
            res = {'message': 'Delivery day detail record not found.'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=404)

        if 'country' in python_data or 'country_id' in python_data:
            c_val = python_data.get('country') or python_data.get('country_id')
            if c_val:
                c_obj = None
                if str(c_val).isdigit():
                    c_obj = models.CountryWithCurrency.objects.filter(id=int(c_val)).first()
                if not c_obj:
                    c_obj = models.CountryWithCurrency.objects.filter(country_name__iexact=str(c_val).strip()).first()
                if c_obj:
                    dup = models.DeliveryDayDetail.objects.filter(country=c_obj).exclude(id=detail_obj.id).first()
                    if dup:
                        res = {'message': f'Delivery day detail already exists for {c_obj.country_name}.'}
                        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)
                    detail_obj.country = c_obj

        if 'express_delivery' in python_data:
            detail_obj.express_delivery = python_data.get('express_delivery')

        if 'air_delivery' in python_data:
            detail_obj.air_delivery = python_data.get('air_delivery')

        if 'ship_delivery' in python_data:
            detail_obj.ship_delivery = python_data.get('ship_delivery')

        detail_obj.save()

        serializer = DeliveryDayDetailSerializer(detail_obj).data
        res = {
            'message': 'Delivery days updated successfully.',
            'data': serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

    res = {'message': 'Invalid request method.'}
    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=405)


@csrf_exempt
def delivery_day_detail_delete_admin(request):
    """
    Delete Delivery Day Detail (Admin).
    Permanently deletes a DeliveryDayDetail configuration record by ID.
    """
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body)) if request.body else {}
        detail_id = python_data.get('id')

        if not detail_id:
            res = {'message': 'id is required.'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        detail_obj = models.DeliveryDayDetail.objects.filter(id=detail_id).first()
        if not detail_obj:
            res = {'message': 'Delivery day detail record not found.'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=404)

        detail_obj.delete()
        res = {'message': 'Delivery day detail deleted successfully.'}
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

    res = {'message': 'Invalid request method.'}
    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=405)


@csrf_exempt
def delivery_day_available_countries_admin(request):
    """
    Get Available Countries for Delivery Days (Admin).
    Returns list of all country data from CountryWithCurrency that DO NOT yet have a DeliveryDayDetail record created.
    No parameters required. Simply trigger this API (GET or POST) to get all unconfigured country records.
    """
    if request.method == "GET" or request.method == "POST":
        # Get all country IDs already configured in DeliveryDayDetail
        existing_country_ids = models.DeliveryDayDetail.objects.filter(
            country__isnull=False
        ).values_list('country_id', flat=True)

        # Exclude configured countries from CountryWithCurrency
        queryset = models.CountryWithCurrency.objects.exclude(
            id__in=existing_country_ids
        ).order_by('country_name')

        serializer = AvailableCountryForDeliverySerializer(queryset, many=True).data
        res = {
            'data': serializer,
            'total_count': queryset.count(),
            'message': 'Available countries fetched successfully.'
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

    res = {'message': 'Invalid request method.'}
    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=405)