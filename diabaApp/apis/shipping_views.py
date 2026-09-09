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

    # print("data--get_shipping_cost-->",data)

    result = calculate_shipping_cost(
        carton_length=data.get("carton_length"),
        carton_width=data.get("carton_width"),
        carton_height=data.get("carton_height"),
        carton_weight=data.get("carton_weight"),
        quantity=data.get("quantity"),
        price_by_air=data.get("price_by_air"),
        price_by_ship=data.get("price_by_ship"),
        price_by_express=data.get("price_by_express"),
    )

    # print("result=======>",result)

    total_air_cost_view = f"{result.get('total_air_cost'):,}".replace(',', ' ')
    total_sea_cost_view = f"{result.get('total_sea_cost'):,}".replace(',', ' ')
    total_express_cost_view = f"{result.get('total_express_cost'):,}".replace(',', ' ')

    result["total_air_cost_view"] = total_air_cost_view
    result["total_sea_cost_view"] = total_sea_cost_view
    result["total_express_cost_view"] = total_express_cost_view
    
    res={
        'data':result
    }
    # print("res-=-=---->",res)
    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

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