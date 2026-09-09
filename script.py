import schedule
import time
from datetime import datetime, timedelta
from diabaApp import models

from django.utils import timezone



def expire_pending_orders():
    now = datetime.now()

    # print("Ruunin script---->",now)

    updated = models.OrderDetail.objects.filter(
        status='pending',
        expire_at__lt=now
    ).exclude(payment_type__in =["cash","bank transfer"]).update(status='failed', order_status='failed')

    print(f"Expired {updated} orders")
schedule.every(10).seconds.do(expire_pending_orders)


while True:
    schedule.run_pending()
    time.sleep(1)



