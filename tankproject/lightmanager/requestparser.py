from django.http import HttpResponse
from lightmanager import scheduler
from functools import cache
import datetime
from dataclasses import dataclass


from lightmanager import mylogger

logger = mylogger.Logger()

N_CHANNELS = 8


def get_only(request):
    return get_default_false(request, "only")


def get_relative(request):
    return get_default_false(request, "relative")


def get_scale(request):
    return get_default_false(request, "scale")


def get_schedule(request):
    return get_default_false(request, "schedule")


def get_delay(request):
    # don't use get_default_false, since this is something with a value we don't want to set from default
    return float(request.GET.get("delay", 0))


def get_default_false(request, key):
    x = request.GET.get(key.lower(), None)
    return str(x).lower() in ("true", "1", "")


def get_request_brightness(request, channel_id, models):
    keys, channel = models.get_keys_and_channel(channel_id)
    bs = [request.GET.get(str(k), None) for k in keys]
    bs = [b for b in bs if b is not None]
    assert len(bs) <= 1
    if len(bs) == 1:
        return bs.pop()


# TODO: cache?
def get_time_of_day_color_by_abbreviation(models):
    return scheduler.Schedule(models).get()


@dataclass
class Options:
    default: float = 0
    only: bool = False
    relative: bool = False
    scale: bool = False
    request_brightness_by_channel_id: dict = None
    schedule: bool = False
    delay: float = 0

    def __post_init__(self):
        if self.request_brightness_by_channel_id is None:
            self.request_brightness_by_channel_id = {i: None for i in range(N_CHANNELS)}


def load_options(request, models):
    default = request.GET.get("default", 0)
    only = get_only(request)
    relative = get_relative(request)
    scale = get_scale(request)
    request_brightness_by_channel_id = {
        channel_id: get_request_brightness(request, channel_id, models)
        for channel_id in models.CHANNEL_IDS
    }
    schedule = get_schedule(request)
    delay = get_delay(request)
    assert not (schedule and only)

    ret = Options(
        default=default,
        only=only,
        relative=relative,
        scale=scale,
        request_brightness_by_channel_id=request_brightness_by_channel_id,
        schedule=schedule,
        delay=delay,
    )
    logger.log(ret)
    return ret
