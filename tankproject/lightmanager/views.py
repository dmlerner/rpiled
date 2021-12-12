from django.http import HttpResponse
from . import models
from . import pcanew


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def set_brightness(request, channel_id, milli_percent):
    channel, created = models.PWMChannel.objects.get_or_create(index=channel_id)
    channel.milli_percent = milli_percent
    pcanew.set_brightness(channel.index, milli_percent)
    channel.save()
    print(channel_id, milli_percent)
    return HttpResponse(f'Setting channel {channel_id} to {milli_percent}%')
