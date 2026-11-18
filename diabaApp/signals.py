from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models
from .faiss_store import async_refresh_faiss


from django.db import transaction

@receiver(post_save, sender=models.ProductDetail)
def product_updated(sender, instance, **kwargs):
    if instance.product_added_from in ['yuwi_go', 'yiwu_go'] or instance.status in ['yuwi_go', 'yiwu_go'] or getattr(instance, '_skip_faiss_refresh', False):
        return

    transaction.on_commit(
        lambda: async_refresh_faiss()
    )