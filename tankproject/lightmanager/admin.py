from django.contrib import admin

# Register your models here.

from .models import PCA9685, PWMChannel

admin.site.register(PCA9685)
admin.site.register(PWMChannel)
