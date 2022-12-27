from django.apps import AppConfig
#from . import models


class LightmanagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lightmanager'

    #def ready(self):
        #channels = models.PWMChannel.objects.get()
        #for c in channels:
            #pca.set_channel(c.index, c.milli)
