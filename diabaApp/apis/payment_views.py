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
from django.core.files.base import ContentFile, File
from diabaApp.payment_gateway import APIDTSClient
from weasyprint import HTML
from decimal import Decimal
from firebase_admin import messaging
import uuid
from django.shortcuts import render
from urllib.parse import urlparse, parse_qs
from django.template.loader import render_to_string

import time
import hmac
import hashlib

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL
import  requests


@csrf_exempt
def cash_in_view(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))

    amount = python_data.get("amount")
    phone = python_data.get("phone")
    network = python_data.get("network_code")  
    currency = python_data.get("currency", "XOF")

    result = APIDTSClient.cash_in(amount, phone, network, currency)

    res={
        'data': result
    }
    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)



@csrf_exempt
def payment_callback(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))
    context = python_data.get('context')
    txn_id = python_data.get('txnId')

    # print(python_data, 'status')
    result = APIDTSClient.check_status(txn_id)
    status = result["transaction"]["status"]
    reference_id = txn_id
    now = datetime.now()
    date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
    print(status, 'statusstatus')
    if status == 'completed':
        get_transaction = models.OrderTransaction.objects.get(reference_id = reference_id)
        get_transaction.status = status
        get_transaction.save()

        get_order = models.OrderDetail.objects.get(id = get_transaction.order.id)
        get_order.status = status
        get_order.save()

        order_id = get_transaction.order.id
        get_customer = get_transaction.order.customer.id
        if get_transaction.order.promocode != None:
            get_promocode = get_transaction.order.promocode.id
            create_tracking = models.PromocodeTracking.objects.create(
                order_id = order_id,
                promocode_id = get_promocode,
                customer_id = get_customer,
                created_at = date_time
            ).save()

        order_id = context['order_id']
        order = models.OrderDetail.objects.get(id = order_id)
        order_number = order.order_id
        html_string = render_to_string("order_invoice.html", context)

        pdf_bytes = HTML(string=html_string).write_pdf()
        order.invoice.save(f"{order_number}.pdf",ContentFile(pdf_bytes),save=True)

        get_email = context['get_email']
        # print(order_id, get_email)
        if get_email != None and get_email != "null" and get_email != '':
            try:
                htmlgen = get_template("order_confirm.html").render(context)
                # print(htmlgen, 'htmlgen')

                send_mail(
                    subject='Order Confirmation',
                    message='Your order has been confirmed successfully.',
                    from_email=settings.DEFAULT_FROM_EMAIL,  # or EMAIL_HOST_USER
                    recipient_list=[get_email],
                    fail_silently=False,
                    html_message=htmlgen
                )

            except Exception as e:
                print("error:..............",e)
        

        
        # print(get_transaction, 'get_transaction')
        cart_data = models.CartDetail.objects.filter(customer = get_transaction.customer.id)
        cart_data.delete()

        res={
            'status': status,
            'message':"Transaction Create Successfully.",
            
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
    else:
        # try:
        #     get_transaction = models.OrderTransaction.objects.get(reference_id = reference_id)
        #     get_order = models.OrderDetail.objects.filter(id = get_transaction.order.id)
        #     print(get_order, 'get_order')
        #     get_order.delete()
        # except: 
        #     pass
        
        if status == "pending":
            status = "failed" 

        get_transaction = models.OrderTransaction.objects.get(reference_id = reference_id)
        get_transaction.status = status
        get_transaction.save()

        get_order = models.OrderDetail.objects.get(id = get_transaction.order.id)
        get_order.order_status = status
        get_order.status = status
        get_order.save()



        res={
            'status': status,
            'message':"Transaction failed.",
            
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

@csrf_exempt
def status_view(request, txn_id):
    result = APIDTSClient.check_status(txn_id)
    res={
        'data': result
    }
    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)



@csrf_exempt
def create_wave_checkout(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        print(python_data, 'python_data')
        amount = python_data.get('amount')
        # amount = 10
        currency = python_data.get('currency', 'XOF')
        success_url = "https://diaba.store/payment-success/"
        error_url = "https://diaba.store/payment-failed/"


        url = "https://api.wave.com/v1/checkout/sessions"

        payload = {
            "amount": amount,
            "currency": currency,
            "error_url": error_url,
            "success_url": success_url
        }

        timestamp = str(int(time.time()))

        body_str = json.dumps(payload, separators=(',', ':'))  # IMPORTANT
        message = f"{timestamp}{body_str}"

        signature = hmac.new(
            settings.WAVE_SIGNING_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Authorization": f"Bearer {settings.WAVE_API_KEY}",
            "Wave-Signature": f"t={timestamp},v1={signature}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, data=body_str, headers=headers)

        res = {
            'data': response.json()
        }
        return HttpResponse(JSONRenderer().render(res),content_type='application/json',status=response.status_code)


@csrf_exempt
def get_wave_checkout_session(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        url = f"https://api.wave.com/v1/checkout/sessions/{id}"

        timestamp = str(int(time.time()))
        body_str = ""   # VERY IMPORTANT
        message = f"{timestamp}{body_str}"

        signature = hmac.new(
            settings.WAVE_SIGNING_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Authorization": f"Bearer {settings.WAVE_API_KEY}",
            "Wave-Signature": f"t={timestamp},v1={signature}",
        }

        try:
            response = requests.get(url, headers=headers)
            res = {
                "data": response.json()
            }
            return HttpResponse(JSONRenderer().render(res),content_type='application/json',status=response.status_code)

        except Exception as e:
            return HttpResponse(JSONRenderer().render({"error": str(e)}),content_type='application/json',status=500)


def get_access_token():
    url = "https://api.orange.com/oauth/v3/token"

    try:
        response = requests.post(
            url,
            auth=(settings.ORANGE_CLIENT_ID, settings.ORANGE_CLIENT_SECRET),
            data={"grant_type": "client_credentials"},
            timeout=10
        )

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        response.raise_for_status()
        return response.json().get("access_token")

    except requests.RequestException as e:
        print("FULL ERROR:", str(e))
        return None



@csrf_exempt
def initiate_payment(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))
    amount = python_data.get('amount')
    # amount = request.data.get("amount")

    if not amount:
        res={
            "error": "Amount is required"
            }
        return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=400)
    token = get_access_token()
    
    if not token:
        res={
            "error": "Failed to get access token"
            }
        return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=400)

    order_id = str(uuid.uuid4())

    # Save initial payment record
    # payment = Payment.objects.create(
    #     order_id=order_id,
    #     amount=amount,
    #     status="PENDING"
    # )

    url = "https://api.orange.com/orange-money-webpay/dev/v1/webpayment"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "merchant_key": settings.ORANGE_MERCHANT_KEY,
        "currency": "XOF",
        "order_id": order_id,
        "amount": amount,
        "return_url": "https://diaba.store/payment-failed/",
        "cancel_url": "https://diaba.store/payment-failed/",
        # success_url = "https://diaba.store/payment-success/"
        # error_url = "https://diaba.store/payment-failed/"
        "notif_url": "https://api.diaba.store.com/api/orange/callback",
        "lang": "en"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # return Response({
        #     "payment_url": data.get("payment_url"),
        #     "order_id": order_id
        # })

        res={
            "payment_url": data.get("payment_url"),
            "order_id": order_id
        }
        return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=200)

    except requests.RequestException as e:
        # payment.status = "FAILED"
        # payment.save()

        # return Response(
        #     {"error": "Payment initiation failed", "details": str(e)},
        #     status=status.HTTP_500_INTERNAL_SERVER_ERROR
        # )
        res={
            "error": "Payment initiation failed", 
            "details": str(e)
        }
        return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=500)




