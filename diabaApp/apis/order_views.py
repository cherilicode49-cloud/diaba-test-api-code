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
import uuid
from diabaApp.apis.wallet_views import compute_customer_locked_balances, get_all_currency_rates, convert_to_usd, calculate_locked_values
from firebase_admin import messaging

from django.template.loader import render_to_string

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL
import  requests
from diabaApp.serializer import ProductOrderDetailOrderSerializer, OrderDetailSerializer, OrderDetailDataSerializer, \
    ProductOrderDetailSerializer, ProductReviewSerializer, VendorOrderDetailSerializer, VendorOrderTrackingSerializer, \
    WarehouseDetailSerializer, VendorOrderDataSerializer, OrderTrackingSerializer, PromocodeDetailSerializer, OrderInquiryDataSerializer
from diabaApp.utils import track_user_activity


def _handle_order_promocodes_and_commissions(order, promocodes_input, currency_name, original_total_amount, original_amount_paid, date_time=None):
    """
    Process multiple promo codes on an order:
    - Extracts list of promo codes (comma-separated or list)
    - Validates and links each to order (both order.promocode and order.promocodes M2M)
    - Records PromocodeTracking per promocode
    - Decrements remaining_promocode count
    - Calculates and records PromocodeCommissionDetail:
        * Product-wise: commission is based on that specific product's order revenue
        * Overall: commission is based on order original_amount_paid
    Returns (primary_promocode_name, primary_promocode_discount, applied_promocodes_list)
    """
    if not date_time:
        date_time = datetime.now().strftime('%Y-%m-%d, %H:%M:%S')

    raw_promo_list = []
    if isinstance(promocodes_input, list):
        for p in promocodes_input:
            if p and str(p).strip():
                raw_promo_list.append(str(p).strip())
    elif isinstance(promocodes_input, str) and promocodes_input.strip():
        for p in promocodes_input.split(','):
            if p and str(p).strip():
                raw_promo_list.append(str(p).strip())

    primary_name = None
    primary_discount = None
    applied_list = []

    if not raw_promo_list:
        return primary_name, primary_discount, applied_list

    # Map ordered products to total revenue in this order
    product_orders = models.ProductOrderDetail.objects.filter(order=order)
    product_sales_map = {}
    for po in product_orders:
        try:
            p_price = float(po.price or 0)
            p_qty = float(po.quantity or 1)
            product_sales_map[po.product_id] = product_sales_map.get(po.product_id, 0.0) + (p_price * p_qty)
        except Exception:
            pass

    seen_ids = set()
    for p_name in raw_promo_list:
        promo_obj = models.PromocodeDetail.objects.filter(promocode__iexact=p_name).first()
        if not promo_obj or promo_obj.id in seen_ids:
            continue
        seen_ids.add(promo_obj.id)

        try:
            order.promocodes.add(promo_obj)
        except Exception:
            pass

        if not order.promocode:
            order.promocode = promo_obj
            order.save(update_fields=['promocode'])

        if not primary_name:
            primary_name = promo_obj.promocode
            primary_discount = promo_obj.discount

        applied_list.append(promo_obj)

        # Decrement remaining count
        if promo_obj.remaining_promocode not in [None, '', 'null']:
            try:
                rem = int(promo_obj.remaining_promocode)
                if rem > 0:
                    promo_obj.remaining_promocode = str(rem - 1)
                    promo_obj.save(update_fields=['remaining_promocode'])
            except Exception:
                pass

        # Create PromocodeTracking
        try:
            models.PromocodeTracking.objects.create(
                order_id=order.id,
                promocode_id=promo_obj.id,
                customer_id=order.customer_id,
                created_at=date_time
            )
        except Exception as e:
            print("PromocodeTracking create error:", e)

        # Calculate and record Commission if influencer exists
        if promo_obj.influencer and promo_obj.influencer.commission:
            try:
                comm_pct = int(promo_obj.influencer.commission)
            except Exception:
                comm_pct = 0

            if comm_pct > 0:
                try:
                    clean_orig_total = float(str(original_total_amount).replace(' ', '').strip())
                except Exception:
                    clean_orig_total = 0.0

                try:
                    clean_orig_paid = float(str(original_amount_paid).replace(' ', '').strip())
                except Exception:
                    clean_orig_paid = clean_orig_total

                if promo_obj.product_id:
                    base_sales = product_sales_map.get(promo_obj.product_id, clean_orig_paid)
                else:
                    base_sales = clean_orig_paid

                if currency_name == "XOF":
                    converted_curr = "XOF"
                    converted_paid = int(base_sales)
                    converted_total = int(clean_orig_total)
                else:
                    xof_rate_row = models.CurrencyConverter.objects.filter(currency_code="XOF").values_list('system_rate', flat=True).first()
                    xof_rate = float(xof_rate_row) if xof_rate_row else 589.0
                    converted_curr = "XOF"
                    converted_total = round(float(clean_orig_total) * xof_rate)
                    converted_paid = round(float(base_sales) * xof_rate)

                total_comm = round((converted_paid * comm_pct) / 100.0)

                models.PromocodeCommissionDetail.objects.create(
                    order_id=order.id,
                    promocode_id=promo_obj.id,
                    product_id=promo_obj.product_id,
                    original_currency=currency_name,
                    original_total_amount=str(int(clean_orig_total)),
                    original_amount_paid=str(int(base_sales)),
                    converted_currency=converted_curr,
                    converted_total_amount=str(converted_total),
                    converted_amount_paid=str(converted_paid),
                    commission_percentage=str(comm_pct),
                    total_commission=str(total_comm),
                    created_at=date_time
                )

    return primary_name, primary_discount, applied_list


def process_order_wallet_redemption(order, python_data, currency_name, now):
    """
    Checks if wallet redemption was requested for an order, deducts balance from CustomerWallet,
    and logs an auditable Debit transaction in WalletTransaction.
    """
    use_wallet = python_data.get('use_wallet') or python_data.get('redeem_wallet') or python_data.get('is_wallet_redeem')
    wallet_amount_input = python_data.get('wallet_amount') or python_data.get('wallet_amount_used')
    is_requested = bool(use_wallet in [True, 'true', 'True', 1, '1'] or (wallet_amount_input and float(wallet_amount_input) > 0))

    if not is_requested or not order or not order.customer:
        return {'wallet_used': False, 'wallet_amount_used': 0.0}

    customer_wallet = models.CustomerWallet.objects.select_for_update().filter(customer=order.customer).first()
    if not customer_wallet or customer_wallet.balance <= Decimal('0.00'):
        return {'wallet_used': False, 'wallet_amount_used': 0.0}

    rates = get_all_currency_rates()
    locked_balances = compute_customer_locked_balances(order.customer, customer_wallet, rates)
    avail_in_order_curr = float(locked_balances.get(currency_name, 0.0))

    if wallet_amount_input:
        try:
            redeem_amount = min(float(wallet_amount_input), avail_in_order_curr)
        except (ValueError, TypeError):
            redeem_amount = avail_in_order_curr
    else:
        redeem_amount = avail_in_order_curr

    if redeem_amount <= 0:
        return {'wallet_used': False, 'wallet_amount_used': 0.0}

    usd_val = convert_to_usd(redeem_amount, currency_name, rates)
    wallet_rate = rates.get(customer_wallet.currency, 1.0)
    deduct_base = Decimal(str(round(usd_val * wallet_rate, 2) if customer_wallet.currency != 'USD' else round(usd_val, 2)))

    bal_before = customer_wallet.balance
    bal_after = max(Decimal('0.00'), bal_before - deduct_base)
    customer_wallet.balance = bal_after
    customer_wallet.save(update_fields=['balance', 'updated_at'])

    wtx_ref = f"WTX-ORD-{now.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
    debit_locked = calculate_locked_values(usd_val, rates)
    debit_locked[currency_name] = round(redeem_amount, 2)

    models.WalletTransaction.objects.create(
        wallet=customer_wallet,
        customer=order.customer,
        transaction_type='Debit',
        amount=Decimal(str(round(redeem_amount, 2))),
        currency=currency_name,
        balance_before=bal_before,
        balance_after=bal_after,
        source_type='Order_Redemption',
        source_id=order.order_id,
        transaction_ref=wtx_ref,
        description=f"Wallet redemption applied to Order {order.order_id} ({redeem_amount} {currency_name})",
        rates_snapshot=rates,
        locked_values=debit_locked,
        status='Success'
    )

    return {
        'wallet_used': True,
        'wallet_amount_used': redeem_amount,
        'wallet_transaction_ref': wtx_ref,
        'remaining_wallet_balance': float(customer_wallet.balance)
    }



