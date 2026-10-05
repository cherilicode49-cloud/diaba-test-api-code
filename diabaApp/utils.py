from diabaApp import models
import logging

logger = logging.getLogger(__name__)

def track_user_activity(
    action_type,
    customer_id=None,
    product_id=None,
    product_name=None,
    payment_method=None,
    search_keyword=None,
    category_name=None,
    metadata=None,
    device_id=None,
    device_type=None,
    ip_address=None,
    country=None
):
    """
    Utility function to log user activity into the database safely.
    Works for both registered customers and guest visits.
    """
    try:
        # If product_id is given but product_name is empty, fetch name if available
        if product_id and not product_name:
            try:
                prod = models.ProductDetail.objects.filter(id=product_id).first()
                if prod:
                    product_name = prod.product_name
            except Exception:
                pass

        activity = models.UserActivity.objects.create(
            customer_id=customer_id if customer_id else None,
            action_type=action_type,
            product_id=str(product_id) if product_id is not None else None,
            product_name=product_name,
            payment_method=payment_method,
            search_keyword=search_keyword,
            category_name=category_name,
            metadata=metadata if isinstance(metadata, dict) else {},
            device_id=device_id,
            device_type=device_type,
            ip_address=ip_address,
            country=country
        )
        return activity
    except Exception as e:
        logger.error(f"Error logging user activity: {e}")
        return None
