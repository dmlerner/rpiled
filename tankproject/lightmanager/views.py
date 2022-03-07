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

def get_only(request):
    return get_default_false(request, 'only')

def get_relative(request):
    return get_default_false(request, 'relative')

def get_scale(request):
    return get_default_false(request, 'scale')

def get_default_false(request, key):
    x = request.GET.get(key.lower(), None)
    return str(x).lower() in ('true', '1', '')

def set_brightnesses(request):
    milli_percents = {}
    # first, load the current channel states (brightnesses)
    default = request.GET.get('default', 0)
    only = get_only(request) # defaults to false
    relative = get_relative(request) # defaults to false
    scale = get_scale(request) # defaults to false
    print(f'default={default}')
    print(f'only={only}')
    for channel_id in models.CHANNEL_IDS: 
        milli_percent = get_brightness(request, channel_id)
        print(f'channel_id={channel_id}')
        print(f'milli_percent={milli_percent}')

        key_missing = milli_percent is None
        if key_missing and only:
            continue
        value_missing = milli_percent == ''
        if key_missing or value_missing:
            milli_percent = default

        milli_percent = float(milli_percent)
        try:
            print('set', channel_id, milli_percent)
            channel = models.get_channel(channel_id)
            milli_percents[channel_id] = milli_percent
            if scale:
                channel.milli_percent *= milli_percent # TODO awkwardly not milli
            elif relative:
                channel.milli_percent += milli_percent
            else:
                channel.milli_percent = milli_percent
        except Exception as e:
            print(e)
            print('skip', channel_id, milli_percent)

    pcanew.set_brightnesses(milli_percents, relative=relative, scale=scale)
    return HttpResponse(f'Setting channels: {milli_percents}')

def get_brightness(request, channel_id):
    keys, channel = models.get_keys_and_channel(channel_id)
    bs = [request.GET.get(str(k), None) for k in keys]
    bs = [b for b in bs if b is not None]
    assert len(bs) <= 1
    if len(bs) == 1:
        return bs.pop()