@csrf_exempt
def order_create(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        customer  = python_data.get('customer')
        customer_address = python_data.get('customer_address')
        payment_type = python_data.get('payment_type').lower()
        payment_id = python_data.get('payment_id')
        air_shipping_price = python_data.get('air_shipping_price')
        ship_shipping_price = python_data.get('ship_shipping_price')
        express_shipping_price = python_data.get('express_shipping_price')
        
        total_price = python_data.get('total_price')
        amount = python_data.get('total_price')
        products = python_data.get('products')
        network = python_data.get("network_code") 
        currency = python_data.get("currency")
        promocode = python_data.get("promocode")
        original_total_amount = python_data.get("original_total_amount")
        original_amount_paid = python_data.get("original_amount_paid")
        discount_price = python_data.get("discount_price", 0)
        cargo = python_data.get("cargo")
        is_order_track = python_data.get("is_order_track", True)

        # -------------------------------------------------------------
        # Security Check: Prevent Payment Reference Reuse / Duplication
        # -------------------------------------------------------------
        if payment_id:
            payment_id = str(payment_id).strip()
            already_used_order = models.OrderDetail.objects.filter(payment_id=payment_id).first()
            already_used_txn = models.OrderTransaction.objects.filter(
                reference_id=payment_id,
                order__isnull=False
            ).first()
            if already_used_order or already_used_txn:
                print(f"FRAUD/REUSE BLOCKED in order_create: payment_id '{payment_id}' is already linked to an order.")
                res = {
                    "success": False,
                    "error": "This payment reference has already been used for an order.",
                    "message": "This payment reference has already been used for an order."
                }
                return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)
        
        print(python_data, 'python_datapython_data')


        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        current_date = now.strftime('%Y%m%d')
        current_date_data = datetime.strptime(current_date, '%Y%m%d').date()

        expire_at = now + timedelta(minutes=15)

        # total_price = 20

        get_customer = models.CustomerDetail.objects.get(id = customer)
        get_email = get_customer.email
        mobileNumber = get_customer.mobileNumber
        tax_price = 0
        if payment_type not in ['cash','Cash','bank','Bank','Bank Transfer','bank transfer', 'Inquiry', 'inquiry']:
            print("payment_type----0-0-0000>",payment_type)
            check_gateway = models.MoneyNetwork.objects.get(value = network)
            if check_gateway.label.startswith(('Orange Money', 'Wave')):
                if currency == 'USD':
                    price = round(float(total_price) * 1.025, 2)
                    tax_price = round(price - float(total_price), 2)
                    total_price = round(price, 2)
                else:
                    price = math.ceil(total_price * 1.025)
                    tax_price = math.ceil(price - total_price) 
                    total_price = math.ceil(price)
                result = APIDTSClient.cash_in(total_price, mobileNumber, network, currency)
                # print(result, 'result')
                if result.get('error'):
                    res={
                        'message':f'{result.get("details")}'
                    }
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
            else:
                tax_price = 0

            payment_id = result["transaction"]["id"]
            reference_id = result["transaction"]["reference_id"]
            fee_amount = result["transaction"]["fee_amount"]
            net_amount = result["transaction"]["net_amount"]
            total_amount = result["transaction"]["total_amount"]
            status = result["transaction"]["status"]
            payment_url = result["transaction"]["payment_url"]
          
        print(tax_price, 'tax_price', total_price, 'total_price')
        
        digits = "abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        random_data = ""
       
        if currency == "USD":
            currency_symbol = "$"
            currency_name = "USD"
        else:
            print("currency----->",currency)
            get_currency = models.CountryWithCurrency.objects.filter(currency_code = currency).first()
            currency_symbol = get_currency.currency_symbol 
            currency_name = currency
       
        for i in range(4) :
            random_data += digits[math.floor(random.random() * 52)]
        
        order_number = "ord-diaba-"+ current_date +'-'+ random_data

        promocodes_input = python_data.get("promocodes") or python_data.get("promocode")
        first_promo_str = (promocodes_input[0] if isinstance(promocodes_input, list) else str(promocodes_input or '')).split(',')[0].strip()
        first_promo_obj = models.PromocodeDetail.objects.filter(promocode__iexact=first_promo_str).first() if first_promo_str else None
        promocode_id = first_promo_obj.id if first_promo_obj else None

        order = models.OrderDetail.objects.create(
            customer_id = customer,
            customer_address_id = customer_address,
            order_id = order_number,
            promocode_id = promocode_id,
            cargo_id = cargo,
            payment_type = payment_type,
            payment_id = payment_id,
            order_status = 'pending',
            air_shipping_price = air_shipping_price,
            ship_shipping_price = ship_shipping_price,
            express_shipping_price = express_shipping_price,
            currency = currency_symbol,
            currency_name = currency_name,
            original_total_amount = original_total_amount,
            original_amount_paid = original_amount_paid,
            discount_price = discount_price,
            total_price = total_price,
            tax_price = tax_price,
            # created_at = date_time,
            expire_at = expire_at,
            status = 'pending',
            is_order_track = is_order_track
        )
        order.save()
        customer_mobile = order.customer.mobileNumber
        # print(customer_mobile, 'customer_mobile')

        order_id = order.id

        # Process Wallet Balance Redemption if applied
        wallet_result = process_order_wallet_redemption(order, python_data, currency_name, now)

        # Determine payment gateway
        detected_gateway = python_data.get('payment_gateway') or python_data.get('gateway') or network or payment_type

        # Track user activity for payment method, gateway, and order creation
        track_user_activity(
            action_type='ORDER_PLACED',
            customer_id=customer,
            payment_method=payment_type,
            payment_gateway=str(detected_gateway),
            metadata={
                'order_id': order.id,
                'order_number': order_number,
                'total_price': float(total_price) if total_price else 0,
                'currency': str(currency_symbol),
                'payment_gateway': str(detected_gateway)
            },
            ip_address=request.META.get('REMOTE_ADDR')
        )
        track_user_activity(
            action_type='PAYMENT_METHOD_SELECT',
            customer_id=customer,
            payment_method=payment_type,
            payment_gateway=str(detected_gateway),
            metadata={
                'order_number': order_number,
                'payment_gateway': str(detected_gateway)
            },
            ip_address=request.META.get('REMOTE_ADDR')
        )


        for product in products:

            print("product---->",product)
            shipping_via = product.get('shipping_via')
            variant = product.get('variant')
            quantity = int(product.get('quantity'))
            price = float(product.get('price'))
            product_shipping_price = float(product.get('product_shipping_price', None))
            if product_shipping_price != None:
                product_shipping_price = float(product_shipping_price)
            # print(variant, 'variantvariantvariant')
            total_price = quantity * price
            # check_cart = models.CartDetail.objects.filter(customer = customer, variant = variant, quantity = quantity).count()
            # if check_cart == 1:
            #     cart_data = models.CartDetail.objects.get(customer = customer, variant = variant, quantity = quantity)
            #     cart_data.delete()
                

            variant_data = models.ProductModelVariant.objects.get(id = variant)
            # print("variant_data---->",variant_data)
            # print("variant_data.product---->",variant_data.product)
            # print("variant_data.product.id---->",variant_data.product.id)
            product_id = variant_data.model.product.id

            create_order = models.ProductOrderDetail.objects.create(
                order_id = order_id,
                product_id = product_id,
                variant_id = variant_data.id,
                quantity = quantity,
                price = price,
                total_price = total_price,
                currency = currency_symbol,
                currency_name = currency_name,
                product_shipping_price = product_shipping_price,
                vendor_status = "pending",
                status = 'pending',
                # created_at = now,
                shipping_via = shipping_via
            )
            create_order.save()
            product_variant = create_order.id
            create_tracking = models.OrderTracking.objects.create(
                order_id = order_id,
                variant_id = product_variant,
                status = "pending",
                created_at  = date_time
            ).save()

            create_vendor_tracking = models.VendorOrderTracking.objects.create(
                order_id = order_id,
                variant_id = product_variant,
                status = "pending",
                created_at  = date_time
            ).save()

        
        ## for the testing purpose we take 1 XOF
        # amount = float(total_price) + float(shipping_price)
        
        ### payment Gateway
        if payment_type not in ['cash','Cash','bank','Bank','Bank Transfer','bank transfer', 'Inquiry', 'inquiry']:
            phone = customer_mobile
            network = python_data.get("network_code")  
            currency = python_data.get("currency")
           

            create_transaction = models.OrderTransaction.objects.create(
                order_id  = order_id,
                customer_id = customer,
                currency= currency_name,
                payment_type = payment_type,
                payment_id = payment_id,
                reference_id = reference_id,
                fee_amount = fee_amount,
                net_amount = net_amount,
                total_amount = total_amount,
                tax_price = tax_price,
                status = status,
                created_at = date_time,
            ).save()
            order.payment_id = payment_id
            order.save()

            
        else:
            # print('Check ', 'asfasf')
            payment_id = "cash-" + current_date +'-'+ random_data
            reference_id = None
            fee_amount = None
            net_amount = None
            total_amount = amount
            status = 'pending'
            payment_url = None
            
            if payment_type not in ['Inquiry', 'inquiry']:

                create_transaction = models.OrderTransaction.objects.create(
                    order_id  = order_id,
                    customer_id = customer,
                    currency= currency_name,
                    payment_type = payment_type,
                    payment_id = payment_id,
                    reference_id = reference_id,
                    fee_amount = fee_amount,
                    net_amount = net_amount,
                    cash_status = False,
                    tax_price = tax_price, 
                    total_amount = total_amount,
                    status = status,
                    created_at = date_time,
                )

            cart_data = models.CartDetail.objects.filter(customer = customer)
            cart_data.delete()
            
        promocode_name, promocode_discount, applied_promos = _handle_order_promocodes_and_commissions(
            order=order,
            promocodes_input=promocodes_input,
            currency_name=currency_name,
            original_total_amount=original_total_amount,
            original_amount_paid=original_amount_paid,
            date_time=date_time
        )

        # order_list_product
        order_data = models.ProductOrderDetail.objects.filter(order_id = order_id)
        order_list_product = ProductOrderDetailOrderSerializer(order_data,many=True).data

        user = get_customer.name
        # get_address = models.CustomerAddressDetail.objects.get(id = customer_address)
        # street_address = get_address.street_address
        # city = get_address.city
        # country = get_address.country
        
        try:
            if not discount_price or int(str(discount_price).replace(' ', '').strip()) == 0:
                discount_price = None
        except (ValueError, TypeError):
            discount_price = None
        # print("STARTING OF EMAIL.......", discount_price)
        
        context = {
            'user': user, 
            'order_id': order_number,
            'date': date_time,
            'customer_name': user,
            # 'street_address' : street_address,
            # 'city' : city,
            # 'country' : country,
            'order_list_product' : order_list_product,
            'subtotal': original_total_amount,
            'discount_price': discount_price,
            'promocode_name':promocode_name,
            'promocode_discount':promocode_discount,
            'ship_shipping_price': ship_shipping_price,
            'air_shipping_price': air_shipping_price,
            'express_shipping_price':express_shipping_price,
            'total_price':amount,
            'currency_name':currency_name,
            'payment_type':payment_type,
            'customer_id':get_customer.id,
            'order_id':order_id,
            'get_email':get_email
        }

        if payment_type  in ['cash','Cash','bank','Bank','Bank Transfer','bank transfer']:
        
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
        
            if payment_type in ['bank','Bank','Bank Transfer','bank transfer']:
                print("BANK in hererer")
                bank_id = python_data.get('bank_id')
                print("bank_id--------->",bank_id)
                get_bank_details = models.CountryWiseBankDetail.objects.filter(id = bank_id).first()
                if get_bank_details:
                    print("get_bank_details=====>",get_bank_details)
                    holder_name = get_bank_details.holder_name
                    bank_name = get_bank_details.bank_name
                    account_number = get_bank_details.account_number
                    branch_name = get_bank_details.branch_name
                    branch_code = get_bank_details.branch_code
                    
                    models.OrderPaymentReceivingBankDetail.objects.create(
                        order_id = order.id,
                        holder_name = holder_name,
                        bank_name = bank_name,
                        account_number = account_number,
                        branch_name = branch_name,
                        branch_code = branch_code,
                    )
        if payment_type in ['Inquiry', 'inquiry']:
            payment_type = 'cash'

        res={
            'message':"Order Create Successfully.",
            'payment_type':payment_type,
            'payment_url':payment_url,
            'txn_id':reference_id,
            'context':context,
            'wallet_used': wallet_result.get('wallet_used', False),
            'wallet_amount_used': wallet_result.get('wallet_amount_used', 0.0),
            'wallet_data': wallet_result
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def order_create_wave_orange(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        customer  = python_data.get('customer')
        customer_address = python_data.get('customer_address')
        payment_type = python_data.get('payment_type').lower()
        payment_id = python_data.get('payment_id')
        air_shipping_price = python_data.get('air_shipping_price')
        ship_shipping_price = python_data.get('ship_shipping_price')
        express_shipping_price = python_data.get('express_shipping_price')
        
        total_price = python_data.get('total_price')
        amount = python_data.get('total_price')
        products = python_data.get('products')
        network = python_data.get("network_code") 
        currency = python_data.get("currency")
        promocode = python_data.get("promocode")
        original_total_amount = python_data.get("original_total_amount")
        original_amount_paid = python_data.get("original_amount_paid")
        discount_price = python_data.get("discount_price", 0)
        cargo = python_data.get("cargo")
        reference_id = python_data.get("reference_id")
        is_order_track = python_data.get("is_order_track", True)

        # -------------------------------------------------------------
        # Security Check: Prevent Payment Reference Reuse / Duplication
        # -------------------------------------------------------------
        if reference_id:
            reference_id = str(reference_id).strip()
            already_used_order = models.OrderDetail.objects.filter(payment_id=reference_id).first()
            already_used_txn = models.OrderTransaction.objects.filter(
                reference_id=reference_id,
                order__isnull=False
            ).first()

            if already_used_order or already_used_txn:
                print(f"FRAUD/REUSE BLOCKED: reference_id '{reference_id}' is already linked to an order.")
                res = {
                    "success": False,
                    "error": "This payment reference has already been used for an order.",
                    "message": "This payment reference has already been used for an order."
                }
                return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)
        
        print(python_data, 'python_datapython_data')


        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        current_date = now.strftime('%Y%m%d')
        current_date_data = datetime.strptime(current_date, '%Y%m%d').date()

        expire_at = now + timedelta(minutes=15)

        # total_price = 20

        get_customer = models.CustomerDetail.objects.get(id = customer)
        get_email = get_customer.email
        mobileNumber = get_customer.mobileNumber
        tax_price = 0
        # if payment_type not in ['cash','Cash','bank','Bank','Bank Transfer','bank transfer']:
        #     print("payment_type----0-0-0000>",payment_type)
        #     check_gateway = models.MoneyNetwork.objects.get(value = network)
        #     if check_gateway.label.startswith(('Orange Money', 'Wave')):
        #         price = math.ceil(total_price * 1.015)
        #         tax_price = math.ceil(price - total_price) 
        #         total_price = math.ceil(price)
        #         result = APIDTSClient.cash_in(total_price, mobileNumber, network, currency)
        #         # print(result, 'result')
        #         if result.get('error'):
        #             res={
        #                 'message':f'{result.get("details")}'
        #             }
        #             return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
        #     else:
        #         tax_price = 0

        #     payment_id = result["transaction"]["id"]
        #     reference_id = result["transaction"]["reference_id"]
        #     fee_amount = result["transaction"]["fee_amount"]
        #     net_amount = result["transaction"]["net_amount"]
        #     total_amount = result["transaction"]["total_amount"]
        #     status = result["transaction"]["status"]
        #     payment_url = result["transaction"]["payment_url"]
          
        # print(tax_price, 'tax_price', total_price, 'total_price')
        fee_amount = None
        net_amount = None
        payment_url = None
        payment_id = reference_id

        digits = "abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        random_data = ""
       
        if currency == "USD":
            currency_symbol = "$"
            currency_name = "USD"
        else:
            get_currency = models.CountryWithCurrency.objects.filter(currency_code = currency).first()
            currency_symbol = get_currency.currency_symbol 
            currency_name = currency
       
        for i in range(4) :
            random_data += digits[math.floor(random.random() * 52)]
        
        order_number = "ord-diaba-"+ current_date +'-'+ random_data

        promocodes_input = python_data.get("promocodes") or python_data.get("promocode")
        first_promo_str = (promocodes_input[0] if isinstance(promocodes_input, list) else str(promocodes_input or '')).split(',')[0].strip()
        first_promo_obj = models.PromocodeDetail.objects.filter(promocode__iexact=first_promo_str).first() if first_promo_str else None
        promocode_id = first_promo_obj.id if first_promo_obj else None

        order = models.OrderDetail.objects.create(
            customer_id = customer,
            customer_address_id = customer_address,
            order_id = order_number,
            promocode_id = promocode_id,
            cargo_id = cargo,
            payment_type = payment_type,
            payment_id = payment_id,
            order_status = 'pending',
            air_shipping_price = air_shipping_price,
            ship_shipping_price = ship_shipping_price,
            express_shipping_price = express_shipping_price,
            currency = currency_symbol,
            currency_name = currency_name,
            original_total_amount = original_total_amount,
            original_amount_paid = original_amount_paid,
            discount_price = discount_price,
            total_price = total_price,
            tax_price = tax_price,
            # created_at = date_time,
            expire_at = expire_at,
            status = 'completed',
            is_order_track = is_order_track
        )
        order.save()
        customer_mobile = order.customer.mobileNumber
        # print(customer_mobile, 'customer_mobile')

        order_id = order.id

        # Process Wallet Balance Redemption if applied
        wallet_result = process_order_wallet_redemption(order, python_data, currency_name, now)

        # Determine payment gateway for Wave / Orange Money
        detected_gateway = python_data.get('payment_gateway') or python_data.get('gateway') or network or 'Wave/Orange Money'

        # Track user activity for payment method, gateway, and order creation
        track_user_activity(
            action_type='ORDER_PLACED',
            customer_id=customer,
            payment_method=payment_type,
            payment_gateway=str(detected_gateway),
            metadata={
                'order_id': order.id,
                'order_number': order_number,
                'total_price': float(total_price) if total_price else 0,
                'currency': str(currency_symbol),
                'payment_gateway': str(detected_gateway),
                'api': 'order_create_wave_orange'
            },
            ip_address=request.META.get('REMOTE_ADDR')
        )
        track_user_activity(
            action_type='PAYMENT_METHOD_SELECT',
            customer_id=customer,
            payment_method=payment_type,
            payment_gateway=str(detected_gateway),
            metadata={
                'order_number': order_number,
                'payment_gateway': str(detected_gateway),
                'api': 'order_create_wave_orange'
            },
            ip_address=request.META.get('REMOTE_ADDR')
        )

        for product in products:

            print("product---->",product)
            shipping_via = product.get('shipping_via')
            variant = product.get('variant')
            quantity = int(product.get('quantity'))
            price = float(product.get('price'))
            product_shipping_price = float(product.get('product_shipping_price', None))
            if product_shipping_price != None:
                product_shipping_price = float(product_shipping_price)
            total_price = quantity * price
                

            variant_data = models.ProductModelVariant.objects.get(id = variant)
            product_id = variant_data.model.product.id

            create_order = models.ProductOrderDetail.objects.create(
                order_id = order_id,
                product_id = product_id,
                variant_id = variant_data.id,
                quantity = quantity,
                price = price,
                total_price = total_price,
                currency = currency_symbol,
                currency_name = currency_name,
                product_shipping_price = product_shipping_price,
                vendor_status = "pending",
                status = 'pending',
                # created_at = now,
                shipping_via = shipping_via
            )
            create_order.save()
            product_variant = create_order.id
            create_tracking = models.OrderTracking.objects.create(
                order_id = order_id,
                variant_id = product_variant,
                status = "pending",
                created_at  = date_time
            ).save()

            create_vendor_tracking = models.VendorOrderTracking.objects.create(
                order_id = order_id,
                variant_id = product_variant,
                status = "pending",
                created_at  = date_time
            ).save()

        
        ## for the testing purpose we take 1 XOF
        # amount = float(total_price) + float(shipping_price)
        
        ### payment Gateway
       
        phone = customer_mobile
        network = python_data.get("network_code")  
        currency = python_data.get("currency")
        

        # -------------------------------------------------------------
        # Link or create OrderTransaction
        # -------------------------------------------------------------
        existing_txn = None
        if reference_id:
            existing_txn = models.OrderTransaction.objects.filter(
                reference_id=reference_id,
                order__isnull=True
            ).order_by('-id').first()

        if existing_txn:
            existing_txn.order_id = order_id
            existing_txn.customer_id = customer
            existing_txn.currency = currency_name
            existing_txn.payment_type = payment_type
            existing_txn.payment_id = payment_id
            existing_txn.total_amount = original_total_amount
            existing_txn.tax_price = tax_price
            existing_txn.status = 'completed'
            existing_txn.cash_status = 'paid'
            existing_txn.save()
        else:
            models.OrderTransaction.objects.create(
                order_id = order_id,
                customer_id = customer,
                currency = currency_name,
                payment_type = payment_type,
                payment_id = payment_id,
                reference_id = reference_id,
                fee_amount = fee_amount,
                net_amount = net_amount,
                total_amount = original_total_amount,
                tax_price = tax_price,
                status = 'completed',
                cash_status = 'paid',
                created_at = date_time,
            )

        order.payment_id = payment_id
        order.save()

        cart_data = models.CartDetail.objects.filter(customer = customer)
        cart_data.delete()
            
        promocode_name, promocode_discount, applied_promos = _handle_order_promocodes_and_commissions(
            order=order,
            promocodes_input=promocodes_input,
            currency_name=currency_name,
            original_total_amount=original_total_amount,
            original_amount_paid=original_amount_paid,
            date_time=date_time
        )

        # order_list_product
        order_data = models.ProductOrderDetail.objects.filter(order_id = order_id)
        order_list_product = ProductOrderDetailOrderSerializer(order_data,many=True).data

        user = get_customer.name
        # get_address = models.CustomerAddressDetail.objects.get(id = customer_address)
        # street_address = get_address.street_address
        # city = get_address.city
        # country = get_address.country
        
        # if int(discount_price.replace(' ', '').strip())== 0:
        #     discount_price = None
        # print("STARTING OF EMAIL.......", discount_price)
        
        context = {
            'user': user, 
            'order_id': order_number,
            'date': date_time,
            'customer_name': user,
            # 'street_address' : street_address,
            # 'city' : city,
            # 'country' : country,
            'order_list_product' : order_list_product,
            'subtotal': original_total_amount,
            'discount_price': discount_price,
            'promocode_name':promocode_name,
            'promocode_discount':promocode_discount,
            'ship_shipping_price': ship_shipping_price,
            'air_shipping_price': air_shipping_price,
            'express_shipping_price':express_shipping_price,
            'total_price':amount,
            'currency_name':currency_name,
            'payment_type':payment_type,
            'customer_id':get_customer.id,
            'order_id':order_id,
            'get_email':get_email
        }

        if payment_type  in ['cash','Cash','bank','Bank','Bank Transfer','bank transfer']:
        
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
        
            if payment_type in ['bank','Bank','Bank Transfer','bank transfer']:
                print("BANK in hererer")
                bank_id = python_data.get('bank_id')
                print("bank_id--------->",bank_id)
                get_bank_details = models.CountryWiseBankDetail.objects.filter(id = bank_id).first()
                if get_bank_details:
                    print("get_bank_details=====>",get_bank_details)
                    holder_name = get_bank_details.holder_name
                    bank_name = get_bank_details.bank_name
                    account_number = get_bank_details.account_number
                    branch_name = get_bank_details.branch_name
                    branch_code = get_bank_details.branch_code
                    
                    models.OrderPaymentReceivingBankDetail.objects.create(
                        order_id = order.id,
                        holder_name = holder_name,
                        bank_name = bank_name,
                        account_number = account_number,
                        branch_name = branch_name,
                        branch_code = branch_code,
                    )


        res={
            'message':"Order Create Successfully.",
            'payment_type':payment_type,
            # 'payment_url':payment_url,
            'txn_id':reference_id,
            'context':context,
            'wallet_used': wallet_result.get('wallet_used', False),
            'wallet_amount_used': wallet_result.get('wallet_amount_used', 0.0),
            'wallet_data': wallet_result
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



@csrf_exempt
def inquiry_order_create(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        print("python_data--->",python_data)
        
        customer  = python_data.get('customer')
        customer_address = python_data.get('customer_address')
        payment_type = 'inquiry'
        payment_id = python_data.get('payment_id')
        air_shipping_price = python_data.get('air_shipping_price')
        ship_shipping_price = python_data.get('ship_shipping_price')
        express_shipping_price = python_data.get('express_shipping_price')
        
        total_price = python_data.get('total_price')
        amount = python_data.get('total_price')
        products = python_data.get('products')
        network = python_data.get("network_code") 
        currency = python_data.get("currency")
        promocode = python_data.get("promocode")
        original_total_amount = python_data.get("original_total_amount")
        original_amount_paid = python_data.get("original_amount_paid")
        discount_price = python_data.get("discount_price", 0)
        cargo = python_data.get("cargo")

        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        current_date = now.strftime('%Y%m%d')
        current_date_data = datetime.strptime(current_date, '%Y%m%d').date()

        expire_at = now + timedelta(minutes=15)

        print("customer_address--->",customer_address)
        # total_price = 20

        get_customer = models.CustomerDetail.objects.get(id = customer)
        get_email = get_customer.email
        mobileNumber = get_customer.mobileNumber
        tax_price = 0

        digits = "abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        random_data = ""
       
        if currency == "USD":
            currency_symbol = "$"
            currency_name = "USD"
        else:
            get_currency = models.CountryWithCurrency.objects.filter(currency_code = currency).first()
            currency_symbol = get_currency.currency_symbol 
            currency_name = currency
       
        for i in range(4) :
            random_data += digits[math.floor(random.random() * 52)]
        
        order_number = "inq-diaba-"+ current_date +'-'+ random_data

       
        order = models.OrderDetail.objects.create(
            customer_id = customer,
            customer_address_id = customer_address,
            order_id = order_number,
            cargo_id = cargo,
            payment_type = payment_type,
            payment_id = payment_id,
            order_status = 'inquiry',
            air_shipping_price = air_shipping_price,
            ship_shipping_price = ship_shipping_price,
            express_shipping_price = express_shipping_price,
            currency = currency_symbol,
            currency_name = currency_name,
            original_total_amount = original_total_amount,
            original_amount_paid = original_amount_paid,
            discount_price = discount_price,
            total_price = total_price,
            tax_price = tax_price,
            # created_at = now,
            expire_at = expire_at,
            status = 'inquiry',
        )
        order.save()
        customer_mobile = order.customer.mobileNumber
        # print(customer_mobile, 'customer_mobile')

        order_id = order.id

        # Process Wallet Balance Redemption if applied
        wallet_result = process_order_wallet_redemption(order, python_data, currency_name, now)


        for product in products:
            print("product---->",product)
            shipping_via = product.get('shipping_via')
            variant = product.get('variant')
            quantity = int(product.get('quantity'))
            price = float(product.get('price'))
            product_shipping_price = float(product.get('product_shipping_price', None))
            if product_shipping_price != None:
                product_shipping_price = float(product_shipping_price)
            total_price = quantity * price
            
            variant_data = models.ProductModelVariant.objects.get(id = variant)
            product_id = variant_data.model.product.id

            create_order = models.ProductOrderDetail.objects.create(
                order_id = order_id,
                product_id = product_id,
                variant_id = variant_data.id,
                quantity = quantity,
                price = price,
                total_price = total_price,
                currency = currency_symbol,
                currency_name = currency_name,
                product_shipping_price = product_shipping_price,
                vendor_status = "pending",
                status = 'inquiry',
                # created_at = now,
                shipping_via = shipping_via
            )
            create_order.save()
            product_variant = create_order.id
            
            # print('Check ', 'asfasf')
            payment_id = "cash-" + current_date +'-'+ random_data
            reference_id = None
            fee_amount = None
            net_amount = None
            total_amount = amount
            status = 'pending'
            payment_url = None    
        
            cart_data = models.CartDetail.objects.filter(customer = customer)
            cart_data.delete()
            
        promocodes_input = python_data.get("promocodes") or python_data.get("promocode")
        promocode_name, promocode_discount, applied_promos = _handle_order_promocodes_and_commissions(
            order=order,
            promocodes_input=promocodes_input,
            currency_name=currency_name,
            original_total_amount=original_total_amount,
            original_amount_paid=original_amount_paid,
            date_time=date_time
        )

        order_data = models.ProductOrderDetail.objects.filter(order_id = order_id)
        order_list_product = ProductOrderDetailOrderSerializer(order_data,many=True).data

        user = get_customer.name
        # get_address = models.CustomerAddressDetail.objects.get(id = customer_address)
        # street_address = get_address.street_address
        # city = get_address.city
        country = get_customer.country
        
        # if int(discount_price.replace(' ', '').strip())== 0:
        if int(str(discount_price).replace(' ', '').strip()) == 0:
    # your logic
            discount_price = None
        # print("STARTING OF EMAIL.......", discount_price)
        
        context = {
            'user': user, 
            'order_id': order_number,
            'date': date_time,
            'customer_name': user,
            # 'street_address' : street_address,
            # 'city' : city,
            'country' : country,
            'order_list_product' : order_list_product,
            'subtotal': original_total_amount,
            'discount_price': discount_price,
            'promocode_name':promocode_name,
            'promocode_discount':promocode_discount,
            'ship_shipping_price': ship_shipping_price,
            'air_shipping_price': air_shipping_price,
            'express_shipping_price':express_shipping_price,
            'total_price':amount,
            'currency_name':currency_name,
            'payment_type':payment_type,
            'customer_id':get_customer.id,
            'order_id':order_id,
            'get_email':get_email
        }

        res={
            'message':"Order inquiry created successfully.",
            'payment_type':payment_type,
            'payment_url':payment_url,
            'txn_id':reference_id,
            'context':context
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



@csrf_exempt
def all_order_list_admin(request):
    if request.method == 'POST':
        try:
            body_bytes = request.body
            if body_bytes:
                try:
                    python_data = json.loads(body_bytes)
                except Exception:
                    import re
                    cleaned = re.sub(r',\s*([\]}])', r'\1', body_bytes.decode('utf-8', errors='ignore'))
                    python_data = json.loads(cleaned)
            else:
                python_data = {}
        except Exception:
            python_data = request.POST.dict() or {}
        
        order_status = python_data.get('order_status', 'completed')
        search_key = python_data.get('search_key', "").strip()
        
        created_at_from = python_data.get('created_at_from')
        created_at_to = python_data.get('created_at_to')
        shipping_via = python_data.get('shipping_via')
        payment_type = python_data.get('payment_type')

        sort_by = python_data.get('sort_by')
        sort_order = python_data.get('sort_order')

        page_number = int(python_data.get('page_number', 1))
        row_size = int(python_data.get('row_data', 10))

        last_row = row_size * page_number
        first_row = last_row - row_size

        # print(python_data, 'python_data')
        
        if order_status == "Confirm":
            status = "completed"
            order_status = "pending"
            queryset = models.OrderDetail.objects.filter(status = status, order_status=order_status)
        elif order_status == "pending":
            queryset = models.OrderDetail.objects.filter(status = "pending", payment_type__in = ["cash","bank transfer"], order_status=order_status)
        else:
            queryset = models.OrderDetail.objects.filter(order_status=order_status)

        query_filter = Q()

        if search_key:
            if any(char in search_key for char in ["+", " "]):
                split_search_key = search_key.split() 

                # print("split_search_key----->", split_search_key)

                search_countryCode = split_search_key[0]
                search_mobileNumber = split_search_key[1]

                query_filter |= Q(customer__countryCode__icontains=search_countryCode)
                query_filter &= Q(customer__mobileNumber__icontains=search_mobileNumber)
            else:
                query_filter |= Q(customer__countryCode__icontains=search_key)
                query_filter |= Q(customer__mobileNumber__icontains=search_key)

        queryset = queryset.filter(
            Q(order_id__icontains=search_key) |
            Q(customer__name__icontains=search_key) |
            Q(customer__email__icontains=search_key) |
            query_filter
        )

        if created_at_from:
            queryset = queryset.filter(created_at__gte=created_at_from)
        if created_at_to:
            queryset = queryset.filter(created_at__lte=created_at_to)
        if shipping_via:
            if shipping_via == ['ship',"Ship","SHIP"]:
                shipping_via = "By Ship"
            elif shipping_via == ['air',"Air","AIR"]:
                shipping_via = "By Air"
            elif shipping_via == ['express',"Express","EXPRESS"]:
                shipping_via = "By Express"

            queryset = queryset.filter(productorderdetail__shipping_via__icontains=shipping_via)
        if payment_type:
            payment_options ={
                'cash': ['cash', 'Cash'],
                'bank_transfer': ['bank', 'Bank', 'Bank Transfer', 'bank transfer'],
                'wave': ['Wave', 'wave'],
                'orange_money': ['Orange Money', 'orange money'],
                'inquiry': ['inquiry'],
            }
            # print("payment_options[payment_type]---->",payment_options[payment_type])
            queryset = queryset.filter(payment_type__in=payment_options[payment_type])
        
        if sort_by:
            if sort_by in ['email', "Email"]:
                sort_by = 'customer__email'
            queryset = queryset.order_by(sort_by)
        if sort_order:
            if sort_order == 'asc':
                queryset = queryset.order_by(sort_by)
            else:
                queryset = queryset.order_by('-' + sort_by)
        else:
            queryset = queryset.order_by('-id')

        queryset = queryset.distinct()

        order_count = queryset.count()

        order_list = queryset[first_row:last_row]
                
        # order_count = models.OrderDetail.objects.filter( Q(order_id__icontains=search_key) |Q(customer__name__icontains=search_key) |Q(customer__email__icontains=search_key), order_status = order_status).count()
        # order_list = models.OrderDetail.objects.filter(Q(order_id__icontains=search_key) |Q(customer__name__icontains=search_key) |Q(customer__email__icontains=search_key), order_status = order_status).order_by('-id')[first_row:last_row]
        list_data = []
        for order in order_list:
            order = models.OrderDetail.objects.get(id = order.id)
            order_serializer = OrderDetailSerializer(order).data
            payment_count = models.OrderTransaction.objects.filter(order = order.id).count()
            if payment_count == 1:
                cash_status = models.OrderTransaction.objects.filter(order = order.id).values_list('cash_status', flat=True)[0]
                transaction_id = models.OrderTransaction.objects.filter(order = order.id).values_list('id', flat=True)[0]
            else:
                cash_status = None 
                transaction_id = None
            
            order_serializer.update({'cash_status':cash_status, 'transaction_id':transaction_id})
            list_data.append(order_serializer)
        res={
            'data':list_data,
            'order_count':order_count
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def all_order_list_admin_inquiry(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        order_status = python_data.get('order_status', 'completed')
        search_key = python_data.get('search_key', "").strip()
        page_number = int(python_data.get('page_number', 1))
        row_size = int(python_data.get('row_data', 10))
        last_row = row_size * page_number
        first_row = last_row - row_size
        print(python_data, 'python_data')
        
        if order_status == "Confirm":
            status = "completed"
            order_status = "pending"
            queryset = models.OrderDetail.objects.filter(Q(status = status)|Q(status = "pending", payment_type = "inquiry"), order_status=order_status)
        else:
            queryset = models.OrderDetail.objects.filter(order_status=order_status)

        if search_key:
            queryset = queryset.filter(
                Q(order_id__icontains=search_key) |
                Q(customer__name__icontains=search_key) |
                Q(customer__email__icontains=search_key) |
                Q(customer__mobileNumber__icontains=search_key) 
            )

        order_count = queryset.count()

        order_list = queryset.order_by('-id')[first_row:last_row]
                
        list_data = []
        for order in order_list:
            order = models.OrderDetail.objects.get(id = order.id)
            order_serializer = OrderDetailSerializer(order).data
            
            list_data.append(order_serializer)
        res={
            'data':list_data,
            'order_count':order_count,
            'total_count':order_count
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def customer_order_list(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        customer = python_data.get('customer')
        check_customer = models.CustomerDetail.objects.filter(id = customer).count()
        if check_customer == 1:

            order_list = models.OrderDetail.objects.filter(customer = customer).order_by('-id')
            list_data = []
            for order in order_list:
                order_data = models.OrderDetail.objects.get(id = order.id)
                order_serializer = OrderDetailDataSerializer(order_data).data

                list_product_data = []
                get_all_product = models.ProductOrderDetail.objects.filter(order = order.id)
                for product in get_all_product:
                    product = models.ProductOrderDetail.objects.get(id = product.id)

                    product_data = ProductOrderDetailSerializer(product).data

                    check_review = models.ProductReview.objects.filter(product = product.product).count()
                    # print(check_review, 'check_review')
                    review_data = ''
                    if check_review == 1:
                        review = models.ProductReview.objects.get(product = product.product)
                        review_data = ProductReviewSerializer(review).data
                    product_data.update({'review':review_data})
                    list_product_data.append(product_data)
                
                order_serializer.update({'product':list_product_data})

                # Track if wallet balance was used for this order
                wallet_tx = models.WalletTransaction.objects.filter(
                    source_id=order.order_id,
                    transaction_type='Debit',
                    status='Success'
                ).first()
                order_serializer['is_wallet_used'] = bool(wallet_tx)
                order_serializer['wallet_amount_used'] = float(wallet_tx.amount) if wallet_tx else 0.0
                order_serializer['wallet_currency'] = wallet_tx.currency if wallet_tx else order.currency_name
                order_serializer['wallet_transaction_ref'] = wallet_tx.transaction_ref if wallet_tx else None

                list_data.append(order_serializer)

            res={
                'data':list_data
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
                


@csrf_exempt
def vendor_order_list(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("pytohn_data-=-vendor_order_list-=--->",python_data)

        vendor = int(python_data.get('vendor'))

        list_data = []
        order_list = models.VendorOrderDetail.objects.filter(vendor = vendor).order_by('-id')
        for order in order_list:
            order = models.VendorOrderDetail.objects.get(id = order.id)
            order_data = VendorOrderDetailSerializer(order).data

            get_price = models.VendorProductPrice.objects.filter(variant = order.variant.variant, vendor = vendor).values_list('price', flat=True).first()
            quantity = order.variant.quantity
            order_data.update({'vendor_price':get_price, 'quantity':quantity, 'total_variant_price':float(get_price)*int(quantity)})
            
            list_data.append(order_data)

        res={
    
            'data':list_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

@csrf_exempt
def vendor_order_list_vendor(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')
        page_number = int(python_data.get('page_number', 1))
        row_size = int(python_data.get('row_data', 10))
        last_row = row_size * page_number
        first_row = last_row - row_size
        
        list_data = []
        total_order_count = models.VendorOrderDetail.objects.filter(vendor = vendor).count()
        order_list = models.VendorOrderDetail.objects.filter(vendor = vendor).order_by('-id')[first_row:last_row]

        for order in order_list:
            order = models.VendorOrderDetail.objects.get(id = order.id)
            order_data = VendorOrderDetailSerializer(order).data

            get_price = models.VendorProductPrice.objects.filter(variant = order.variant.variant, vendor = vendor).values_list('price', flat=True).first()
            quantity = order.variant.quantity
            order_data.update({'variant_price':get_price, 'quantity':quantity, 'total_variant_price':float(get_price)*int(quantity)})

            tracking = models.VendorOrderTracking.objects.filter(order = order.order,variant = order.variant)
            order_tracking = VendorOrderTrackingSerializer(tracking, many=True).data
            order_data.update({'order_tracking':order_tracking})

            
            if getattr(order.variant.warehouse, "id", None) and models.WarehouseDetail.objects.filter(id=order.variant.warehouse.id).exists():

                warehouse_count = models.WarehouseDetail.objects.get(id =order.variant.warehouse.id)
                warehouse_serialiser = WarehouseDetailSerializer(warehouse_count).data
                order_data.update({'warehouse_data':warehouse_serialiser})

            list_data.append(order_data)
        
        res={
    
            'data':list_data,
            'total_order_count':total_order_count
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def order_detail_admin(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        order = python_data.get('order')

        print("python_data=====>",python_data)
    
        order_data = models.OrderDetail.objects.get(id = order)
        order_serializer = OrderDetailSerializer(order_data).data
        
        get_all_product = models.ProductOrderDetail.objects.filter(order = order).order_by('-id')
        list_data = []
        for product in get_all_product:
            product = models.ProductOrderDetail.objects.get(id = product.id)
            product_data = ProductOrderDetailSerializer(product).data

            warehouse_assign = product.warehouse
            if warehouse_assign != None and warehouse_assign != 'null':
                warehouseConfirmed = True 
            else:
                warehouseConfirmed = False 


            check_vendor = models.VendorOrderDetail.objects.filter(variant = product.id).count()
            if check_vendor == 1:
                vendor = models.VendorOrderDetail.objects.get(variant = product.id)
                vendor_data = VendorOrderDataSerializer(vendor).data
                
                order_tracking = models.OrderTracking.objects.filter(variant = product.id).order_by('id')
                order_tracking_data = OrderTrackingSerializer(order_tracking, many=True).data
                vendor_order_tracking = models.VendorOrderTracking.objects.filter(variant = product.id).order_by('id')
                vendor_order_tracking_data = VendorOrderTrackingSerializer(vendor_order_tracking, many=True).data
                product_data.update({'vendorConfirmed':True, 'vendor_data':vendor_data, 'order_tracking_data':order_tracking_data, \
                'warehouseConfirmed':warehouseConfirmed, 'vendor_order_tracking_data':vendor_order_tracking_data})
            else:
                vendor_order_tracking = models.VendorOrderTracking.objects.filter(variant = product.id).order_by('id')
                vendor_order_tracking_data = VendorOrderTrackingSerializer(vendor_order_tracking, many=True).data
                order_tracking = models.OrderTracking.objects.filter(variant = product.id).order_by('id')
                order_tracking_data = OrderTrackingSerializer(order_tracking, many=True).data
                product_data.update({'vendorConfirmed':False, 'order_tracking_data':order_tracking_data, \
                'warehouseConfirmed':warehouseConfirmed, 'vendor_order_tracking_data':vendor_order_tracking_data})

            list_data.append(product_data)
        
        promocode_data = None
        promocode_list_data = []
        if order_data.promocode != None:
            all_promocode = models.PromocodeDetail.objects.get(id = order_data.promocode.id)
            promocode_data = PromocodeDetailSerializer(all_promocode).data 
        if hasattr(order_data, 'promocodes') and order_data.promocodes.exists():
            promocode_list_data = PromocodeDetailSerializer(order_data.promocodes.all(), many=True).data
        elif promocode_data:
            promocode_list_data = [promocode_data]

        # Track if wallet balance was used for this order
        wallet_tx = models.WalletTransaction.objects.filter(
            source_id=order_data.order_id,
            transaction_type='Debit',
            status='Success'
        ).first()
        order_serializer['is_wallet_used'] = bool(wallet_tx)
        order_serializer['wallet_amount_used'] = float(wallet_tx.amount) if wallet_tx else 0.0
        order_serializer['wallet_currency'] = wallet_tx.currency if wallet_tx else order_data.currency_name
        order_serializer['wallet_transaction_ref'] = wallet_tx.transaction_ref if wallet_tx else None

        wallet_info = {
            'is_wallet_used': bool(wallet_tx),
            'wallet_amount_used': float(wallet_tx.amount) if wallet_tx else 0.0,
            'wallet_currency': wallet_tx.currency if wallet_tx else order_data.currency_name,
            'wallet_transaction_ref': wallet_tx.transaction_ref if wallet_tx else None,
            'description': wallet_tx.description if wallet_tx else None,
            'created_at': wallet_tx.created_at.strftime('%Y-%m-%d %H:%M:%S') if wallet_tx and wallet_tx.created_at else None
        } if wallet_tx else {
            'is_wallet_used': False,
            'wallet_amount_used': 0.0,
            'wallet_currency': order_data.currency_name,
            'wallet_transaction_ref': None
        }

        res={
            'data':order_serializer,
            'product_data':list_data,
            'promocode_data':promocode_data,
            'promocodes':promocode_list_data,
            'wallet_data': wallet_info
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def vendor_order_assign(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=-=vendor_order_assign-=-->", python_data)

        order = python_data.get('order')
        variant = python_data.get('variant')
        vendor = python_data.get('vendor')
        warehouse = python_data.get('warehouse')
        
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        check_order = models.VendorOrderDetail.objects.filter(order = order, variant=variant).count()
        # print("ORDER -=-=-=-=-=-=-=-=-->", check_order)
        if check_order == 0:

            create_order = models.VendorOrderDetail.objects.create(
                order_id = order, 
                variant_id = variant,
                vendor_id = vendor,
                # created_at = datetime.now()
            )
            create_order.save()

            vendor_price = int(models.VendorProductPrice.objects.filter(vendor = vendor, variant = create_order.variant.variant).first().price)
            total_vendor_price = vendor_price * int(create_order.variant.quantity)

            get_product_order_detail = models.ProductOrderDetail.objects.get(id = variant)
            get_product_order_detail.vendor_price = vendor_price
            get_product_order_detail.total_vendor_price = total_vendor_price
            get_product_order_detail.save()

            # product_update = models.ProductOrderDetail.objects.get(id = variant)
            # product_update.warehouse_id = warehouse
            # product_update.save()

            
            # order_tracking = models.OrderTracking.objects.create(
            #     order_id = order,
            #     variant_id = variant,
            #     status = "Processing",
            #     created_at  = date_time
            # ).save()

            get_vendor_variant = models.VendorProductPrice.objects.filter(variant = create_order.variant.variant.id, vendor = vendor).first()
            remarks = str(create_order.variant.product.product_name)+" X "+str(create_order.variant.quantity)

            # transaction_create = models.VendorTransaction.objects.create(
            #     vendor_id = vendor,
            #     currency = "CFA",
            #     amount = float(get_vendor_variant.price) * int(create_order.variant.quantity),
            #     transaction_type = "pending",
            #     remarks = remarks,
            #     created_at = datetime.now(),
            #     status = "pending",
            # )


            vendor_detail = models.VendorDetail.objects.get(id = vendor)
            previous_remaining_amount = models.VendorPaymentTracker.objects.filter(vendor = vendor).order_by('-id').values_list('remaining_amount', flat=True).first()
            
            vendor_name = vendor_detail.vendor_name
            vendor_email = vendor_detail.email
            vendor_mobile = vendor_detail.phone_number
            payment_type = "Pay"
            # currency = "CFA"
            amount = Decimal(str(float(get_vendor_variant.price) * int(create_order.variant.quantity)))
            remaining_amount = amount if previous_remaining_amount is None else previous_remaining_amount + amount
            description = remarks


            create_payment = models.VendorPaymentTracker.objects.create(
                vendor_id = vendor,
                vendor_name = vendor_name,
                vendor_email = vendor_email,
                vendor_mobile = vendor_mobile,
                payment_type = payment_type,
                currency = "XOF",
                amount = amount,
                remaining_amount = remaining_amount,
                description = description,
                created_at = datetime.now(),
            ).save()
            
            
            
            res={
        
                'message':"Order send to Vendor, they'll accept soon."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={       
                'message':"This order already send to Vendor."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)



@csrf_exempt
def warehouse_order_assign(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        variant = python_data.get('variant')
        warehouse = python_data.get('warehouse')

        product_update = models.ProductOrderDetail.objects.get(id = variant)
        product_update.warehouse_id = warehouse
        product_update.save()

        res={
        
            'message':"Warehouse Added successfully."
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)




@csrf_exempt
def cash_status_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        transaction  = python_data.get('transaction')
        print(python_data, 'python_data')

        if python_data.get('cash_status') == 'True':

            order = models.OrderTransaction.objects.get(id = transaction)
            order.cash_status = python_data.get('cash_status', order.cash_status)
            order.status = "completed"
            order.save()
            print(123)

            get_order = models.OrderDetail.objects.get(id = order.order.id)
            get_order.status = "completed"
            get_order.save()

        res={
            'message':"Status Update successfully."
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

    
@csrf_exempt
def order_status_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        order = python_data.get('order')
        status = python_data.get('status')
        
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        # print(python_data, 'python_data')
        check_order = models.OrderDetail.objects.filter(id = order).count()
        if check_order == 1:
            # print('dafadg 1122')
            order_status = models.OrderDetail.objects.get(id = order)
            order_status.order_status = status
            order_status.save()
            
            res={
                'message':"Status update successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':"This status already used."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)


@csrf_exempt
def variant_order_status_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        order = python_data.get('order')
        variant = python_data.get('variant')
        status = python_data.get('status')
        # print(python_data, 'python_datapython_data')
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        status_check = models.OrderTracking.objects.filter(order = order,variant = variant,status = status).count()
        if status_check == 0:
            # get_variant_id = models.ProductOrderDetail.objects.filter(order = order,variant = variant).values_list('id', flat=True)[0]
            get_variant = models.ProductOrderDetail.objects.get(id = variant)
            get_variant.status = status
            get_variant.save()

            status_create = models.OrderTracking.objects.create(
                order_id = order,
                variant_id = variant,
                status = status,
                created_at = date_time
            )
            status_create.save()

            token = status_create.order.customer.FCMToken
            product_name = status_create.variant.product.product_name
            prod_img = str(status_create.variant.product.product_image_1 or "")
            product_image = prod_img if prod_img.startswith(("http://", "https://")) else (IMAGE_URL + prod_img)
            # print(product_image, 'product_image')
            # product_name = full_name[:15] + "..." if len(full_name) > 15 else full_name
            title = 'Order Status Updated'
            body = f'Your {product_name} order is now {status}.'
            
            try:
                # print('Test')
                message = messaging.Message(
                notification=messaging.Notification(
                        title=title,
                        body=body,
                        image = product_image
                    ),
                    data={
                        'notification_type':'order',
                    },
                    token=token
                    # tokens=token_chunk,
                )
                try:
                    response = messaging.send(message)

                    print("Notification Sent Successfully")

                   
                except Exception as e:
                    print(f"An error occurred while sending multicast message: {e}")
            except Exception as e:
                print('Error---->',e)


            res={
                'message':"Status update successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':"This status already used."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)

@csrf_exempt
def vendor_variant_order_status_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        order = python_data.get('order')
        variant = python_data.get('variant')
        vendor_status = python_data.get('vendor_status')
        # print(python_data, 'python_datapython_data')
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        status_check = models.VendorOrderTracking.objects.filter(order = order,variant = variant,status = vendor_status).count()
        if status_check == 0:
            # get_variant_id = models.ProductOrderDetail.objects.filter(order = order,variant = variant).values_list('id', flat=True)[0]
            get_variant = models.ProductOrderDetail.objects.get(id = variant)
            get_variant.vendor_status = vendor_status
            get_variant.save()

            status_create = models.VendorOrderTracking.objects.create(
                order_id = order,
                variant_id = variant,
                status = vendor_status,
                created_at = date_time
            ).save()
            res={
                'message':"Status update successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':"This status already used."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)


@csrf_exempt
def order_delete_admin(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        order_id = python_data.get('id')
        
        check_order = models.OrderDetail.objects.filter(id=order_id)
        if check_order.exists():
            order_obj = check_order.first()
            order_obj.is_deleted = True
            order_obj.deleted_at = datetime.now()
            order_obj.order_status = 'cancelled'
            order_obj.save()

            # Mark order tracking status
            models.OrderTracking.objects.filter(order=order_id).update(status="cancelled")

            res = {
                'status': True,
                'message': "Order Soft Deleted Successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        else:
            res = {
                'status': False,
                'message': "Order not found."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 404)


    
@csrf_exempt
def product_order_list(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        product = python_data.get('product')

        check_product = models.ProductDetail.objects.filter(id = product).count()
        if check_product == 1:
            list_data = []
            get_all_order = models.ProductOrderDetail.objects.filter(product = product)
            for order in get_all_order:
                order = models.ProductOrderDetail.objects.get(id = order.id)
                order_data = ProductOrderDetailSerializer(order).data

                vendor_check = models.VendorOrderDetail.objects.filter(variant = order.id).count()
                if vendor_check == 1:
                    vendor = models.VendorOrderDetail.objects.get(variant = order.id)
                    vendor_data = VendorOrderDataSerializer(vendor).data
                    order_data.update({'vendor_data':vendor_data, 'vendor_assign':True})
                    list_data.append(order_data)
                else:
                    order_data.update({'vendor_assign':False})
                    list_data.append(order_data)

            res={
                'data':list_data
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':'Enter valid Product ID.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)

@csrf_exempt
def all_order_inquiry_list_app(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        customer = python_data.get('customer')

        order_list = models.OrderDetail.objects.filter(customer = customer, payment_type = "inquiry",status = "inquiry").order_by('-id')
        order_count = order_list.count()

        list_data = []
        for order in order_list:
            order_data = models.OrderDetail.objects.get(id = order.id)
            order_serializer = OrderInquiryDataSerializer(order_data).data

            list_product_data = []
            get_all_product = models.ProductOrderDetail.objects.filter(order = order.id)
            for product in get_all_product:
                product = models.ProductOrderDetail.objects.get(id = product.id)

                product_data = ProductOrderDetailSerializer(product).data

                check_review = models.ProductReview.objects.filter(product = product.product).count()
                # print(check_review, 'check_review')
                review_data = ''
                if check_review == 1:
                    review = models.ProductReview.objects.get(product = product.product)
                    review_data = ProductReviewSerializer(review).data
                product_data.update({'review':review_data})
                list_product_data.append(product_data)
            
            order_serializer.update({'product':list_product_data})
            list_data.append(order_serializer)
            
        res={
            'data':list_data,
            'order_count':order_count
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



@csrf_exempt
def container_added_in_order(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        id = python_data.get('id')
        container_id = python_data.get('container_id')
        is_container_same = python_data.get('is_container_same')

        if is_container_same == True:
            for get_id in id:
                update = models.ProductOrderDetail.objects.get(id = get_id)
                update.container_id = python_data.get('container_id', update.container_id)
                update.save()
        else:
            update = models.ProductOrderDetail.objects.get(id = id)
            update.container_id = python_data.get('container_id', update.container_id)
            update.save()
        
        res={
            'message':"Container added."
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
