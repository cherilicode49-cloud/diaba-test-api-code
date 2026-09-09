import requests
from django.conf import settings


class PayDunyaService:

    @staticmethod
    def create_invoice(order_id, amount, customer_name, email):
        url = "https://app.paydunya.com/api/v1/checkout-invoice/create"

        headers = {
            "PAYDUNYA-MASTER-KEY": settings.PAYDUNYA_MASTER_KEY,
            "PAYDUNYA-PRIVATE-KEY": settings.PAYDUNYA_PRIVATE_KEY,
            "PAYDUNYA-TOKEN": settings.PAYDUNYA_TOKEN,
            "Content-Type": "application/json"
        }

        payload = {
            "invoice": {
                "items": [
                    {
                        "name": f"Order #{order_id}",
                        "quantity": 1,
                        "unit_price": float(amount),
                        "total_price": float(amount),
                        "description": "Payment for Order"
                    }
                ],
                "total_amount": float(amount),
                "description": f"Order Payment #{order_id}"
            },
            "store": {
                "name": "Your Store Name",
                "website_url": "https://yourwebsite.com"
            },
            "actions": {
                "cancel_url": "https://yourwebsite.com/payment-cancel",
                "return_url": "https://yourwebsite.com/payment-success",
                "callback_url": "https://yourwebsite.com/api/payment/callback/"
            },
            "custom_data": {
                "order_id": str(order_id),
                "customer_name": customer_name,
                "email": email
            }
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers
        )

        return response.json()