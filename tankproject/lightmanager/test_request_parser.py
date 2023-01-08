from dataclasses import dataclass
from django.http import HttpRequest
from lightmanager import pca
from lightmanager import utils
from lightmanager import timesource
from lightmanager import requestparser
from lightmanager import views
from django.test import TestCase, Client
from lightmanager.models import PWMChannel, PCA9685
import lightmanager.models as models
import datetime


def verify(actual, expected):
    if actual == expected:
        return
    print(actual, expected)
    assert False


def to_abbr_dict(milli_percents):
    return dict(zip(("v", "r", "g", "a", "sw", "cw", "ww", "b"), milli_percents))


class MyTestCase(TestCase):
    def setUp(self):
        pca = PCA9685.objects.create()
        # TODO: check order
        colors = "violet,red,green,amber,spot white,cool white,warm white,blue".split(
            ","
        )
        # TODO: set the 1000s
        currents = (700,) * 8
        abbreviations = "v,r,g,a,sw,cw,ww,b".split(",")
        assert len(colors) == len(currents) == len(abbreviations)
        for i in range(len(colors)):
            PWMChannel.objects.create(
                controller=pca,
                index=i,
                milli_percent=0,
                color=colors[i],
                driver_current=currents[i],
                color_abbreviation=abbreviations[i],
            )

    def test_default_brightness(self):
        request = HttpRequest()
        request.method = "GET"
        default = "2"
        request.GET = {"default": default}

        options = requestparser.load_options(request, models)

        verify(options, requestparser.Options(default=default))

    def test_delay(self):
        request = HttpRequest()
        request.method = "GET"
        delay = 0.5
        request.GET = {"delay": delay}

        options = requestparser.load_options(request, models)

        verify(options, requestparser.Options(delay=delay))
