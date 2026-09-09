import requests
from django.conf import settings

class APIDTSClient:
    BASE_URL = settings.APIDTS_BASE_URL
    API_KEY = settings.APIDTS_API_KEY

    @staticmethod
    def _headers():
        return {
            "Authorization": f"Bearer {APIDTSClient.API_KEY}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def cash_in(amount, phone_number, network_code, currency="XOF"):
        url = f"{APIDTSClient.BASE_URL}/transactions/cash_in"

        payload = {
            "amount": amount,
            "phone_number": phone_number,
            "network_code": network_code,
            "currency": currency,
            "success_url": "https://api.diaba.store/api/success_url/",
            "error_url": "https://api.diaba.store/api/error_url/",

        }


        response = requests.post(url, json=payload, headers=APIDTSClient._headers())
        return response.json()

    @staticmethod
    def cash_out(amount, phone_number, network_code, currency="XOF"):
        url = f"{APIDTSClient.BASE_URL}/transactions/cash_out"

        payload = {
            "amount": amount,
            "phone_number": phone_number,
            "network_code": network_code,
            "currency": currency
        }

        response = requests.post(url, json=payload, headers=APIDTSClient._headers())
        return response.json()

    @staticmethod
    def check_status(transaction_id):
        url = f"{APIDTSClient.BASE_URL}/transactions/{transaction_id}"
        response = requests.get(url, headers=APIDTSClient._headers())
        return response.json()