PIX_BASE_URL = "https://api.pixprovider.com"
PIX_API_KEY = 'PIX_560e8b6f-6038-41f8-8469-89c54f3611dd'

@csrf_exempt
def pay_pix_test(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))
    amount = python_data.get("amount")
    txid = str(uuid.uuid4())
    print(txid, 'txidtxid')
    payload = {
        "txid": txid,
        "amount": float(amount),
        "description": "PIX Payment"
    }

    headers = {
        "Authorization": f"Bearer {PIX_API_KEY}",
        "Content-Type": "application/json",
    }
    print('try')
    try:
        response = requests.post(
            f"{PIX_BASE_URL}/pix/charges",
            json=payload,
            headers=headers,
            timeout=1,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        res = {
            "error": "PIX provider error", "details": str(e)
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=502)


    data = response.json()
    return render(request, "error_url.html")


def success_url(request):
    return render(request, "success_url.html")

def error_url(request):
    return render(request, "error_url.html")


@csrf_exempt
def send_otp_whatsapp(request):
    if request.method =="POST":
        url = "https://api.verifyway.com/api/v1/"
        headers = {
            "Authorization": "Bearer 1515$iwLeuAjYrEcHnD8Rs2GymuXAefPF8M5fx7wV",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        code = 986987
        payload = {
            "recipient": "+919265096459",
            "type": "otp",
            "channel": "whatsapp",
            "fallback": "no",
            "code": code,
            "lang": "en",
            "message": f"Hello! Your Secure Login Code for Diaba app is {code}. Do not share this with anyone."
        }
        response = requests.post(url, json=payload, headers=headers)
        print(response, 'responseresponse')
        res={
        "status_code": response.status_code,
        "response": response.json()
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def initiate_bictorys_payment(request):
 
    try:
 
        # -----------------------------------------
        # Validate request method
        # -----------------------------------------
 
        if request.method != "POST":
 
            return HttpResponse(
                JSONRenderer().render({
                    "success": False,
                    "error": "POST method required"
                }),
                content_type="application/json",
                status=405
            )
 
        # -----------------------------------------
        # Parse request
        # -----------------------------------------
 
        try:
 
            python_data = JSONParser().parse(
                io.BytesIO(request.body)
            )
 
        except Exception as e:
 
            return HttpResponse(
                JSONRenderer().render({
                    "success": False,
                    "error": "Invalid JSON payload",
                    "details": str(e)
                }),
                content_type="application/json",
                status=400
            )
 
        amount = python_data.get("amount")
 
        if amount is None:
 
            return HttpResponse(
                JSONRenderer().render({
                    "success": False,
                    "error": "Amount is required"
                }),
                content_type="application/json",
                status=400
            )
 
        # -----------------------------------------
        # Validate amount
        # -----------------------------------------
 
        try:
 
            amount = float(amount)
 
        except (ValueError, TypeError):
 
            return HttpResponse(
                JSONRenderer().render({
                    "success": False,
                    "error": "Invalid amount"
                }),
                content_type="application/json",
                status=400
            )
 
        if amount <= 0:
 
            return HttpResponse(
                JSONRenderer().render({
                    "success": False,
                    "error": "Amount must be greater than zero"
                }),
                content_type="application/json",
                status=400
            )
 
        # -----------------------------------------
        # Generate payment reference
        # -----------------------------------------
 
        payment_reference = (
            f"BICT-"
            f"{uuid.uuid4().hex[:12].upper()}"
        )
 
        # Example:
        # BICT-83CD18D2A728
 
        # -----------------------------------------
        # Bictorys API
        # -----------------------------------------
 
        url = (
            f"{settings.BICTORYS_API_URL}"
            f"/pay/v1/charges"
        )
 
        # IMPORTANT:
        # Do NOT send payment_type here.
        #
        # Without payment_type, Bictorys Checkout
        # allows the customer to select the available
        # payment method from the hosted checkout page.
        #
        # Examples:
        # - Card
        # - Mobile Money
        # - Wave
        # - Orange Money
        # - Other available methods
        #
        # Therefore there is intentionally NO:
        #
        # params = {
        #     "payment_type": "card"
        # }
 
        headers = {
 
            "X-Api-Key":
                settings.BICTORYS_API_KEY,
 
            "Content-Type":
                "application/json",
 
            "Accept":
                "application/json"
        }
 
        # -----------------------------------------
        # Payload
        # -----------------------------------------
 
        payload = {
 
            # "amount": amount,
            "amount": 10,
 
            "currency": "XOF",
 
            "country": "SN",
 
            "paymentReference":
                payment_reference,
 
            # Existing Diaba deep-link / App Link /
            # Universal Link URL.
            #
            # Bictorys redirects the user's browser
            # here after successful payment.
            "successRedirectUrl":
                "https://diaba.store/payment-success/",
 
            # Existing Diaba failure callback.
            "errorRedirectUrl":
                "https://diaba.store/payment-failed/"
        }
 
        print(
            "BICTORYS REQUEST:",
            payload
        )
 
        # -----------------------------------------
        # Request
        # -----------------------------------------
 
        response = requests.post(
 
            url,
 
            json=payload,
 
            headers=headers,
 
            timeout=30
        )
 
        # -----------------------------------------
        # Parse Bictorys response
        # -----------------------------------------
 
        try:
 
            data = response.json()
 
        except ValueError:
 
            data = {
                "message":
                    response.text
            }
 
        print(
            "BICTORYS RESPONSE:",
            data
        )
 
        # -----------------------------------------
        # Handle Bictorys API error
        # -----------------------------------------
 
        if response.status_code not in [
            200,
            201,
            202
        ]:
 
            return HttpResponse(
                JSONRenderer().render({
 
                    "success": False,
 
                    "error":
                        "Payment initiation failed",
 
                    "status_code":
                        response.status_code,
 
                    "details":
                        data
                }),
                content_type="application/json",
                status=response.status_code
            )
 
        # -----------------------------------------
        # Extract Checkout URL
        # -----------------------------------------
 
        payment_url = (
 
            data.get("link")
 
            or data.get("checkoutUrl")
 
            or data.get("checkout_url")
 
            or data.get("payment_url")
        )
 
        if not payment_url:
 
            return HttpResponse(
                JSONRenderer().render({
 
                    "success": False,
 
                    "error":
                        "Payment URL not received",
 
                    "details":
                        data
                }),
                content_type="application/json",
                status=502
            )
 
        # -----------------------------------------
        # Extract Bictorys transaction / charge ID
        # -----------------------------------------
 
        charge_id = (
 
            data.get("id")
 
            or data.get("transactionId")
 
            or data.get("transaction_id")
 
            or data.get("charge_id")
        )
 
        # -----------------------------------------
        # Extract charge ID from Checkout URL
        # -----------------------------------------
 
        if not charge_id:
 
            try:
 
                parsed_url = urlparse(
                    payment_url
                )
 
                query_params = parse_qs(
                    parsed_url.query
                )
 
                charge_id = (
                    query_params
                    .get(
                        "charge_id",
                        [None]
                    )[0]
                )
 
            except Exception as e:
 
                print(
                    "Charge ID extraction error:",
                    e
                )
 
        print(
            "Bictorys Charge ID:",
            charge_id
        )
 
        # -----------------------------------------
        # Create local pending transaction
        # -----------------------------------------
 
        transaction = (
            models.OrderTransaction.objects.create(
 
                order=None,
 
                customer=None,
 
                # IMPORTANT:
                # Do not store "card" here because
                # the customer has not selected a
                # payment method yet.
                #
                # Bictorys Checkout will allow the
                # customer to choose the payment method.
                payment_type="bictorys",
 
                cash_status="pending",
 
                payment_id=charge_id,
 
                reference_id=payment_reference,
 
                fee_amount="0",
 
                net_amount=str(amount),
 
                total_amount=str(amount),
 
                tax_price="0",
 
                currency="XOF",
 
                status="PENDING"
            )
        )
 
        # -----------------------------------------
        # Response to React Native
        # -----------------------------------------
 
        return HttpResponse(
            JSONRenderer().render({
 
                "success": True,
 
                "message":
                    "Payment initiated successfully",
 
                "transaction_id":
                    transaction.id,
 
                "payment_reference":
                    payment_reference,
 
                "bictorys_transaction_id":
                    charge_id,
 
                "payment_url":
                    payment_url,
 
                "amount":
                    amount,
 
                "currency":
                    "XOF",
 
                "status":
                    "PENDING"
            }),
            content_type="application/json",
            status=200
        )
 
    # ---------------------------------------------
    # Bictorys / Requests exception
    # ---------------------------------------------
 
    except requests.RequestException as e:
 
        print(
            "BICTORYS REQUEST ERROR:",
            str(e)
        )
 
        return HttpResponse(
            JSONRenderer().render({
 
                "success": False,
 
                "error":
                    "Bictorys API request failed",
 
                "details":
                    str(e)
            }),
            content_type="application/json",
            status=500
        )
 
    # ---------------------------------------------
    # Generic exception
    # ---------------------------------------------
 
    except Exception as e:
 
        print(
            "BICTORYS PAYMENT ERROR:",
            str(e)
        )
 
        return HttpResponse(
            JSONRenderer().render({
 
                "success": False,
 
                "error":
                    "Payment initiation failed",
 
                "details":
                    str(e)
            }),
            content_type="application/json",
            status=500
        )



@csrf_exempt
def bictorys_payment_status(request):

    try:

        if request.method != "POST":

            return HttpResponse(
                JSONRenderer().render({
                    "success": False,
                    "error": "POST method required"
                }),
                content_type="application/json",
                status=405
            )

        # -----------------------------------------
        # Parse
        # -----------------------------------------

        data = JSONParser().parse(
            io.BytesIO(request.body)
        )

        payment_reference = data.get(
            "payment_reference"
        )

        if not payment_reference:

            return HttpResponse(
                JSONRenderer().render({
                    "success": False,
                    "error":
                        "payment_reference is required"
                }),
                content_type="application/json",
                status=400
            )

        # -----------------------------------------
        # Find transaction
        # -----------------------------------------

        transaction = (
            models.OrderTransaction.objects
            .filter(
                reference_id=payment_reference
            )
            .order_by("-id")
            .first()
        )

        if not transaction:

            return HttpResponse(
                JSONRenderer().render({

                    "success": False,

                    "error":
                        "Payment transaction not found"
                }),
                content_type="application/json",
                status=404
            )

        # =================================================
        # IMPORTANT
        #
        # If webhook already confirmed it,
        # don't downgrade it.
        # =================================================

        if transaction.status == "SUCCEEDED":

            return HttpResponse(
                JSONRenderer().render({

                    "success": True,

                    "payment_reference":
                        payment_reference,

                    "transaction_id":
                        transaction.id,

                    "bictorys_transaction_id":
                        transaction.payment_id,

                    "payment_status":
                        "SUCCEEDED",

                    "cash_status":
                        "paid",

                    "amount":
                        transaction.total_amount,

                    "currency":
                        transaction.currency,

                    "message":
                        "Payment already confirmed"
                }),
                content_type="application/json",
                status=200
            )

        # -----------------------------------------
        # Charge ID
        # -----------------------------------------

        charge_id = transaction.payment_id

        if not charge_id:

            return HttpResponse(
                JSONRenderer().render({

                    "success": False,

                    "error":
                        "Bictorys transaction ID not found"
                }),
                content_type="application/json",
                status=400
            )

        # -----------------------------------------
        # Bictorys status URL
        # -----------------------------------------

        url = (
            f"{settings.BICTORYS_API_URL}"
            f"/pay/v1/transactions/"
            f"{charge_id}/status"
        )

        headers = {

            "X-Api-Key":
                settings.BICTORYS_API_KEY,

            "Accept":
                "application/json"
        }

        response = requests.get(

            url,

            headers=headers,

            timeout=30
        )

        try:

            bictorys_data = response.json()

        except ValueError:

            bictorys_data = {
                "message":
                    response.text
            }

        print(
            "Bictorys status:",
            bictorys_data
        )

        if response.status_code != 200:

            return HttpResponse(
                JSONRenderer().render({

                    "success": False,

                    "error":
                        "Unable to check payment status",

                    "status_code":
                        response.status_code,

                    "details":
                        bictorys_data
                }),
                content_type="application/json",
                status=response.status_code
            )

        # -----------------------------------------
        # Get verified status
        # -----------------------------------------

        bictorys_status = str(
            bictorys_data.get("status")
            or "pending"
        ).lower()

        # -----------------------------------------
        # SUCCESS
        # -----------------------------------------

        if bictorys_status in [

            "success",
            "succeeded",
            "successful",
            "paid",
            "completed"

        ]:

            transaction.status = "SUCCEEDED"

            transaction.cash_status = "paid"

            transaction.save(
                update_fields=[
                    "status",
                    "cash_status"
                ]
            )

        # -----------------------------------------
        # FAILED
        # -----------------------------------------

        elif bictorys_status in [

            "failed",
            "cancelled",
            "canceled",
            "reversed"

        ]:

            transaction.status = (
                bictorys_status.upper()
            )

            transaction.cash_status = (
                bictorys_status
            )

            transaction.save(
                update_fields=[
                    "status",
                    "cash_status"
                ]
            )

        # -----------------------------------------
        # PENDING
        # -----------------------------------------

        else:

            transaction.status = "PENDING"

            transaction.cash_status = "pending"

            transaction.save(
                update_fields=[
                    "status",
                    "cash_status"
                ]
            )

        # -----------------------------------------
        # Response
        # -----------------------------------------

        return HttpResponse(
            JSONRenderer().render({

                "success": True,

                "payment_reference":
                    payment_reference,

                "transaction_id":
                    transaction.id,

                "bictorys_transaction_id":
                    transaction.payment_id,

                "payment_status":
                    transaction.status,

                "cash_status":
                    transaction.cash_status,

                "amount":
                    transaction.total_amount,

                "currency":
                    transaction.currency,

                "bictorys_response":
                    bictorys_data
            }),
            content_type="application/json",
            status=200
        )

    except requests.RequestException as e:

        return HttpResponse(
            JSONRenderer().render({

                "success": False,

                "error":
                    "Bictorys request failed",

                "details":
                    str(e)
            }),
            content_type="application/json",
            status=500
        )

    except Exception as e:

        return HttpResponse(
            JSONRenderer().render({

                "success": False,

                "error":
                    "Payment status failed",

                "details":
                    str(e)
            }),
            content_type="application/json",
            status=500
        )


import secrets
@csrf_exempt
def bictorys_webhook(request):

    try:

        # -----------------------------------------
        # Only POST is allowed
        # -----------------------------------------

        if request.method != "POST":

            return JsonResponse(
                {
                    "success": False,
                    "error": "POST method required"
                },
                status=405
            )

        # -----------------------------------------
        # Verify Bictorys webhook secret
        # -----------------------------------------

        received_secret = request.headers.get(
            "X-Secret-Key"
        )

        expected_secret = getattr(
            settings,
            "BICTORYS_WEBHOOK_SECRET",
            None
        )

        if not expected_secret:

            print(
                "BICTORYS WEBHOOK ERROR: "
                "BICTORYS_WEBHOOK_SECRET is not configured"
            )

            return JsonResponse(
                {
                    "success": False,
                    "error": "Webhook secret not configured"
                },
                status=500
            )

        if not received_secret:

            print(
                "BICTORYS WEBHOOK ERROR: "
                "Missing X-Secret-Key"
            )

            return JsonResponse(
                {
                    "success": False,
                    "error": "Unauthorized"
                },
                status=401
            )

        if not secrets.compare_digest(
            received_secret,
            expected_secret
        ):

            print(
                "BICTORYS WEBHOOK ERROR: "
                "Invalid X-Secret-Key"
            )

            return JsonResponse(
                {
                    "success": False,
                    "error": "Unauthorized"
                },
                status=401
            )

        # -----------------------------------------
        # Parse webhook payload
        # -----------------------------------------

        try:

            data = json.loads(
                request.body.decode("utf-8")
            )

        except (json.JSONDecodeError, UnicodeDecodeError) as e:

            print(
                "BICTORYS WEBHOOK ERROR: "
                "Invalid JSON",
                str(e)
            )

            return JsonResponse(
                {
                    "success": False,
                    "error": "Invalid JSON payload"
                },
                status=400
            )

        print(
            "BICTORYS WEBHOOK RECEIVED:",
            data
        )

        # -----------------------------------------
        # Extract required fields
        # -----------------------------------------

        payment_reference = data.get(
            "paymentReference"
        )

        status = str(
            data.get("status", "")
        ).lower()

        transaction_id = data.get(
            "id"
        )

        payment_type = data.get(
            "pspName"
        )

        amount = data.get(
            "amount"
        )

        currency = data.get(
            "currency"
        )

        settled_amount = data.get(
            "settledAmount"
        )

        settled_currency = data.get(
            "settledCurrency"
        )

        # -----------------------------------------
        # Validate required fields
        # -----------------------------------------

        if not payment_reference:

            print(
                "BICTORYS WEBHOOK ERROR: "
                "Missing paymentReference"
            )

            return JsonResponse(
                {
                    "success": False,
                    "error": "paymentReference is required"
                },
                status=400
            )

        if not status:

            print(
                "BICTORYS WEBHOOK ERROR: "
                "Missing status"
            )

            return JsonResponse(
                {
                    "success": False,
                    "error": "status is required"
                },
                status=400
            )

        # -----------------------------------------
        # Find local transaction
        # -----------------------------------------

        transaction = (
            models.OrderTransaction.objects
            .filter(
                reference_id=payment_reference
            )
            .first()
        )

        if not transaction:

            print(
                "BICTORYS WEBHOOK ERROR: "
                "Transaction not found:",
                payment_reference
            )

            return JsonResponse(
                {
                    "success": False,
                    "error": "Transaction not found"
                },
                status=404
            )

        # -----------------------------------------
        # Idempotency
        # -----------------------------------------
        #
        # Bictorys may send the webhook more than once.
        # Do not process an already completed transaction
        # again.
        # -----------------------------------------

        if str(transaction.status).upper() in [
            "SUCCESS",
            "SUCCEEDED",
            "COMPLETED"
        ]:

            print(
                "BICTORYS WEBHOOK: "
                "Transaction already processed:",
                payment_reference
            )

            return JsonResponse(
                {
                    "success": True,
                    "message": "Transaction already processed"
                },
                status=200
            )

        # -----------------------------------------
        # Validate amount
        # -----------------------------------------

        try:

            webhook_amount = float(
                amount
            )

            local_amount = float(
                transaction.total_amount
            )

        except (ValueError, TypeError):

            print(
                "BICTORYS WEBHOOK ERROR: "
                "Invalid amount"
            )

            return JsonResponse(
                {
                    "success": False,
                    "error": "Invalid transaction amount"
                },
                status=400
            )

        # -----------------------------------------
        # Validate currency
        # -----------------------------------------

        local_currency = str(
            transaction.currency or ""
        ).upper()

        webhook_currency = str(
            currency or ""
        ).upper()

        # -----------------------------------------
        # Handle successful payment
        # -----------------------------------------

        if status in [
            "succeeded",
            "authorized"
        ]:

            # -------------------------------------
            # Validate amount
            # -------------------------------------

            if webhook_amount != local_amount:

                print(
                    "BICTORYS WEBHOOK ERROR: "
                    "Amount mismatch",
                    {
                        "payment_reference":
                            payment_reference,
                        "webhook_amount":
                            webhook_amount,
                        "local_amount":
                            local_amount
                    }
                )

                transaction.status = "FAILED"
                transaction.cash_status = "failed"
                transaction.save(
                    update_fields=[
                        "status",
                        "cash_status"
                    ]
                )

                return JsonResponse(
                    {
                        "success": False,
                        "error": "Amount mismatch"
                    },
                    status=400
                )

            # -------------------------------------
            # Validate currency
            # -------------------------------------

            if (
                local_currency
                and webhook_currency
                and local_currency != webhook_currency
            ):

                print(
                    "BICTORYS WEBHOOK ERROR: "
                    "Currency mismatch",
                    {
                        "payment_reference":
                            payment_reference,
                        "webhook_currency":
                            webhook_currency,
                        "local_currency":
                            local_currency
                    }
                )

                transaction.status = "FAILED"
                transaction.cash_status = "failed"
                transaction.save(
                    update_fields=[
                        "status",
                        "cash_status"
                    ]
                )

                return JsonResponse(
                    {
                        "success": False,
                        "error": "Currency mismatch"
                    },
                    status=400
                )

            # -------------------------------------
            # Update payment method
            # -------------------------------------

            if payment_type:

                transaction.payment_type = (
                    payment_type
                )

            # -------------------------------------
            # Update transaction information
            # -------------------------------------

            if transaction_id:

                transaction.payment_id = (
                    transaction_id
                )

            transaction.status = "SUCCESS"
            transaction.cash_status = "success"

            transaction.save()

            print(
                "BICTORYS PAYMENT SUCCESS:",
                {
                    "payment_reference":
                        payment_reference,
                    "transaction_id":
                        transaction_id,
                    "payment_type":
                        payment_type,
                    "amount":
                        webhook_amount,
                    "currency":
                        webhook_currency
                }
            )

            # -------------------------------------
            # TODO:
            #
            # If transaction.order is available,
            # update the actual order here.
            #
            # Example:
            #
            # order = transaction.order
            # order.payment_status = "PAID"
            # order.status = "CONFIRMED"
            # order.save()
            #
            # -------------------------------------

            return JsonResponse(
                {
                    "success": True,
                    "message":
                        "Payment webhook processed",
                    "status":
                        "SUCCESS"
                },
                status=200
            )

        # -----------------------------------------
        # Failed / cancelled payment
        # -----------------------------------------

        if status in [
            "failed",
            "cancelled",
            "canceled",
            "declined",
            "expired"
        ]:

            transaction.status = "FAILED"
            transaction.cash_status = "failed"

            if payment_type:

                transaction.payment_type = (
                    payment_type
                )

            if transaction_id:

                transaction.payment_id = (
                    transaction_id
                )

            transaction.save()

            print(
                "BICTORYS PAYMENT FAILED:",
                {
                    "payment_reference":
                        payment_reference,
                    "transaction_id":
                        transaction_id,
                    "status":
                        status
                }
            )

            return JsonResponse(
                {
                    "success": True,
                    "message":
                        "Payment failure webhook processed",
                    "status":
                        "FAILED"
                },
                status=200
            )

        # -----------------------------------------
        # Pending / other status
        # -----------------------------------------

        transaction.status = "PENDING"

        if payment_type:

            transaction.payment_type = (
                payment_type
            )

        if transaction_id:

            transaction.payment_id = (
                transaction_id
            )

        transaction.save()

        print(
            "BICTORYS PAYMENT STATUS:",
            {
                "payment_reference":
                    payment_reference,
                "status":
                    status
            }
        )

        return JsonResponse(
            {
                "success": True,
                "message":
                    "Webhook received",
                "status":
                    status
            },
            status=200
        )

    # ---------------------------------------------
    # Generic exception
    # ---------------------------------------------

    except Exception as e:

        print(
            "BICTORYS WEBHOOK ERROR:",
            str(e)
        )

        return JsonResponse(
            {
                "success": False,
                "error":
                    "Webhook processing failed",
                "details":
                    str(e)
            },
            status=500
        )



class ShipsGoClient:

    BASE_URL = "https://api.shipsgo.com/v2"

    @staticmethod
    def get_container_status(container_number):

        try:
            url = f"{ShipsGoClient.BASE_URL}/ocean/shipments"

            headers = {
                "X-Shipsgo-User-Token": settings.SHIPSGO_API_KEY,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )

            # Raise exception for 4xx / 5xx
            response.raise_for_status()

            result = response.json()

            # Get shipments from ShipsGo response
            shipments = result.get("shipments", [])

            # Exact container number matching
            matched_shipments = []

            for shipment in shipments:

                shipsgo_container_number = shipment.get(
                    "container_number"
                )

                if (
                    shipsgo_container_number
                    and shipsgo_container_number.upper()
                    == container_number.upper()
                ):
                    matched_shipments.append(shipment)

            # Container not found
            if not matched_shipments:

                return {
                    "success": False,
                    "message": "Container not found",
                    "container_number": container_number,
                    "shipment": None
                }

            # First matching shipment
            shipment = matched_shipments[0]
            print(shipment, 'shipment', flush=True)
            # Extract route information
            route = shipment.get("route", {})

            port_of_loading = route.get(
                "port_of_loading", {}
            )

            port_of_discharge = route.get(
                "port_of_discharge", {}
            )

            loading_location = port_of_loading.get(
                "location", {}
            )

            discharge_location = port_of_discharge.get(
                "location", {}
            )

            # Return simplified response
            return {
                "success": True,
                "message": "Container found",

                "container_number": shipment.get(
                    "container_number"
                ),

                "status": shipment.get(
                    "status"
                ),

                "shipment": {
                    "id": shipment.get("id"),

                    "reference": shipment.get(
                        "reference"
                    ),

                    "booking_number": shipment.get(
                        "booking_number"
                    ),

                    "container_number": shipment.get(
                        "container_number"
                    ),

                    "container_count": shipment.get(
                        "container_count"
                    ),

                    "carrier": shipment.get(
                        "carrier"
                    ),

                    "status": shipment.get(
                        "status"
                    ),

                    "port_of_loading": {
                        "code": loading_location.get(
                            "code"
                        ),
                        "name": loading_location.get(
                            "name"
                        ),
                        "country": loading_location.get(
                            "country"
                        ),
                        "date_of_loading":
                            port_of_loading.get(
                                "date_of_loading"
                            )
                    },

                    "port_of_discharge": {
                        "code": discharge_location.get(
                            "code"
                        ),
                        "name": discharge_location.get(
                            "name"
                        ),
                        "country": discharge_location.get(
                            "country"
                        ),
                        "date_of_discharge":
                            port_of_discharge.get(
                                "date_of_discharge"
                            ),
                        "date_of_discharge_predicted":
                            port_of_discharge.get(
                                "date_of_discharge_predicted"
                            )
                    },

                    "transit_time": route.get(
                        "transit_time"
                    ),

                    "transit_percentage": route.get(
                        "transit_percentage"
                    ),

                    "co2_emission": route.get(
                        "co2_emission"
                    ),

                    "created_at": shipment.get(
                        "created_at"
                    ),

                    "updated_at": shipment.get(
                        "updated_at"
                    ),

                    "checked_at": shipment.get(
                        "checked_at"
                    )
                }
            }

        except requests.exceptions.Timeout:

            return {
                "success": False,
                "message": "ShipsGo API request timed out"
            }

        except requests.exceptions.HTTPError as e:

            return {
                "success": False,
                "message": "ShipsGo API returned an error",
                "error": str(e)
            }

        except requests.exceptions.RequestException as e:

            return {
                "success": False,
                "message": "Unable to connect to ShipsGo",
                "error": str(e)
            }

        except Exception as e:

            return {
                "success": False,
                "message": "Something went wrong",
                "error": str(e)
            }




@csrf_exempt
def container_status_view(request):

    # Only allow POST
    if request.method != "POST":

        res = {
            "data": {
                "success": False,
                "message": "Only POST method is allowed"
            }
        }

        return HttpResponse(
            JSONRenderer().render(res),
            content_type="application/json",
            status=405
        )

    try:

        # Parse request body
        python_data = JSONParser().parse(
            io.BytesIO(request.body)
        )

        # Get container number
        container_id = python_data.get(
            "container_id"
        )

        # Validate container number
        if not container_id:

            res = {
                "data": {
                    "success": False,
                    "message": "container_id is required"
                }
            }

            return HttpResponse(
                JSONRenderer().render(res),
                content_type="application/json",
                status=400
            )

        # Remove spaces
        container_id = container_id.strip()

        # Call ShipsGo
        result = ShipsGoClient.get_container_status(
            container_id
        )

        # Return response
        res = {
            "data": result
        }

        return HttpResponse(
            JSONRenderer().render(res),
            content_type="application/json",
            status=200
        )

    except Exception as e:

        res = {
            "data": {
                "success": False,
                "message": "Invalid request",
                "error": str(e)
            }
        }

        return HttpResponse(
            JSONRenderer().render(res),
            content_type="application/json",
            status=400
        )



# @csrf_exempt
# def container_status_view(request):

#     python_data = JSONParser().parse(
#         io.BytesIO(request.body)
#     )

#     container_number = python_data.get("container_number")

#     if not container_number:
#         res = {
#             "success": False,
#             "message": "container_number is required"
#         }

#         return HttpResponse(
#             JSONRenderer().render(res),
#             content_type="application/json",
#             status=400
#         )

#     result = ShipsGoClient.get_container_status(
#         container_number
#     )

#     res = {
#         "data": result
#     }

#     return HttpResponse(
#         JSONRenderer().render(res),
#         content_type="application/json",
#         status=200
#     )




@csrf_exempt
def initiate_bictorys_payment_for_inquiry(request):
 
    try:
 
        # -----------------------------------------
        # Validate request method
        # -----------------------------------------
 
        if request.method != "POST":
 
            return HttpResponse(
                JSONRenderer().render({
                    "success": False,
                    "error": "POST method required"
                }),
                content_type="application/json",
                status=405
            )
 
        # -----------------------------------------
        # Parse request
        # -----------------------------------------
 
        try:
 
            python_data = JSONParser().parse(
                io.BytesIO(request.body)
            )
 
        except Exception as e:
 
            return HttpResponse(
                JSONRenderer().render({
                    "success": False,
                    "error": "Invalid JSON payload",
                    "details": str(e)
                }),
                content_type="application/json",
                status=400
            )
 
        amount = python_data.get("amount")
 
        if amount is None:
 
            return HttpResponse(
                JSONRenderer().render({
                    "success": False,
                    "error": "Amount is required"
                }),
                content_type="application/json",
                status=400
            )
 
        # -----------------------------------------
        # Validate amount
        # -----------------------------------------
 
        try:
 
            amount = float(amount)
 
        except (ValueError, TypeError):
 
            return HttpResponse(
                JSONRenderer().render({
                    "success": False,
                    "error": "Invalid amount"
                }),
                content_type="application/json",
                status=400
            )
 
        if amount <= 0:
 
            return HttpResponse(
                JSONRenderer().render({
                    "success": False,
                    "error": "Amount must be greater than zero"
                }),
                content_type="application/json",
                status=400
            )
 
        # -----------------------------------------
        # Generate payment reference
        # -----------------------------------------
 
        payment_reference = (
            f"BICT-"
            f"{uuid.uuid4().hex[:12].upper()}"
        )
 
        # Example:
        # BICT-83CD18D2A728
 
        # -----------------------------------------
        # Bictorys API
        # -----------------------------------------
 
        url = (
            f"{settings.BICTORYS_API_URL}"
            f"/pay/v1/charges"
        )
 
        # IMPORTANT:
        # Do NOT send payment_type here.
        #
        # Without payment_type, Bictorys Checkout
        # allows the customer to select the available
        # payment method from the hosted checkout page.
        #
        # Examples:
        # - Card
        # - Mobile Money
        # - Wave
        # - Orange Money
        # - Other available methods
        #
        # Therefore there is intentionally NO:
        #
        # params = {
        #     "payment_type": "card"
        # }
 
        headers = {
 
            "X-Api-Key":
                settings.BICTORYS_API_KEY,
 
            "Content-Type":
                "application/json",
 
            "Accept":
                "application/json"
        }
 
        # -----------------------------------------
        # Payload
        # -----------------------------------------
 
        payload = {
 
            # "amount": amount,
            "amount": 10,
 
            "currency": "XOF",
 
            "country": "SN",
 
            "paymentReference":
                payment_reference,
 
            # Existing Diaba deep-link / App Link /
            # Universal Link URL.
            #
            # Bictorys redirects the user's browser
            # here after successful payment.
            "successRedirectUrl":
                "https://diaba.store/inquiry-success/",
 
            # Existing Diaba failure callback.
            "errorRedirectUrl":
                "https://diaba.store/inquiry-failed/"
        }
 
        print(
            "BICTORYS REQUEST:",
            payload
        )
 
        # -----------------------------------------
        # Request
        # -----------------------------------------
 
        response = requests.post(
 
            url,
 
            json=payload,
 
            headers=headers,
 
            timeout=30
        )
 
        # -----------------------------------------
        # Parse Bictorys response
        # -----------------------------------------
 
        try:
 
            data = response.json()
 
        except ValueError:
 
            data = {
                "message":
                    response.text
            }
 
        print(
            "BICTORYS RESPONSE:",
            data
        )
 
        # -----------------------------------------
        # Handle Bictorys API error
        # -----------------------------------------
 
        if response.status_code not in [
            200,
            201,
            202
        ]:
 
            return HttpResponse(
                JSONRenderer().render({
 
                    "success": False,
 
                    "error":
                        "Payment initiation failed",
 
                    "status_code":
                        response.status_code,
 
                    "details":
                        data
                }),
                content_type="application/json",
                status=response.status_code
            )
 
        # -----------------------------------------
        # Extract Checkout URL
        # -----------------------------------------
 
        payment_url = (
 
            data.get("link")
 
            or data.get("checkoutUrl")
 
            or data.get("checkout_url")
 
            or data.get("payment_url")
        )
 
        if not payment_url:
 
            return HttpResponse(
                JSONRenderer().render({
 
                    "success": False,
 
                    "error":
                        "Payment URL not received",
 
                    "details":
                        data
                }),
                content_type="application/json",
                status=502
            )
 
        # -----------------------------------------
        # Extract Bictorys transaction / charge ID
        # -----------------------------------------
 
        charge_id = (
 
            data.get("id")
 
            or data.get("transactionId")
 
            or data.get("transaction_id")
 
            or data.get("charge_id")
        )
 
        # -----------------------------------------
        # Extract charge ID from Checkout URL
        # -----------------------------------------
 
        if not charge_id:
 
            try:
 
                parsed_url = urlparse(
                    payment_url
                )
 
                query_params = parse_qs(
                    parsed_url.query
                )
 
                charge_id = (
                    query_params
                    .get(
                        "charge_id",
                        [None]
                    )[0]
                )
 
            except Exception as e:
 
                print(
                    "Charge ID extraction error:",
                    e
                )
 
        print(
            "Bictorys Charge ID:",
            charge_id
        )
 
        # -----------------------------------------
        # Create local pending transaction
        # -----------------------------------------
 
        transaction = (
            models.OrderTransaction.objects.create(
 
                order=None,
 
                customer=None,
 
                # IMPORTANT:
                # Do not store "card" here because
                # the customer has not selected a
                # payment method yet.
                #
                # Bictorys Checkout will allow the
                # customer to choose the payment method.
                payment_type="bictorys",
 
                cash_status="pending",
 
                payment_id=charge_id,
 
                reference_id=payment_reference,
 
                fee_amount="0",
 
                net_amount=str(amount),
 
                total_amount=str(amount),
 
                tax_price="0",
 
                currency="XOF",
 
                status="PENDING"
            )
        )
 
        # -----------------------------------------
        # Response to React Native
        # -----------------------------------------
 
        return HttpResponse(
            JSONRenderer().render({
 
                "success": True,
 
                "message":
                    "Payment initiated successfully",
 
                "transaction_id":
                    transaction.id,
 
                "payment_reference":
                    payment_reference,
 
                "bictorys_transaction_id":
                    charge_id,
 
                "payment_url":
                    payment_url,
 
                "amount":
                    amount,
 
                "currency":
                    "XOF",
 
                "status":
                    "PENDING"
            }),
            content_type="application/json",
            status=200
        )
 
    # ---------------------------------------------
    # Bictorys / Requests exception
    # ---------------------------------------------
 
    except requests.RequestException as e:
 
        print(
            "BICTORYS REQUEST ERROR:",
            str(e)
        )
 
        return HttpResponse(
            JSONRenderer().render({
 
                "success": False,
 
                "error":
                    "Bictorys API request failed",
 
                "details":
                    str(e)
            }),
            content_type="application/json",
            status=500
        )
 
    # ---------------------------------------------
    # Generic exception
    # ---------------------------------------------
 
    except Exception as e:
 
        print(
            "BICTORYS PAYMENT ERROR:",
            str(e)
        )
 
        return HttpResponse(
            JSONRenderer().render({
 
                "success": False,
 
                "error":
                    "Payment initiation failed",
 
                "details":
                    str(e)
            }),
            content_type="application/json",
            status=500
        )



