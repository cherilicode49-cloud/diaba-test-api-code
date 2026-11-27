from django.views.decorators.csrf import csrf_exempt
from diabaApp import models
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
import io
import math, random
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Q
import numpy as np
import uuid
from decimal import Decimal

from diabaApp.serializer import CustomerWalletSerializer, WalletTransactionSerializer


def get_all_currency_rates():
    """
    Returns a dictionary of all active system exchange rates from CurrencyConverter.
    Base currency is USD (rate = 1.0).
    """
    rates = {'USD': 1.0}
    for conv in models.CurrencyConverter.objects.all():
        try:
            rates[conv.currency_code] = float(conv.system_rate) if conv.system_rate else 1.0
        except Exception:
            pass
    if 'XOF' not in rates or rates['XOF'] <= 0:
        rates['XOF'] = 589.0
    return rates


def convert_to_usd(amount, from_currency, rates):
    """
    Converts any amount from its source currency to USD base using rates dictionary.
    """
    amt = float(amount)
    from_curr = str(from_currency).upper().strip()
    if from_curr in ['USD', '$']:
        return amt
    rate = rates.get(from_curr, 0.0)
    if rate > 0:
        return amt / rate
    # Fallback to XOF rate if unspecified CFA Franc
    if from_curr in ['CFA', 'FCFA']:
        xof_rate = rates.get('XOF', 589.0)
        return amt / xof_rate if xof_rate > 0 else amt
    return amt


def calculate_locked_values(usd_amount, rates):
    """
    Computes exact converted amounts across all supported currencies.
    """
    usd_val = float(usd_amount)
    values = {}
    for code, rate in rates.items():
        if code == 'USD':
            values['USD'] = round(usd_val, 2)
        else:
            values[code] = round(usd_val * rate, 2)
    return values


def compute_customer_locked_balances(customer, wallet, rates):
    """
    Computes exact wallet balances across all currencies using historical locked_values
    stored in WalletTransaction records. Eliminates live exchange rate drift for
    transferred inquiries and credits.
    """
    if not wallet or wallet.balance <= Decimal('0.00'):
        return {code: 0.0 for code in rates}

    tx_qs = models.WalletTransaction.objects.filter(
        customer=customer,
        status='Success'
    ).order_by('id')

    if not tx_qs.exists():
        usd_balance = convert_to_usd(wallet.balance, wallet.currency, rates)
        conversions = calculate_locked_values(usd_balance, rates)
        if wallet.currency:
            conversions[wallet.currency.upper()] = float(wallet.balance)
        return conversions

    conversions = {}
    for code, rate in rates.items():
        total_credit = 0.0
        total_debit = 0.0
        has_locked = False

        for tx in tx_qs:
            tx_locked = tx.locked_values if isinstance(tx.locked_values, dict) else {}
            if tx.transaction_type == 'Credit':
                if code in tx_locked:
                    try:
                        total_credit += float(tx_locked[code])
                        has_locked = True
                    except (ValueError, TypeError):
                        pass
                elif tx.currency and tx.currency.upper() == code:
                    total_credit += float(tx.amount)
                    has_locked = True
                else:
                    tx_rates = tx.rates_snapshot if isinstance(tx.rates_snapshot, dict) and tx.rates_snapshot else rates
                    usd_val = convert_to_usd(tx.amount, tx.currency, tx_rates)
                    r = tx_rates.get(code, rate)
                    total_credit += float(usd_val * r if code != 'USD' else usd_val)
            elif tx.transaction_type == 'Debit':
                if code in tx_locked:
                    try:
                        total_debit += float(tx_locked[code])
                    except (ValueError, TypeError):
                        pass
                elif tx.currency and tx.currency.upper() == code:
                    total_debit += float(tx.amount)
                else:
                    tx_rates = tx.rates_snapshot if isinstance(tx.rates_snapshot, dict) and tx.rates_snapshot else rates
                    usd_val = convert_to_usd(tx.amount, tx.currency, tx_rates)
                    r = tx_rates.get(code, rate)
                    total_debit += float(usd_val * r if code != 'USD' else usd_val)

        net_val = max(0.0, total_credit - total_debit)
        if not has_locked and net_val == 0.0:
            usd_bal = convert_to_usd(wallet.balance, wallet.currency, rates)
            net_val = round(usd_bal * rate, 2) if code != 'USD' else round(usd_bal, 2)

        conversions[code] = round(net_val, 2)

    # Ensure wallet's own native currency matches exact wallet balance if not already matching
    if wallet.currency and wallet.currency.upper() in conversions:
        conversions[wallet.currency.upper()] = float(wallet.balance)

    return conversions


