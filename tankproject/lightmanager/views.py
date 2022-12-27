from django.http import HttpResponse
from . import models
from . import pca
from . import requestparser

DEBUG = True


def debug(*x):
    if DEBUG:
        print(*x)


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def set_brightnesses(request):
    # first, load the current channel states (brightnesses)
    options = (
        default,
        only,
        relative,
        scale,
        request_brightness_by_channel_id,
    ) = requestparser.load_options(request)
    return f(*options)


# TODO: rename stuff
def f(default, only, relative, scale, request_brightness_by_channel_id):
    milli_percents = {}
    for channel_id in models.CHANNEL_IDS:
        milli_percent = request_brightness_by_channel_id.get(channel_id)
        debug(f"channel_id={channel_id}")
        debug(f"milli_percent={milli_percent}")

        key_missing = milli_percent is None
        if key_missing and only:
            continue
        value_missing = milli_percent == ""
        if key_missing or value_missing:
            milli_percent = default

        milli_percent = float(milli_percent)
        try:
            debug("set", channel_id, milli_percent)
            channel = models.get_channel(channel_id)
            milli_percents[channel_id] = milli_percent
            if scale:
                channel.milli_percent *= milli_percent  # TODO awkwardly not milli
            elif relative:
                channel.milli_percent += milli_percent
            else:
                channel.milli_percent = milli_percent
            channel.save()
        except Exception as e:
            debug(e)
            debug("skip", channel_id, milli_percent)

    pca.set_brightnesses(milli_percents, relative=relative, scale=scale)

    # TODO: these values are wrong at least sometimes.
    return HttpResponse(f"Setting channels: {models.get_brightnesses()}")


def warmer(request):
    options = (
        default,
        only,
        relative,
        scale,
        request_brightness_by_channel_id,
    ) = requestparser.load_options(request)
    # ignore request_brightness_by_channel_id
    # TODO: support relative and overrides and such.
    # will require factoring out more of `f`
    assert default
    default = float(default)
    warm_brightness = default
    cool_brightness = 1 / default
    brightness_by_channel_id = {
        k: get_warmer_factor(k, default) for k in models.CHANNEL_IDS
    }
    return f(*options[:-1], brightness_by_channel_id)


# TODO: dry
def cooler(request):
    options = (
        default,
        only,
        relative,
        scale,
        request_brightness_by_channel_id,
    ) = requestparser.load_options(request)
    # ignore request_brightness_by_channel_id
    # TODO: support relative and overrides and such.
    # will require factoring out more of `f`
    assert default
    default = float(default)
    warm_brightness = 1 / default
    cool_brightness = default
    # TODO: is_warm is very slow probably
    brightness_by_channel_id = {
        k: 1 / get_warmer_factor(k, default) for k in models.CHANNEL_IDS
    }
    return f(*options[:-1], brightness_by_channel_id)


def get_warmer_factor(channel_id, factor):
    if models.is_warm(channel_id):
        return factor
    if models.is_cool(channel_id):
        return 1 / factor
    return 1
