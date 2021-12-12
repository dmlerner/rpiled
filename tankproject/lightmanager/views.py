from django.http import HttpResponse
from . import models
import board
import busio
import adafruit_pca9685

pca = None

def get_pca():
    global pca
    if pca:
        return pca

    pca_model = models.PCA9685.get_or_create()
    i2c_bus = busio.I2C(busio.SCL, busio.SDA)
    pca = adafruit_pca9685.PCA9685(i2c_bus)
    return pca


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def set_brightness(request, channel_id, brightness_percent):
    pca = get_pca()
    channel = PWMChannel.get_or_create(channel_id)
    channel.set_percent(brightness_percent, pca)
    print(channel_id, brightness_percent)
    return HttpResponse(f'Setting channel {channel_id} to {brightness_percent}%')
