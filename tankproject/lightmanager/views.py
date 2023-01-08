from django.http import HttpResponse, HttpResponseRedirect
from lightmanager import models
from lightmanager import realpca, mockpca
from lightmanager import requestparser
import time
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
    return set_default_brightness(load_options(request))


def set_default_brightness(options):
    logger.log(datetime.datetime.now())
    # like request_by..., but with options.default filled in
    brightness_by_channel_id = {}
    color_abbreviations = models.get_color_abbreviations()
    color_by_abbreviation = requestparser.get_time_of_day_color_by_abbreviation(models)
    for channel_id in models.CHANNEL_IDS:

        if options.schedule:
            color_abbreviation = color_abbreviations[channel_id]
            brightness = color_by_abbreviation.get(color_abbreviation, 0)
        else:
            brightness = options.request_brightness_by_channel_id.get(channel_id)

        key_missing = brightness is None
        if key_missing and options.only:
            continue
        value_missing = brightness == ""
        if key_missing or value_missing:
            brightness = options.default

        brightness = float(brightness)
        brightness_by_channel_id[channel_id] = brightness

    milli_percent_by_color_abbreviation = pca.set_brightnesses(
        brightness_by_channel_id, relative=options.relative, scale=options.scale, delay=options.delay
    )
    response_str = f"Setting channels: {milli_percent_by_color_abbreviation}"
    logger.log(response_str)

    return HttpResponse(response_str)


def warmer(request):
    return color_temp_adjust(request, True)


def cooler(request):
    return color_temp_adjust(request, False)


def color_temp_adjust(request, is_warmer):
    options = load_options(request)
    # ignore many options
    # TODO: support relative and overrides and such.
    # will require factoring out more of `set_default_brightness`
    # TODO: pause schedule or something if manual used
    assert options.default
    options.default = float(options.default)
    options.brightness_by_channel_id = {
        k: get_temp_adjust_factor(k, default, is_warmer) for k in models.CHANNEL_IDS
    }
    return set_default_brightness(options)


def get_temp_adjust_factor(channel_id, factor, is_warmer):
    exponent = 1 if is_warmer else -1
    if models.is_warm(channel_id):
        return factor**exponent
    if models.is_cool(channel_id):
        return factor ** (-exponent)
    return 1
