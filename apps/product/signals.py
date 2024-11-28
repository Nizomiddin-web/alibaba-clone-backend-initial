from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Color,Size

@receiver(signal=pre_save,sender=Color)
def change_color_name_to_lower(sender,instance,**kwargs):
    instance.name=instance.name.lower()
    print("Signal is ready change Color name to lower")

@receiver(signal=pre_save,sender=Size)
def change_size_name_to_lower(sender,instance,**kwargs):
    instance.name=instance.name.lower()
    print("Signal ready change Size name to lower")