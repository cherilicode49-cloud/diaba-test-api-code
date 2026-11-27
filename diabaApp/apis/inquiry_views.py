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
from decimal import Decimal
from django.utils import timezone

from diabaApp.serializer import ProductInquirySerializer, VendorDelayNoteSerializer, VendorDetailExistsInDelayNote
from diabaApp.apis.wallet_views import get_all_currency_rates, convert_to_usd, calculate_locked_values

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL

@csrf_exempt
def product_inquiry_form(request):
    if request.method == "POST":
        try:
            product_data_raw = request.POST.get("product_data", "[]")
            if isinstance(product_data_raw, str):
                product_data = json.loads(product_data_raw)
            elif isinstance(product_data_raw, list):
                product_data = product_data_raw
            else:
                product_data = []

            customer_id = request.POST.get("customer_id")

            # Dynamic setting check for inquiry price & free_inquiry toggle
            setting = models.InquirySetting.objects.all().first()
            is_free_inquiry = setting.free_inquiry if setting else False
            configured_price = float(setting.inquiry_price) if (setting and setting.inquiry_price is not None) else 0.0
            configured_currency = setting.inquiry_currency if (setting and setting.inquiry_currency) else "XOF"

            raw_amount = request.POST.get("amount")
            bictorys_id = request.POST.get("bictorys_transaction_id")
            payment_ref = request.POST.get("payment_reference")

            # Determine payment parameters
            if is_free_inquiry or configured_price <= 0:
                payment_type = "Free"
                payment_id = bictorys_id or f"FREE-{uuid.uuid4().hex[:10].upper()}"
                reference_id = payment_ref or f"FREE-REF-{uuid.uuid4().hex[:8].upper()}"
                total_amount = "0"
                currency = configured_currency
                status = "Success"
            else:
                payment_type = request.POST.get("payment_type", "Bictorys") or "Bictorys"
                payment_id = bictorys_id or f"TX-{uuid.uuid4().hex[:10].upper()}"
                reference_id = payment_ref or f"REF-{uuid.uuid4().hex[:8].upper()}"
                total_amount = raw_amount if raw_amount is not None else str(configured_price)
                currency = request.POST.get("currency", configured_currency) or configured_currency
                status = "Success"

            with transaction.atomic():
                payment_transaction = models.ProductRequestTransaction.objects.create(
                    customer_id=customer_id,
                    payment_type=payment_type,
                    payment_id=payment_id,
                    reference_id=reference_id,
                    total_amount=total_amount,
                    currency=currency,
                    status=status,
                )

                print(request.POST, 'product_data', flush=True)
                inquiry_code = f"INQ-{uuid.uuid4().hex[:8].upper()}"
                created_inquiry_ids = []

                for index, product in enumerate(product_data):
                    product_name = product.get("product_name")
                    description = product.get("description")
                    quantity = product.get("quantity")

                    try: 
                        quantity = int(quantity)
                    except (ValueError, TypeError):
                        res = {
                            'message': 'Quantity should be an integer.'
                        }
                        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=406)
                    
                    product_inquiry = models.ProductInquiry.objects.create(
                        transaction_id=payment_transaction.id,
                        customer_id=customer_id,
                        inquiry_code=inquiry_code,
                        product_name=product_name,
                        description=description,
                        quantity=quantity,
                        created_at=timezone.now()
                    )
                    created_inquiry_ids.append(product_inquiry.id)

                    # Look for images under various possible field keys: images_0, images_0[], images, images[]
                    images = (
                        request.FILES.getlist(f"images_{index}") or 
                        request.FILES.getlist(f"images_{index}[]") or 
                        (request.FILES.getlist("images") if len(product_data) == 1 else []) or
                        (request.FILES.getlist("images[]") if len(product_data) == 1 else [])
                    )

                    for image in images:
                        models.ProductInquiryImages.objects.create(
                            inquiry=product_inquiry,
                            image=image
                        )

                # AUTOMATIC WALLET TRANSFER:
                # If is_free_inquiry is True: no record is added to wallet.
                # If is_free_inquiry is False: automatic payable amount transferred to customer wallet with all currency values.
                wallet_credit_info = None
                if not is_free_inquiry and customer_id:
                    try:
                        payable_num = float(str(total_amount).replace(',', '').strip())
                    except (ValueError, TypeError):
                        payable_num = 0.0

                    if payable_num > 0:
                        customer = models.CustomerDetail.objects.filter(id=customer_id).first()
                        if customer:
                            now = timezone.now()
                            rates = get_all_currency_rates()
                            usd_amount = convert_to_usd(payable_num, currency, rates)
                            locked_values = calculate_locked_values(usd_amount, rates)
                            usd_decimal = Decimal(str(round(usd_amount, 2)))

                            wallet, _ = models.CustomerWallet.objects.select_for_update().get_or_create(
                                customer=customer,
                                defaults={'balance': Decimal('0.00'), 'currency': 'USD', 'status': 'Active'}
                            )

                            balance_before = wallet.balance
                            balance_after = balance_before + usd_decimal
                            wallet.balance = balance_after
                            wallet.save(update_fields=['balance', 'updated_at'])

                            tx_ref = f"WTX-INQ-{now.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
                            models.WalletTransaction.objects.create(
                                wallet=wallet,
                                customer=customer,
                                transaction_type='Credit',
                                amount=usd_decimal,
                                currency='USD',
                                balance_before=balance_before,
                                balance_after=balance_after,
                                source_type='Inquiry_Payment',
                                source_id=inquiry_code,
                                transaction_ref=tx_ref,
                                description=f"Automatic inquiry transfer to wallet: {inquiry_code} ({payable_num} {currency})",
                                rates_snapshot=rates,
                                locked_values=locked_values,
                                status='Success'
                            )

                            payment_transaction.is_wallet_transferred = True
                            payment_transaction.wallet_transferred_at = now
                            payment_transaction.save(update_fields=['is_wallet_transferred', 'wallet_transferred_at'])

                            models.ProductInquiry.objects.filter(id__in=created_inquiry_ids).update(
                                is_wallet_transferred=True,
                                wallet_transferred_at=now
                            )

                            wallet_credit_info = {
                                'transaction_ref': tx_ref,
                                'credited_amount': payable_num,
                                'currency': currency,
                                'credited_usd': float(usd_decimal),
                                'balance_after_usd': float(balance_after),
                                'locked_values': locked_values
                            }

            res = {
                'message': 'Inquiry Submitted Successfully',
                'inquiry_code': inquiry_code,
                'is_free_inquiry': is_free_inquiry,
                'wallet_credited': bool(wallet_credit_info),
            }
            if wallet_credit_info:
                res['wallet_data'] = wallet_credit_info
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

        except Exception as e:
            import traceback
            traceback.print_exc()
            res = {
                'message': f'Failed to submit inquiry: {str(e)}'
            }
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=500)
    else:
        print(request.method, "request.method")
        res = {
            'message': 'something went wrong'
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=500)



