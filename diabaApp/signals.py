from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models
from .faiss_store import async_refresh_faiss


from django.db import transaction

@receiver(post_save, sender=models.ProductDetail)
def product_updated(sender, instance, **kwargs):
    # Full database table scan FAISS rebuild on every single product save is intentionally disabled.
    # Rebuilding 150k+ products in Django dev/WSGI server freezes the Python process and causes Broken Pipe timeouts.
    # New image vectors are added incrementally via add_product_vectors_to_faiss() in the background vector worker.
    return