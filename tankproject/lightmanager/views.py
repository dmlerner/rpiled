from django.http import HttpResponse, HttpResponseRedirect
from lightmanager import models
from lightmanager import realpca, mockpca
from lightmanager import requestparser
from django.template import loader
import os

import datetime

from lightmanager import mylogger

logger = mylogger.Logger()


def build_pca():
    if "home/david" in os.getcwd():
        logger.log("using mock pca")
        return mockpca.MockPCA(models)
    return realpca.PCA(models)


pca = build_pca()


def index(request):
    template = loader.get_template("lightmanager/index.html")
    channel_ids = models.get_color_abbreviations()
    context = {"channel_ids": channel_ids}
    rendered = template.render(context, request)
    return HttpResponse(rendered)


def load_options(request):
    return requestparser.load_options(request, models)


def set_brightnesses(request):
    # first, load the current channel states (brightnesses)
    options = (
        default,
        only,
        relative,
        scale,
        request_brightness_by_channel_id,
        schedule,
    ) = load_options(request)
    return set_default_brightness(*options)


def set_default_brightness(
    default, only, relative, scale, request_brightness_by_channel_id, schedule
):
    logger.log(datetime.datetime.now())
    # like request_by..., but with default filled in
    brightness_by_channel_id = {}
    color_abbreviations = models.get_color_abbreviations()
    color_by_abbreviation = requestparser.get_time_of_day_color_by_abbreviation(models)
    for channel_id in models.CHANNEL_IDS:
        if schedule:
            color_abbreviation = color_abbreviations[channel_id]
            brightness = color_by_abbreviation.get(color_abbreviation, 0)
        else:
            brightness = request_brightness_by_channel_id.get(channel_id)

        key_missing = brightness is None
        if key_missing and only:
            continue
        value_missing = brightness == ""
        if key_missing or value_missing:
            brightness = default

        brightness = float(brightness)
        brightness_by_channel_id[channel_id] = brightness

    milli_percent_by_color_abbreviation = pca.set_brightnesses(
        brightness_by_channel_id, relative=relative, scale=scale
    )
    response_str = f"Setting channels: {milli_percent_by_color_abbreviation}"
    logger.log(response_str)

    return HttpResponse(response_str)


def warmer(request):
    options = (
        default,
        only,
        relative,
        scale,
        request_brightness_by_channel_id,
        schedule,
    ) = load_options(request)
    # ignore request_brightness_by_channel_id, schedule
    # TODO: support relative and overrides and such.
    # will require factoring out more of `f`
    # TODO: pause schedule or something if manual used
    assert default
    default = float(default)
    warm_brightness = default
    cool_brightness = 1 / default
    brightness_by_channel_id = {
        k: get_warmer_factor(k, default) for k in models.CHANNEL_IDS
    }
    return set_default_brightness(*options[:-1], brightness_by_channel_id)


# TODO: dry
def cooler(request):
    options = (
        default,
        only,
        relative,
        scale,
        request_brightness_by_channel_id,
    ) = load_options(request)
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
    return set_default_brightness(*options[:-1], brightness_by_channel_id)


def get_warmer_factor(channel_id, factor):
    if models.is_warm(channel_id):
        return factor
    if models.is_cool(channel_id):
        return 1 / factor
    return 1
