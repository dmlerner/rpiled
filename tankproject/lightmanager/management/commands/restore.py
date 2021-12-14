from django.core.management.base import BaseCommand
from lightmanager.models import PWMChannel
from lightmanager import pcanew

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for c in PWMChannel.objects.all():
            pcanew.set_brightness(c.index, c.milli_percent)
