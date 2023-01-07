from dataclasses import dataclass
from lightmanager import pca
from lightmanager import utils
from django.test import TestCase
from lightmanager.models import PWMChannel, PCA9685
import lightmanager.models as models

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


if __name__ == "__main__":
    test()