@csrf_exempt
def customer_wallet_balance(request):
    """
    Fetch customer wallet balance and live currency conversions.
    POST JSON or GET query params:
      - customer_id (required): int
      - currency (optional): str (e.g. 'XOF', 'USD', 'XAF', 'CDF', 'GNF')
        When currency is provided, returns exact total value converted using lock currency.
    """
    if request.method in ["POST", "GET"]:
        python_data = {}
        if request.body:
            try:
                python_data = JSONParser().parse(io.BytesIO(request.body))
            except Exception:
                pass

        customer_id = python_data.get('customer_id') or request.GET.get('customer_id')
        if not customer_id:
            res = {'status': False, 'message': 'customer_id is required.'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        customer = models.CustomerDetail.objects.filter(id=customer_id).first()
        if not customer:
            res = {'status': False, 'message': 'Customer not found.'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=404)

        target_currency = (python_data.get('currency') or request.GET.get('currency') or '').strip().upper()

        wallet, _ = models.CustomerWallet.objects.get_or_create(
            customer=customer,
            defaults={'balance': Decimal('0.00'), 'currency': 'USD', 'status': 'Active'}
        )

        rates = get_all_currency_rates()
        locked_conversions = compute_customer_locked_balances(customer, wallet, rates)

        # If a specific currency was requested that isn't in locked_conversions, convert it
        if target_currency and target_currency not in locked_conversions:
            usd_val = convert_to_usd(wallet.balance, wallet.currency, rates)
            r = rates.get(target_currency, 1.0)
            locked_conversions[target_currency] = round(usd_val * r if target_currency != 'USD' else usd_val, 2)

        effective_currency = target_currency if target_currency else (wallet.currency or 'USD')
        exact_converted_value = locked_conversions.get(effective_currency, float(wallet.balance))

        # Calculate total credits and debits in USD
        credit_txs = models.WalletTransaction.objects.filter(
            customer=customer, transaction_type='Credit', status='Success'
        )
        total_credits_usd = 0.0
        for tx in credit_txs:
            if isinstance(tx.locked_values, dict) and 'USD' in tx.locked_values:
                try:
                    total_credits_usd += float(tx.locked_values['USD'])
                except (ValueError, TypeError):
                    total_credits_usd += convert_to_usd(tx.amount, tx.currency, rates)
            else:
                total_credits_usd += convert_to_usd(tx.amount, tx.currency, rates)

        debit_txs = models.WalletTransaction.objects.filter(
            customer=customer, transaction_type='Debit', status='Success'
        )
        total_debits_usd = 0.0
        for tx in debit_txs:
            if isinstance(tx.locked_values, dict) and 'USD' in tx.locked_values:
                try:
                    total_debits_usd += float(tx.locked_values['USD'])
                except (ValueError, TypeError):
                    total_debits_usd += convert_to_usd(tx.amount, tx.currency, rates)
            else:
                total_debits_usd += convert_to_usd(tx.amount, tx.currency, rates)

        res = {
            'status': True,
            'message': 'Wallet balance retrieved successfully',
            'data': {
                'wallet_id': wallet.id,
                'customer_id': customer.id,
                'customer_name': customer.name,
                'balance': exact_converted_value if target_currency else float(wallet.balance),
                'currency': effective_currency,
                'converted_balance': exact_converted_value,
                'locked_currency_value': exact_converted_value,
                'total_wallet_balance': exact_converted_value,
                'target_currency': effective_currency,
                'wallet_balance': float(wallet.balance),
                'wallet_currency': wallet.currency,
                'currency_conversions': locked_conversions,
                'total_credits_usd': round(total_credits_usd, 2),
                'total_debits_usd': round(total_debits_usd, 2),
                'status': wallet.status
            }
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

    res = {'status': False, 'message': 'Invalid request method.'}
    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=405)


@csrf_exempt
def eligible_inquiries_for_wallet(request):
    """
    Lists inquiries eligible for transfer into customer wallet balance.
    POST JSON or GET query params: customer_id
    """
    if request.method in ["POST", "GET"]:
        python_data = {}
        if request.body:
            try:
                python_data = JSONParser().parse(io.BytesIO(request.body))
            except Exception:
                pass

        customer_id = python_data.get('customer_id') or request.GET.get('customer_id')
        if not customer_id:
            res = {'status': False, 'message': 'customer_id is required.'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        rates = get_all_currency_rates()
        eligible_list = []

        # 1. ProductInquiry entries with transactions
        inquiries = models.ProductInquiry.objects.filter(
            customer_id=customer_id,
            is_wallet_transferred=False
        ).select_related('transaction').order_by('-id')

        for inq in inquiries:
            tx = inq.transaction
            if tx and tx.total_amount:
                try:
                    raw_amount = float(str(tx.total_amount).replace(',', '').strip())
                except (ValueError, TypeError):
                    raw_amount = 0.0

                if raw_amount > 0:
                    curr = tx.currency or 'XOF'
                    usd_val = convert_to_usd(raw_amount, curr, rates)
                    eligible_list.append({
                        'inquiry_type': 'product_inquiry',
                        'inquiry_id': inq.id,
                        'inquiry_code': inq.inquiry_code or f"INQ-{inq.id}",
                        'product_name': inq.product_name or 'Custom Product Inquiry',
                        'original_amount': raw_amount,
                        'original_currency': curr,
                        'estimated_usd': round(usd_val, 2),
                        'converted_values': calculate_locked_values(usd_val, rates),
                        'created_at': inq.created_at.strftime('%Y-%m-%d %H:%M:%S') if inq.created_at else None,
                        'status': inq.status
                    })

        # 2. OrderDetail entries with order_status='inquiry'
        orders = models.OrderDetail.objects.filter(
            customer_id=customer_id,
            order_status='inquiry',
            is_wallet_transferred=False
        ).order_by('-id')

        for ord_obj in orders:
            try:
                raw_amount = float(ord_obj.total_price) if ord_obj.total_price else 0.0
            except (ValueError, TypeError):
                raw_amount = 0.0

            if raw_amount > 0:
                curr = ord_obj.currency_name or ord_obj.currency or 'USD'
                usd_val = convert_to_usd(raw_amount, curr, rates)
                eligible_list.append({
                    'inquiry_type': 'order_inquiry',
                    'inquiry_id': ord_obj.id,
                    'inquiry_code': ord_obj.order_id,
                    'product_name': f"Inquiry Order #{ord_obj.order_id}",
                    'original_amount': raw_amount,
                    'original_currency': curr,
                    'estimated_usd': round(usd_val, 2),
                    'converted_values': calculate_locked_values(usd_val, rates),
                    'created_at': ord_obj.created_at.strftime('%Y-%m-%d %H:%M:%S') if ord_obj.created_at else None,
                    'status': ord_obj.status
                })

        res = {
            'status': True,
            'message': 'Eligible inquiries fetched successfully',
            'data': eligible_list,
            'total_eligible': len(eligible_list)
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

    res = {'status': False, 'message': 'Invalid request method.'}
    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=405)


@csrf_exempt
def transfer_inquiry_to_wallet(request):
    """
    Transfers inquiry amount into the customer's wallet balance.
    Captures exact exchange rate snapshot and locks converted values across all currencies.
    Payload:
      - customer_id: int
      - inquiry_id: int
      - inquiry_type: 'product_inquiry' (default) or 'order_inquiry'
    """
    if request.method == "POST":
        try:
            python_data = JSONParser().parse(io.BytesIO(request.body))
        except Exception:
            res = {'status': False, 'message': 'Invalid JSON body.'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        customer_id = python_data.get('customer_id')
        inquiry_id = python_data.get('inquiry_id')
        inquiry_type = python_data.get('inquiry_type', 'product_inquiry')

        if not customer_id or not inquiry_id:
            res = {'status': False, 'message': 'customer_id and inquiry_id are required.'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        customer = models.CustomerDetail.objects.filter(id=customer_id).first()
        if not customer:
            res = {'status': False, 'message': 'Customer not found.'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=404)

        now = timezone.now()
        rates = get_all_currency_rates()

        with transaction.atomic():
            wallet, _ = models.CustomerWallet.objects.select_for_update().get_or_create(
                customer=customer,
                defaults={'balance': Decimal('0.00'), 'currency': 'USD', 'status': 'Active'}
            )

            if inquiry_type == 'order_inquiry':
                order_obj = models.OrderDetail.objects.select_for_update().filter(id=inquiry_id, customer=customer).first()
                if not order_obj:
                    res = {'status': False, 'message': 'Inquiry order not found.'}
                    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=404)

                if order_obj.is_wallet_transferred:
                    res = {'status': False, 'message': 'This inquiry order has already been transferred to wallet.'}
                    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

                try:
                    original_amount = float(order_obj.total_price) if order_obj.total_price else 0.0
                except (ValueError, TypeError):
                    original_amount = 0.0

                if original_amount <= 0:
                    res = {'status': False, 'message': 'Inquiry order has no valid amount to transfer.'}
                    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

                original_currency = order_obj.currency_name or order_obj.currency or 'USD'
                source_ref = order_obj.order_id
                usd_amount = convert_to_usd(original_amount, original_currency, rates)

                # Mark as transferred
                order_obj.is_wallet_transferred = True
                order_obj.wallet_transferred_at = now
                order_obj.save(update_fields=['is_wallet_transferred', 'wallet_transferred_at'])

            else:
                # Default: product_inquiry
                inq_obj = models.ProductInquiry.objects.select_for_update().filter(id=inquiry_id, customer=customer).first()
                if not inq_obj:
                    res = {'status': False, 'message': 'Product inquiry not found.'}
                    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=404)

                if inq_obj.is_wallet_transferred:
                    res = {'status': False, 'message': 'This inquiry has already been transferred to wallet.'}
                    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

                tx = inq_obj.transaction
                if not tx or not tx.total_amount:
                    res = {'status': False, 'message': 'No paid transaction associated with this inquiry.'}
                    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

                if tx.is_wallet_transferred:
                    res = {'status': False, 'message': 'Transaction amount has already been transferred.'}
                    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

                try:
                    original_amount = float(str(tx.total_amount).replace(',', '').strip())
                except (ValueError, TypeError):
                    original_amount = 0.0

                if original_amount <= 0:
                    res = {'status': False, 'message': 'Inquiry transaction has no positive amount.'}
                    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

                original_currency = tx.currency or 'XOF'
                source_ref = inq_obj.inquiry_code or f"INQ-{inq_obj.id}"
                usd_amount = convert_to_usd(original_amount, original_currency, rates)

                # Mark as transferred
                inq_obj.is_wallet_transferred = True
                inq_obj.wallet_transferred_at = now
                inq_obj.save(update_fields=['is_wallet_transferred', 'wallet_transferred_at'])

                tx.is_wallet_transferred = True
                tx.wallet_transferred_at = now
                tx.save(update_fields=['is_wallet_transferred', 'wallet_transferred_at'])

            # Compute locked conversions across all currencies
            locked_values = calculate_locked_values(usd_amount, rates)
            usd_decimal = Decimal(str(round(usd_amount, 2)))

            balance_before = wallet.balance
            balance_after = balance_before + usd_decimal
            wallet.balance = balance_after
            wallet.save(update_fields=['balance', 'updated_at'])

            tx_ref = f"WTX-INQ-{now.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

            wallet_tx = models.WalletTransaction.objects.create(
                wallet=wallet,
                customer=customer,
                transaction_type='Credit',
                amount=usd_decimal,
                currency='USD',
                balance_before=balance_before,
                balance_after=balance_after,
                source_type='Inquiry_Transfer',
                source_id=source_ref,
                transaction_ref=tx_ref,
                description=f"Transfer from Inquiry {source_ref} ({original_amount} {original_currency})",
                rates_snapshot=rates,
                locked_values=locked_values,
                status='Success'
            )

        res = {
            'status': True,
            'message': 'Inquiry amount successfully transferred to wallet balance.',
            'data': {
                'transaction_ref': tx_ref,
                'source_id': source_ref,
                'original_amount': original_amount,
                'original_currency': original_currency,
                'credited_usd': float(usd_decimal),
                'balance_before_usd': float(balance_before),
                'balance_after_usd': float(balance_after),
                'locked_values': locked_values,
                'rates_snapshot': rates,
                'transferred_at': now.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

    res = {'status': False, 'message': 'Invalid request method.'}
    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=405)


@csrf_exempt
def wallet_transaction_history(request):
    """
    Paginated audit ledger of all wallet transactions (Credits & Debits) for a customer.
    Payload (POST) or Query Params (GET):
      - customer_id: int
      - page_number: int (default: 1)
      - row_data: int (default: 10)
      - transaction_type: 'Credit' or 'Debit' (optional filter)
    """
    if request.method in ["POST", "GET"]:
        python_data = {}
        if request.body:
            try:
                python_data = JSONParser().parse(io.BytesIO(request.body))
            except Exception:
                pass

        customer_id = python_data.get('customer_id') or request.GET.get('customer_id')
        if not customer_id:
            res = {'status': False, 'message': 'customer_id is required.'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        try:
            page_number = max(int(python_data.get('page_number', 1) or request.GET.get('page_number', 1)), 1)
        except (ValueError, TypeError):
            page_number = 1

        try:
            row_size = max(int(python_data.get('row_data', 10) or request.GET.get('row_data', 10)), 1)
        except (ValueError, TypeError):
            row_size = 10

        last_row = row_size * page_number
        first_row = last_row - row_size

        filter_condition = Q(customer_id=customer_id)
        tx_type = python_data.get('transaction_type') or request.GET.get('transaction_type')
        if tx_type in ['Credit', 'Debit']:
            filter_condition &= Q(transaction_type=tx_type)

        tx_qs = models.WalletTransaction.objects.filter(filter_condition).order_by('-created_at')
        total_records = tx_qs.count()
        tx_slice = tx_qs[first_row:last_row]

        serializer = WalletTransactionSerializer(tx_slice, many=True).data

        res = {
            'status': True,
            'data': serializer,
            'total_records': total_records,
            'current_page': page_number,
            'total_pages': int(np.ceil(total_records / row_size)) if total_records > 0 else 1
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

    res = {'status': False, 'message': 'Invalid request method.'}
    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=405)


@csrf_exempt
def calculate_wallet_redemption(request):
    """
    Calculates how much wallet credit can be redeemed against a checkout order in ANY currency.
    Uses the exact locked rate snapshot from the customer's credits.
    Payload:
      - customer_id: int
      - order_amount: float
      - currency: str (e.g. 'XOF', 'USD', 'XAF')
    """
    if request.method in ["POST", "GET"]:
        python_data = {}
        if request.body:
            try:
                python_data = JSONParser().parse(io.BytesIO(request.body))
            except Exception:
                pass

        customer_id = python_data.get('customer_id') or request.GET.get('customer_id')
        order_amount = python_data.get('order_amount') or request.GET.get('order_amount')
        target_currency = (python_data.get('currency') or request.GET.get('currency') or 'USD').upper().strip()

        if not customer_id or order_amount is None:
            res = {'status': False, 'message': 'customer_id and order_amount are required.'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        try:
            order_amt = float(order_amount)
        except (ValueError, TypeError):
            res = {'status': False, 'message': 'Invalid order_amount.'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        wallet = models.CustomerWallet.objects.filter(customer_id=customer_id).first()
        if not wallet or wallet.balance <= 0:
            res = {
                'status': True,
                'data': {
                    'wallet_balance_usd': 0.0,
                    'available_in_target_currency': 0.0,
                    'applied_discount': 0.0,
                    'remaining_order_amount': order_amt,
                    'currency': target_currency
                }
            }
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

        rates = get_all_currency_rates()
        target_rate = rates.get(target_currency, 1.0)

        # Inspect locked_values to preserve exact paid currency amounts and avoid exchange rate drift
        locked_conversions = compute_customer_locked_balances(wallet.customer, wallet, rates)
        if target_currency in locked_conversions:
            wallet_val_target = locked_conversions[target_currency]
        else:
            wallet_val_target = float(wallet.balance) * target_rate

        applied_discount = min(order_amt, wallet_val_target)
        remaining_order = max(0.0, order_amt - applied_discount)
        usd_to_deduct = applied_discount / target_rate if target_rate > 0 else applied_discount

        res = {
            'status': True,
            'data': {
                'wallet_balance_usd': float(wallet.balance),
                'available_in_target_currency': round(wallet_val_target, 2),
                'applied_discount': round(applied_discount, 2),
                'remaining_order_amount': round(remaining_order, 2),
                'usd_equivalent_to_deduct': round(usd_to_deduct, 2),
                'currency': target_currency,
                'exchange_rate_used': target_rate
            }
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

    res = {'status': False, 'message': 'Invalid request method.'}
    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=405)


@csrf_exempt
def admin_customer_wallet_list(request):
    """
    Admin View: Lists all customer wallets, balances, and platform total liabilities.
    Paginated with search_key filter (name, email, mobileNumber).
    """
    if request.method in ["POST", "GET"]:
        python_data = {}
        if request.body:
            try:
                python_data = JSONParser().parse(io.BytesIO(request.body))
            except Exception:
                pass

        try:
            page_number = max(int(python_data.get('page_number', 1) or request.GET.get('page_number', 1)), 1)
        except (ValueError, TypeError):
            page_number = 1

        try:
            row_size = max(int(python_data.get('row_data', 10) or request.GET.get('row_data', 10)), 1)
        except (ValueError, TypeError):
            row_size = 10

        last_row = row_size * page_number
        first_row = last_row - row_size

        search_key = python_data.get('search_key') or request.GET.get('search_key')
        filter_query = Q()
        if search_key not in [None, '', 'null']:
            filter_query = (
                Q(customer__name__icontains=search_key) |
                Q(customer__email__icontains=search_key) |
                Q(customer__mobileNumber__icontains=search_key)
            )

        wallet_qs = models.CustomerWallet.objects.filter(filter_query).select_related('customer').order_by('-balance')
        total_records = wallet_qs.count()
        wallet_slice = wallet_qs[first_row:last_row]

        serializer = CustomerWalletSerializer(wallet_slice, many=True).data

        total_system_liability_usd = models.CustomerWallet.objects.aggregate(total=Sum('balance'))['total'] or Decimal('0.00')
        rates = get_all_currency_rates()

        res = {
            'status': True,
            'data': serializer,
            'total_records': total_records,
            'current_page': page_number,
            'total_pages': int(np.ceil(total_records / row_size)) if total_records > 0 else 1,
            'platform_total_liability_usd': float(total_system_liability_usd),
            'platform_total_liability_xof': round(float(total_system_liability_usd) * rates.get('XOF', 589.0), 2)
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

    res = {'status': False, 'message': 'Invalid request method.'}
    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=405)
