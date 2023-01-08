from django.http import HttpResponse
from lightmanager import timesource
import datetime
from dataclasses import dataclass


from lightmanager import mylogger

logger = mylogger.Logger()
time_source = timesource.TimeSource()

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
    return request.GET.get("delay", 0)


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


# def uhhh(request, channel_id):
#     # not used
#     is_warm = models.is_warm(channel_id)
#     warmer = request.GET.get("warmer", None)
#     cooler = request.GET.get("cooler", None)


def get_time_of_day_color_by_abbreviation(models):
    # TODO: pass in points and have it do linear interpolation
    # or even better, p-nomial interpolation
    # or even allow exponentials
    abbreviations = models.get_color_abbreviations()
    now = time_source.get_now()
    t = now - time_source.get_midnight()
    if t < datetime.timedelta(hours=6):
        return {abbr: 0 for abbr in abbreviations}

    sunrise = "sw r ww".split()
    if t < datetime.timedelta(hours=6, minutes=15):
        return {abbr: 10 * (abbr in sunrise) for abbr in abbreviations}
    if t < datetime.timedelta(hours=6, minutes=30):
        return {abbr: 20 * (abbr in sunrise) for abbr in abbreviations}
    if t < datetime.timedelta(hours=7):
        return {abbr: 40 * (abbr in sunrise) for abbr in abbreviations}

    # linear ramp up from 7-11

    cool_multipliers = {"g": 0.5, "ww": 0.5, "v": 2, "r": 2, "b": 2}
    proportion = (t - datetime.timedelta(hours=7)) / datetime.timedelta(hours=4)
    max_brightness = 10000 / max(cool_multipliers.values())
    baseline = proportion * max_brightness
    if t < datetime.timedelta(hours=11):
        return {
            abbr: cool_multipliers.get(abbr, 1) * baseline for abbr in abbreviations
        }

    # flat peaked 11-13

    if t < datetime.timedelta(hours=13):
        baseline = max_brightness
        return {
            abbr: cool_multipliers.get(abbr, 1) * baseline for abbr in abbreviations
        }

    # linear ramp down 13-21

    proportion = 1 - (t - datetime.timedelta(hours=13)) / datetime.timedelta(hours=8)
    baseline = proportion * max_brightness
    min_brightness = 40
    # warm_multipliers = {"g": 0.5, "ww": 0.5, 'v': 2, 'r': 2, 'b': 2}
    if t < datetime.timedelta(hours=21):
        # at 17 it hits min
        return {
            abbr: max(min_brightness, cool_multipliers.get(abbr, 1) * baseline)
            for abbr in abbreviations
        }

    if t < datetime.timedelta(hours=21):
        return {abbr: 40 for abbr in sunrise}
    if t < datetime.timedelta(hours=22):
        return {abbr: 20 for abbr in sunrise}
    if t < datetime.timedelta(hours=22, minutes=30):
        return {abbr: 20 for abbr in sunrise}
    return {abbr: 0 for abbr in abbreviations}


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
            self.request_brightness_by_channel_id = { i: None for i in range(N_CHANNELS)}


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