@csrf_exempt
def customer_inquiry_list(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        customer = python_data.get('customer')
        get_inquiry = models.ProductInquiry.objects.filter(customer = customer).order_by('-id')
        serialiser = ProductInquirySerializer(get_inquiry, many=True).data
        res={
            'data':serialiser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def product_inquiry_status_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        inquiry_id = python_data.get('inquiry_id')
        status = python_data.get('status')

        get_inquiry = models.ProductInquiry.objects.get(id = inquiry_id)
        get_inquiry.status = status
        get_inquiry.save()

        res={
            'message':'Inquiry Status Updated'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def export_product_inquiry_list(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        print("Python_data-=-=-=--->",python_data)

        user_type = python_data.get('user_type')

        inquiry_list = models.ProductInquiry.objects.all().order_by('-id')
        inquiry_list_serializer = ProductInquirySerializer(inquiry_list, many=True).data

        headers = [
            "Inquiry Code",
            "Product Name",
            "Description",
            "Quantity",
            "Customer Name",
            
        ]

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Inquiry List"

        field_map = {
            'Inquiry Code':'inquiry_code',
            'Product Name':'product_name',
            'Description':'description',
            'Quantity':'quantity',
            'Customer Name':'customer_name',
        }
        if user_type == "admin":
            headers.append("Customer Country Code")
            headers.append("Customer Mobile")
            headers.append("Customer Email")
        
            field_map.update({
                'Customer Email':'customer_email',          
                'Customer Country Code':'customer_countryCode',
                'Customer Mobile':'customer_mobileNumber',
            })
      
        ws.append(headers)
      
        for row in inquiry_list_serializer:  # list_data = your queryset/serializer output
            ws.append([row.get(field_map[h], "") for h in headers])


        # Create the HTTP response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="customer_list.xlsx"'

        wb.save(response)


        # res={
        #     'data':response
        # }
        # json_data = JSONRenderer().render(res)
        # return HttpResponse(json_data, content_type= 'application/json', status=200)

        return response

@csrf_exempt
def product_inquiry_list(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        print("python_data=====>",python_data)

        page_number = int(python_data.get('page_number', 1))
        row_size = int(python_data.get('row_data', 10))
        last_row = row_size * page_number
        first_row = last_row - row_size
        
        search_key = python_data.get('search_key')
        status = python_data.get('status')
        filter_condition = Q()

        if status not in [None,'','null']:
            filter_condition &= Q(status = status)

        if search_key not in [None,'','null']:
            filter_condition &= Q(customer__name__icontains = search_key)| Q(inquiry_code__icontains = search_key) | Q(product_name__icontains = search_key) | Q(customer__mobileNumber__icontains = search_key)

        total_inquiry_count = models.ProductInquiry.objects.filter(filter_condition).order_by('-id').count()
        inquiry_list = models.ProductInquiry.objects.filter(filter_condition).order_by('-id')[first_row:last_row]
        inquiry_list_serializer = ProductInquirySerializer(inquiry_list, many=True).data


        res={
            'data':inquiry_list_serializer,
            'total_inquiry_count':total_inquiry_count,
            'total_count':total_inquiry_count
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def delay_note_create(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        vendor_ids = python_data.get('vendor_ids')
        note = python_data.get('note')
        start_at = python_data.get('start_at')
        end_at = python_data.get('end_at')
        
        created_at = datetime.now()

        delay_note_code = f"DN-{uuid.uuid4().hex[:8].upper()}"

        # try:
        #     vendor_list = [int(x) for x in vendor_ids.split(',')]
        # except Exception as e:

        #     vendor_list = json.loads(vendor_ids)

        delay_note_exists = models.VendorDelayNote.objects.filter(
            start_at__gte = start_at,
            end_at__lte = end_at,
            vendor__id__in = vendor_ids
        ).exists()

        if delay_note_exists:
            res={
                "message":"A delay note already exists among selected vandors during this time period."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

        delay_note = models.VendorDelayNote.objects.create(
            delay_note_code = delay_note_code,
            note = note,
            start_at = start_at,
            end_at = end_at,
            created_at = created_at,
        )
        delay_note.vendor.set(vendor_ids)
        delay_note.save()

        res={
            'message':'Delay Note Added'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

        
@csrf_exempt
def delay_note_list(request):
    if request.method == "POST":
        delay_notes = models.VendorDelayNote.objects.all().order_by('-id')
        delay_notes_serializer = VendorDelayNoteSerializer(delay_notes, many=True).data

        res={
            'data':delay_notes_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def delay_note_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        id = python_data.get('id')
        vendor_ids = python_data.get('vendor_ids')
        note = python_data.get('note')
        start_at = python_data.get('start_at')
        end_at = python_data.get('end_at')

        delay_note_exists = models.VendorDelayNote.objects.filter(
            start_at__gte = start_at,
            end_at__lte = end_at,
            vendor__id__in = vendor_ids
        ).exclude(id=id).exists()

        if delay_note_exists:
            res={
                "message":"A delay note already exists among selected vandors during this time period."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        delay_note = models.VendorDelayNote.objects.get(id = id)
        delay_note.note = note
        delay_note.start_at = start_at
        delay_note.end_at = end_at
        delay_note.vendor.set(vendor_ids)
        delay_note.save()

        res={
            'message':'Delay Note Updated'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def delay_note_status_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        status = python_data.get('status')

        delay_note = models.VendorDelayNote.objects.get(id=id)
        delay_note.status = status
        delay_note.save()

        res={
            'message':'Delay Note Status Updated'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def vendor_list_with_delay_note(request):
    if request.method == "POST":
        vendor_list = models.VendorDetail.objects.all().order_by('vendor_name')
        vendor_list_serializer = VendorDetailExistsInDelayNote(vendor_list, many=True).data

        res={
            'data':vendor_list_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def inquiry_amount(request):
    """
    App-side endpoint to fetch the current inquiry price amount and multi-currency values.
    Endpoint: /api/inquiry_amount/
    
    Supports GET and POST.
    Optional parameters:
      - currency: user's requested display currency (e.g. 'XOF', 'USD', 'EUR', 'CNY')
    """
    if request.method not in ["GET", "POST"]:
        return HttpResponse(
            JSONRenderer().render({'status': False, 'message': 'Method not allowed'}),
            content_type='application/json',
            status=405
        )

    python_data = {}
    if request.body:
        try:
            python_data = JSONParser().parse(io.BytesIO(request.body))
        except Exception:
            pass

    req_currency = python_data.get('currency') or request.GET.get('currency')

    setting = models.InquirySetting.objects.all().first()
    if not setting:
        setting = models.InquirySetting.objects.create(
            inquiry_price=0.00,
            inquiry_currency='XOF',
            free_inquiry=False
        )

    is_free = bool(setting.free_inquiry)
    base_price = float(setting.inquiry_price or 0.0)
    base_currency = (setting.inquiry_currency or 'XOF').upper().strip()

    rates = get_all_currency_rates()

    if is_free or base_price <= 0:
        usd_amount = 0.0
        all_conversions = {curr: 0.0 for curr in rates}
        display_amount = 0.0
        target_currency = (req_currency or base_currency).upper().strip()
    else:
        usd_amount = convert_to_usd(base_price, base_currency, rates)
        all_conversions = calculate_locked_values(usd_amount, rates)
        target_currency = (req_currency or base_currency).upper().strip()
        display_amount = all_conversions.get(target_currency, base_price)

    data = {
        'is_free_inquiry': is_free,
        'free_inquiry': is_free,
        'inquiry_price': base_price,
        'inquiry_currency': base_currency,
        'amount': display_amount,
        'currency': target_currency,
        'all_currencies': all_conversions,
        'rates': rates
    }

    res = {
        'status': True,
        'message': 'Inquiry amount retrieved successfully',
        'data': data
    }
    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)


