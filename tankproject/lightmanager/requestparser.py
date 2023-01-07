from django.http import HttpResponse
import datetime


from lightmanager import mylogger
logger = mylogger.Logger()

def get_only(request):
    return get_default_false(request, "only")


def get_relative(request):
    return get_default_false(request, "relative")


def get_scale(request):
    return get_default_false(request, "scale")

def get_schedule(request):
    return get_default_false(request, "schedule")


def get_default_false(request, key):
    x = request.GET.get(key.lower(), None)
    return str(x).lower() in ("true", "1", "")


def load_options(request, models):
    default = request.GET.get("default", 0)
    only = get_only(request)  # defaults to false
    relative = get_relative(request)  # defaults to false
    scale = get_scale(request)  # defaults to false
    request_brightness_by_channel_id = {
        channel_id: get_request_brightness(request, channel_id, models)
        for channel_id in models.CHANNEL_IDS
    }
    schedule = get_schedule(request)
    logger.log(f'{default=}')
    logger.log(f'{only=}')
    logger.log(f'{relative=}')
    logger.log(f'{scale=}')
    logger.log(f'{request_brightness_by_channel_id=}')
    logger.log(f'{schedule=}')
    assert not (schedule and only)
    return default, only, relative, scale, request_brightness_by_channel_id, schedule



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

MIDNIGHT = datetime.datetime.combine(
    datetime.date.today(), datetime.datetime.min.time()#, tzinfo=pytz.reference.LocalTimezone()
)
def get_time_of_day_color_by_abbreviation():
    abbreviations = models.get_color_abbreviations()
    now = datetime.datetime.now()
    t = now - MIDNIGHT
    if t < datetime.timedelta(hours=6):
        return { abbr: 0 for abbr in abbreviations }

    sunrise = 'sw r ww'.split()
    if t < datetime.timedelta(hours=6, minutes=15):
        return { abbr: 10 for abbr in sunrise }
    if t < datetime.timedelta(hours=6, minutes=30):
        return { abbr: 20  for abbr in sunrise }
    if t < datetime.timedelta(hours=7):
        return { abbr: 40  for abbr in sunrise }

    cool_multipliers = { 'g': .5, 'ww': .5, v: 2, r: 2, b: 2 }
    proportion = t/datetime.timedelta(hours=5)
    max_brightness = 10000/max(cool_multipliers.values())
    baseline = proportion*max_brightness
    if t < datetime.timedelta(hours=12):
        return { abbr: cool_multipliers.get(abbr, 1) * baseline for abbr in abbreviations }

    proportion = 2 - proportion
    baseline = proportion*max_brightness
    min_brightness = 40
    # warm_multipliers = { 'g': .5, 'ww': .5, v: 2, r: 2, b: 2 }
    if t < datetime.timedelta(hours=21):
        # at 17 it hits min
        return { abbr: max(min_brightness, cool_multipliers.get(abbr, 1) * baseline) for abbr in abbreviations }

    if t < datetime.timedelta(hours=21):
        return { abbr: 40  for abbr in sunrise }
    if t < datetime.timedelta(hours=22):
        return { abbr: 20  for abbr in sunrise }
    if t < datetime.timedelta(hours=22, minutes=30):
        return { abbr: 20  for abbr in sunrise }
    return { abbr: 0 for abbr in abbreviations }
