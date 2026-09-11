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

from django.template.loader import render_to_string

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL
import  requests
from diabaApp.serializer import ProductOrderDetailOrderSerializer, OrderDetailSerializer, OrderDetailDataSerializer, \
    ProductOrderDetailSerializer, ProductReviewSerializer, VendorOrderDetailSerializer, VendorOrderTrackingSerializer, \
    WarehouseDetailSerializer, VendorOrderDataSerializer, OrderTrackingSerializer, PromocodeDetailSerializer, OrderInquiryDataSerializer



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
                price = math.ceil(total_price * 1.015)
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

        if promocode:
            promocode = models.PromocodeDetail.objects.get(promocode = promocode)
            promocode_id = promocode.id
        else:
            promocode_id = None

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
            
        promocode_name = None
        promocode_discount = None

        if order.promocode != None:
            promocode_data = models.PromocodeDetail.objects.get(id = order.promocode.id)
            # remaining_promocode = int(promocode_data.remaining_promocode) - 1
            # promocode_data.remaining_promocode = remaining_promocode
            # promocode_data.save()
            promocode_name = promocode_data.promocode
            promocode_discount = promocode_data.discount



            promocode_track = models.PromocodeTracking.objects.create(
                order_id = order_id,
                promocode_id = order.promocode.id,
                customer_id = order.customer.id,
                created_at = date_time
            ).save()

            promocode = order.promocode.id
            # order_id = order_id

            commission_percentage = int(order.promocode.influencer.commission)
            original_currency = currency_name
            original_total_amount = original_total_amount
            original_total_amount = int(original_total_amount.replace(' ', '').strip())
            original_amount_paid = original_amount_paid
            original_amount_paid = int(original_amount_paid.replace(' ', '').strip())
            if original_currency == "XOF":
                converted_currency = original_currency
                converted_total_amount = original_total_amount
                converted_amount_paid = int(original_amount_paid)
            else:
                get_currency_rate = models.CurrencyConverter.objects.filter(currency_code = "XOF").values_list('system_rate', flat=True)[0]
                
                converted_currency = "XOF"
                converted_total_amount = float(original_total_amount)*float(get_currency_rate)
                converted_amount_paid = int(float(original_amount_paid)*float(get_currency_rate))
            
            total_commission = round((converted_amount_paid*commission_percentage)/100)

            create_commission = models.PromocodeCommissionDetail.objects.create(
                order_id = order_id,
                promocode_id = promocode,
                original_currency = original_currency,
                original_total_amount = original_total_amount,
                original_amount_paid = original_amount_paid,
                converted_currency = converted_currency,
                converted_total_amount = converted_total_amount,
                converted_amount_paid = converted_amount_paid,
                commission_percentage = commission_percentage,
                total_commission = total_commission,
                created_at = date_time
            ).save()

        # order_list_product
        order_data = models.ProductOrderDetail.objects.filter(order_id = order_id)
        order_list_product = ProductOrderDetailOrderSerializer(order_data,many=True).data

        user = get_customer.name
        get_address = models.CustomerAddressDetail.objects.get(id = customer_address)
        street_address = get_address.street_address
        city = get_address.city
        country = get_address.country
        
        if int(discount_price.replace(' ', '').strip())== 0:
            discount_price = None
        # print("STARTING OF EMAIL.......", discount_price)
        
        context = {
            'user': user, 
            'order_id': order_number,
            'date': date_time,
            'customer_name': user,
            'street_address' : street_address,
            'city' : city,
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
            'context':context
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

        if promocode:
            promocode = models.PromocodeDetail.objects.get(promocode = promocode)
            promocode_id = promocode.id
        else:
            promocode_id = None

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
        

        create_transaction = models.OrderTransaction.objects.create(
            order_id  = order_id,
            customer_id = customer,
            currency= currency_name,
            payment_type = payment_type,
            payment_id = payment_id,
            reference_id = reference_id,
            fee_amount = fee_amount,
            net_amount = net_amount,
            total_amount = original_total_amount,
            tax_price = tax_price,
            status = 'completed',
            created_at = date_time,
        ).save()
        order.payment_id = payment_id
        order.save()

        cart_data = models.CartDetail.objects.filter(customer = customer)
        cart_data.delete()
            
        promocode_name = None
        promocode_discount = None

        if order.promocode != None:
            promocode_data = models.PromocodeDetail.objects.get(id = order.promocode.id)
            promocode_name = promocode_data.promocode
            promocode_discount = promocode_data.discount



            promocode_track = models.PromocodeTracking.objects.create(
                order_id = order_id,
                promocode_id = order.promocode.id,
                customer_id = order.customer.id,
                created_at = date_time
            ).save()

            promocode = order.promocode.id
           
            commission_percentage = int(order.promocode.influencer.commission)
            original_currency = currency_name
            original_total_amount = original_total_amount
            original_total_amount = int(original_total_amount.replace(' ', '').strip())
            original_amount_paid = original_amount_paid
            original_amount_paid = int(original_amount_paid.replace(' ', '').strip())
            if original_currency == "XOF":
                converted_currency = original_currency
                converted_total_amount = original_total_amount
                converted_amount_paid = int(original_amount_paid)
            else:
                get_currency_rate = models.CurrencyConverter.objects.filter(currency_code = "XOF").values_list('system_rate', flat=True)[0]
                
                converted_currency = "XOF"
                converted_total_amount = float(original_total_amount)*float(get_currency_rate)
                converted_amount_paid = int(float(original_amount_paid)*float(get_currency_rate))
            
            total_commission = round((converted_amount_paid*commission_percentage)/100)

            create_commission = models.PromocodeCommissionDetail.objects.create(
                order_id = order_id,
                promocode_id = promocode,
                original_currency = original_currency,
                original_total_amount = original_total_amount,
                original_amount_paid = original_amount_paid,
                converted_currency = converted_currency,
                converted_total_amount = converted_total_amount,
                converted_amount_paid = converted_amount_paid,
                commission_percentage = commission_percentage,
                total_commission = total_commission,
                created_at = date_time
            ).save()

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
            'context':context
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
            
        promocode_name = None
        promocode_discount = None

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
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
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
        if order_data.promocode != None:
            all_promocode = models.PromocodeDetail.objects.get(id = order_data.promocode.id)
            promocode_data = PromocodeDetailSerializer(all_promocode).data 

        res={
            'data':order_serializer,
            'product_data':list_data,
            'promocode_data':promocode_data
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
            product_image = IMAGE_URL + str(status_create.variant.product.product_image_1)
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
        order = python_data.get('id')
        
        product = models.ProductOrderDetail.objects.filter(order=order)
        if product.exists():
            product.delete()

        vendor = models.VendorOrderDetail.objects.filter(order=order)
        if vendor.exists():
            vendor.delete()

        vendor_tracking = models.VendorOrderTracking.objects.filter(order=order)
        if vendor_tracking.exists():
            vendor_tracking.delete()
        
        order_tracking = models.OrderTracking.objects.filter(order=order)
        if order_tracking.exists():
            order_tracking.delete()
        
        order_transaction = models.OrderTransaction.objects.filter(order=order)
        if order_transaction.exists():
            order_transaction.delete()
        
        promocode = models.PromocodeTracking.objects.filter(order=order)
        if promocode.exists():
            promocode.delete()
                
        commission = models.PromocodeCommissionDetail.objects.filter(order=order)
        if commission.exists():
            commission.delete()

        order = models.OrderDetail.objects.filter(id=order)
        if order.exists():
            order.delete()
        
        res = {
            'data':"serialser"
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

    
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
