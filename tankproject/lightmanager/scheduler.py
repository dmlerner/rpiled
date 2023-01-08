from django.http import HttpResponse
from functools import cache
from lightmanager import timesource
import datetime
from dataclasses import dataclass


from lightmanager import mylogger

logger = mylogger.Logger()
time_source = timesource.TimeSource()

N_CHANNELS = 8


def interpolate(
    t, t1, t2, brightness_by_color_abbreviation1, brightness_by_color_abbreviation2
):
    assert t1 <= t <= t2
    dt = t2 - t1
    p = (t - t1) / dt
    assert (
        brightness_by_color_abbreviation1.keys()
        == brightness_by_color_abbreviation2.keys()
    )
    brightness_by_color_abbreviation = {}
    for k in brightness_by_color_abbreviation1:
        brightness_by_color_abbreviation[k] = (
            1 - p
        ) * brightness_by_color_abbreviation1[
            k
        ] + p * brightness_by_color_abbreviation2[
            k
        ]
    print(f"{ brightness_by_color_abbreviation=}")
    return brightness_by_color_abbreviation


def build_schedule(change_times, brightness_by_color_abbreviations):
    # TODO: nonlinear interpolation
    # can just pass point twice to get constant
    assert change_times == sorted(change_times)
    print(change_times)

    def schedule(t):
        print(t)
        if t <= change_times[0]:
            print("start")
            return brightness_by_color_abbreviations[0]
        for i, change_time in enumerate(change_times):
            if t < change_time:
                print("middle", t, change_time)
                return interpolate(
                    t,
                    change_times[i - 1],
                    change_time,
                    brightness_by_color_abbreviations[i - 1],
                    brightness_by_color_abbreviations[i],
                )

        print("end")
        return brightness_by_color_abbreviations[-1]

    return schedule


def get_time(hour_float):
    return time_source.get_midnight() + datetime.timedelta(hours=hour_float)


def get_time_of_day_color_by_abbreviation(models):
    # TODO: work with times, not datetimes?
    midnight = time_source.get_midnight()
    hours = iter([6, 6.25, 6.5, 7, 11, 13, 18, 21, 22, 22.25, 22.5])
    times = []

    abbreviations = models.get_color_abbreviations()
    brightness_by_color_abbreviations = []

    sunrise = "sw r ww".split()
    for i in range(3):
        h = next(hours)
        brightness = 10 * 2**i
        times.append(get_time(h))
        brightness_by_color_abbreviations.append(
            {abbr: brightness * (abbr in sunrise) for abbr in abbreviations}
        )

    # put in 7 at same brightness to have a short plateau
    times.append(get_time(next(hours)))
    brightness_by_color_abbreviations.append(brightness_by_color_abbreviations[-1])

    # put in 11 as start of peak
    cool_multipliers = {"g": 0.5, "ww": 0.5, "v": 2, "r": 2, "b": 2}
    max_brightness = 10000 / max(cool_multipliers.values())
    times.append(get_time(next(hours)))
    brightness_by_color_abbreviations.append(
        {abbr: cool_multipliers.get(abbr, 1) * max_brightness for abbr in abbreviations}
    )

    # 13 as end of peak plateau
    times.append(get_time(next(hours)))
    brightness_by_color_abbreviations.append(brightness_by_color_abbreviations[-1])

    # linear ramp down 13-18
    times.append(get_time(next(hours)))
    min_brightness = 80
    brightness_by_color_abbreviations.append(
        {abbr: cool_multipliers.get(abbr, 1) * min_brightness for abbr in abbreviations}
    )

    # flat until 21
    times.append(get_time(next(hours)))
    brightness_by_color_abbreviations.append(brightness_by_color_abbreviations[-1])

    for i in range(1, 4):
        brightness = min_brightness / 2**i
        times.append(get_time(next(hours)))
        brightness_by_color_abbreviations.append(
            {abbr: brightness * (abbr in sunrise) for abbr in abbreviations}
        )

    times.insert(0, times[0] - datetime.timedelta(minutes=1))
    times.append(times[-1] + datetime.timedelta(minutes=1))
    off = {abbr: 0 for abbr in abbreviations}
    brightness_by_color_abbreviations.insert(0, off)
    brightness_by_color_abbreviations.append(off)
    return times, brightness_by_color_abbreviations


# TODO: cache?
def get_schedule(models):
    return build_schedule(*get_time_of_day_color_by_abbreviation(models))


class Schedule:
    def __init__(self, models):
        self.schedule = get_schedule(models)
        self.time_source = time_source

    def get(self, t=None):
        t = t or self.time_source.get_now()
        return self.schedule(t)
