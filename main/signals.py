import logging
from io import BytesIO
from PIL import Image

from django.core.files.base import ContentFile
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import productimage
from django.contrib.auth.signals import user_logged_in
from .models import basket

THUMBINAL_SIZE = (300, 300)
logger = logging.getLogger(__name__)

@receiver(pre_save, sender=productimage)
def generate_thumbnail(sender, instance, **kwargs):
    logger.info("Generating thumbnail for product %d", instance.product.id)
    image = Image.open(instance.image)
    image = image.convert("RGB")
    image.thumbnail(THUMBINAL_SIZE, Image.Resampling.LANCZOS)
    temp_thumb = BytesIO()
    image.save(temp_thumb, "JPEG")
    temp_thumb.seek(0)
    instance.thumbnail.save(
        instance.image.name,
        ContentFile(temp_thumb.read()),
        save=False,
    )
    temp_thumb.close()


@receiver(user_logged_in)
def merge_baskets_if_found(sender, user, request, **kwargs):
    anonymous_basket = getattr(request, "basket", None)
    if anonymous_basket:
        try:
            loggedin_basket = basket.objects.get(user=user, status=basket.OPEN)
            for line in anonymous_basket.basketline_set.all():
                line.basket = loggedin_basket
                line.save()
            anonymous_basket.delete()
            request.basket = loggedin_basket
            logger.info("Merged basket to id %d", loggedin_basket.id)
        except basket.DoesNotExist:
            anonymous_basket.user = user
            anonymous_basket.save()
            logger.info("Assigned user to basket id %d", anonymous_basket.id)
