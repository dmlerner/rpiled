from django.core.management.base import BaseCommand
from lightmanager.models import PWMChannel
from lightmanager import pca

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for c in PWMChannel.objects.all():
            pca.set_brightness(c.index, c.milli_percent)
