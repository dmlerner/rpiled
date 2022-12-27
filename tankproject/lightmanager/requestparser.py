from django.http import HttpResponse
import models
import pca

DEBUG = True


def debug(*x):
    if DEBUG:
        print(*x)


def get_only(request):
    return get_default_false(request, "only")


def get_relative(request):
    return get_default_false(request, "relative")


def get_scale(request):
    return get_default_false(request, "scale")


def get_default_false(request, key):
    x = request.GET.get(key.lower(), None)
    return str(x).lower() in ("true", "1", "")


def load_options(request):
    default = request.GET.get("default", 0)
    only = get_only(request)  # defaults to false
    relative = get_relative(request)  # defaults to false
    scale = get_scale(request)  # defaults to false
    request_brightness_by_channel_id = {
        channel_id: get_request_brightness(request, channel_id)
        for channel_id in models.CHANNEL_IDS
    }
    debug(f"default={default}")
    debug(f"only={only}")
    return default, only, relative, scale, request_brightness_by_channel_id


def get_request_brightness(request, channel_id):
    keys, channel = models.get_keys_and_channel(channel_id)
    bs = [request.GET.get(str(k), None) for k in keys]
    bs = [b for b in bs if b is not None]
    assert len(bs) <= 1
    if len(bs) == 1:
        return bs.pop()


def uhhh(request, channel_id):
    # not used
    is_warm = models.is_warm(channel_id)
    warmer = request.GET.get("warmer", None)
    cooler = request.GET.get("cooler", None)
