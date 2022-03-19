from django.db import models

# Create your models here.

CHANNEL_IDS = range(8)

class PCA9685(models.Model):
    frequency = models.IntegerField(default=2441)

class PWMChannel(models.Model):
    controller = models.ForeignKey(PCA9685, on_delete=models.CASCADE)
    index = models.IntegerField(unique=True) # TODO rename channel_id
    milli_percent = models.IntegerField(default=0)
    color = models.CharField(max_length=30)
    driver_current = models.IntegerField(default=700) # mA
    color_abbreviation = models.CharField(max_length=20)

    def __str__(self):
        return ' | '.join(map(str, (self.color, self.color_abbreviation, round(self.milli_percent))))

def get_color_map():
    color_map = {}
    for channel_id in CHANNEL_IDS:
        channel = get_channel(channel_id)
        for k in get_keys(channel_id):
            color_map[k] = channel
        color_map[channel.color] = color_map[channel.color_abbreviation] = color_map[channel_id] = channel
    return color_map

def get_channel(channel_id):
    channel, created = PWMChannel.objects.get_or_create(index=channel_id)
    assert not created
    return channel

def get_keys_and_channel(k):
    ''' k is a color, color abbreviation, or channel index '''
    for channel_id in CHANNEL_IDS:
        channel = get_channel(channel_id)
        keys = get_keys(channel)
        if k in keys:
            return keys, channel

def get_all_keys_and_channels():
    return {k: get_keys_and_channel(k) for k in CHANNEL_IDS}

def get_brightnesses():
    return {k: get_channel(k).milli_percent for k in CHANNEL_IDS}

def get_keys(channel):
    return channel.index, channel.color, channel.color_abbreviation
