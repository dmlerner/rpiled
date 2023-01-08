from dataclasses import dataclass
from lightmanager import pca
from lightmanager import utils
from lightmanager import timesource
from lightmanager import requestparser
from lightmanager import views
from django.test import TestCase, Client
from lightmanager.models import PWMChannel, PCA9685
import lightmanager.models as models
import datetime

N_CHANNELS = 8


@dataclass
class MockChannel:
    # start with a nonzero value to make scale more useful
    duty_cycle: int = 0


class MockChannels(list):
    def get_channel(self, channel_id):
        return self[channel_id]


class MockPCA9685:
    def __init__(self, n=N_CHANNELS, frequency=pca.FREQUENCY):
        self.channels = MockChannels([MockChannel() for i in range(n)])
        self.frequency = frequency


class MockPCA(pca.BasePCA):
    def __init__(self, models):
        self._pca = MockPCA9685()
        self.models = models


MILLI = 100  # TODO: change this to 1000?
PERCENT = 100
MILLI_PERCENT = MILLI * PERCENT


def verify(actual, expected, close=True):
    if len(actual) == len(expected):
        if isinstance(expected, dict):
            equal_keys = set(actual.keys()) == set(expected.keys())
            if equal_keys:
                return verify(
                    [actual[k] for k in actual], [expected[k] for k in actual], close
                )

        if close:
            if all(utils.close_rel(a, e) for (a, e) in zip(actual, expected)):
                return
        elif actual == expected:
            return
    print(actual, expected)
    assert False


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

    def test_constructs_at_zero(self):
        # behavior set in MockPCA, but consistent with models.py default
        p = MockPCA(models)
        expected_duty_cycles = [0] * N_CHANNELS
        verify(p.get_duty_cycles(), expected_duty_cycles)

    def test_absolute_too_low(self):
        p = MockPCA(models)
        expected_duty_cycles = [0] * N_CHANNELS
        p.set_brightness(0, -10, False, False, flush=True)
        # p.set_brightnesses({i:0 for i in range(8)}, False, False, False)
        verify(p.get_duty_cycles(), expected_duty_cycles)

    def test_absolute_max(self):
        p = MockPCA(models)
        expected_duty_cycles = [0] * N_CHANNELS
        p.set_brightness(0, pca.MAX_DUTY_CYCLE, False, False, flush=True)
        expected_duty_cycles[0] = pca.MAX_DUTY_CYCLE
        verify(p.get_duty_cycles(), expected_duty_cycles)

    def test_absolute_too_high(self):
        p = MockPCA(models)
        expected_duty_cycles = [0] * N_CHANNELS
        p.set_brightness(0, pca.MAX_DUTY_CYCLE * 2, False, False, flush=True)
        expected_duty_cycles[0] = pca.MAX_DUTY_CYCLE
        verify(p.get_duty_cycles(), expected_duty_cycles)

    def test_absolute_happy_path(self):
        p = MockPCA(models)
        expected_duty_cycles = [0] * N_CHANNELS
        raw_proportion = 0.5
        brightness = raw_proportion * MILLI_PERCENT
        p.set_brightness(0, brightness, False, False, flush=True)
        expected_duty_cycles[0] = pca.MAX_DUTY_CYCLE * raw_proportion
        verify(p.get_duty_cycles(), expected_duty_cycles)

    def test_absolute_happy_path_request(self):
        p = MockPCA(models)
        views.pca = p
        raw_proportion = 0.5
        brightness = raw_proportion * MILLI_PERCENT
        expected_duty_cycles = [raw_proportion * 2**16] * N_CHANNELS
        c = Client()

        c.get("/lightmanager/sbs/", {"default": brightness})

        verify(p.get_duty_cycles(), expected_duty_cycles)

    def test_schedule_off_at_night(self):
        requestparser.time_source = timesource.TimeSource(
            mock=True,
            now=datetime.datetime(2023, 1, 7, 4, 0, 0),
            today=datetime.datetime(2023, 1, 7, 1),
        )
        color_by_abbr = requestparser.get_time_of_day_color_by_abbreviation(models)
        verify(list(color_by_abbr.values()), [0] * 8)

    def test_abbreviations(self):
        abbreviations = models.get_color_abbreviations()
        verify(abbreviations, ["v", "r", "g", "a", "sw", "cw", "ww", "b"], False)

    def test_schedule_dim_morning(self):
        abbreviations = models.get_color_abbreviations()
        requestparser.time_source = timesource.TimeSource(
            mock=True,
            now=datetime.datetime(2023, 1, 7, 6, 50, 0),
            today=datetime.datetime(2023, 1, 7, 1),
        )
        color_by_abbr = requestparser.get_time_of_day_color_by_abbreviation(models)
        expected = {abbr: 0 for abbr in abbreviations}
        for abbr in "r sw ww".split():
            expected[abbr] = 40

        verify(color_by_abbr, expected, False)

    def test_schedule_before_peak(self):
        requestparser.time_source = timesource.TimeSource(
            mock=True,
            now=datetime.datetime(2023, 1, 7, 10, 55, 0),
            today=datetime.datetime(2023, 1, 7, 1),
        )
        color_by_abbr = requestparser.get_time_of_day_color_by_abbreviation(models)
        expected = to_abbr_dict(
            [
                9791.666666666666,
                9791.666666666666,
                2447.9166666666665,
                4895.833333333333,
                4895.833333333333,
                4895.833333333333,
                2447.9166666666665,
                9791.666666666666,
            ]
        )

        verify(color_by_abbr, expected, True)

    def test_schedule_on_peak(self):
        requestparser.time_source = timesource.TimeSource(
            mock=True,
            now=datetime.datetime(2023, 1, 7, 12, 00, 0),
            today=datetime.datetime(2023, 1, 7, 1),
        )
        color_by_abbr = requestparser.get_time_of_day_color_by_abbreviation(models)
        expected = to_abbr_dict(
            [10000.0, 10000.0, 2500.0, 5000.0, 5000.0, 5000.0, 2500.0, 10000.0]
        )

        verify(color_by_abbr, expected, True)

    def test_schedule_after_peak(self):
        requestparser.time_source = timesource.TimeSource(
            mock=True,
            now=datetime.datetime(2023, 1, 7, 13, 5, 0),
            today=datetime.datetime(2023, 1, 7, 1),
        )
        color_by_abbr = requestparser.get_time_of_day_color_by_abbreviation(models)
        expected = to_abbr_dict(
            [
                9895.833333333334,
                9895.833333333334,
                2473.9583333333335,
                4947.916666666667,
                4947.916666666667,
                4947.916666666667,
                2473.9583333333335,
                9895.833333333334,
            ]
        )

        verify(color_by_abbr, expected, True)

    def test_near_dark(self):
        requestparser.time_source = timesource.TimeSource(
            mock=True,
            now=datetime.datetime(2023, 1, 7, 20, 50, 0),
            today=datetime.datetime(2023, 1, 7, 1),
        )
        color_by_abbr = requestparser.get_time_of_day_color_by_abbreviation(models)
        expected = to_abbr_dict(
            [
                208.3333333333337,
                208.3333333333337,
                52.08333333333343,
                104.16666666666686,
                104.16666666666686,
                104.16666666666686,
                52.08333333333343,
                208.3333333333337,
            ]
        )

        verify(color_by_abbr, expected, True)

    def test_monotonic(self):
        # TODO: test that pca.set doesn't mess it up further
        now = datetime.datetime(2023, 1, 7, 20, 50, 0)
        last_actual = to_abbr_dict(
            [
                208.3333333333337,
                208.3333333333337,
                52.08333333333343,
                104.16666666666686,
                104.16666666666686,
                104.16666666666686,
                52.08333333333343,
                208.3333333333337,
            ]
        )
        for d_minutes in range(1, 90):
            now += datetime.timedelta(minutes=1)
            requestparser.time_source = timesource.TimeSource(
                mock=True,
                now=now,
                today=datetime.datetime(2023, 1, 7, 1),
            )
            color_by_abbr = requestparser.get_time_of_day_color_by_abbreviation(models)
            for v_last, v_now in zip(last_actual.values(), color_by_abbr.values()):
                assert v_last >= v_now


def test_relative():
    pass


def test_scale():
    pass


def test():
    for k, v in globals().items():
        if k.startswith("test_"):
            print(k)
            try:
                v()
                print("passes!")
            except:
                print("fails" + "!" * 20)
            print()


def to_abbr_dict(milli_percents):
    return dict(zip(("v", "r", "g", "a", "sw", "cw", "ww", "b"), milli_percents))


if __name__ == "__main__":
    test()
