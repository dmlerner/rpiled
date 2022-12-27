import time
import traceback
import utils

DEBUG = False
MAX_DUTY_CYCLE = 2**16 - 1
FREQUENCY = 2441


class BasePCA:
    def __init__(self):
        self.hardware_pca = None

    def get_pca(self):
        return self.hardware_pca

    def set_brightness(
        self, channel, milli_percent, relative=False, scale=False, channels=None
    ):
        duty_cycle = to_duty_cycle(milli_percent)
        debug(
            "chan, mp, dc, relative, scale, channels",
            channel,
            milli_percent,
            duty_cycle,
            relative,
            scale,
            channels,
        )

        channels = channels or self.get_pca().channels

        duty_cycle_before = channels[channel].duty_cycle
        assert not (relative and scale)
        if relative:
            duty_cycle += duty_cycle_before
        if scale:
            duty_cycle = duty_cycle_before * milli_percent

        duty_cycle = bound_duty(int(duty_cycle))
        if utils.close(duty_cycle, duty_cycle_before):
            return

        channels[channel].duty_cycle = duty_cycle
        # after = [c.duty_cycle for c in pca.channels]
        # debug(before)
        # debug(after)
        get_elapsed_time()
        # assert before != after

    def set_brightnesses(self, milli_percents, relative=False, scale=False):
        debug("set_brightnesses", milli_percents)
        channels = self.get_pca().channels

        for cid, mp in milli_percents.items():
            self.set_brightness(cid, mp, relative, scale, channels)

    def get_duty_cycles(self):
        return [channel.duty_cycle for channel in self.get_pca().channels]


def debug(*x):
    if DEBUG:
        print(*x)


def get_elapsed_time(show=True):
    now = time.time()
    delta = now - get_elapsed_time.t
    get_elapsed_time.t = now
    if show:
        debug("elapsed time: ", delta)
    return delta


get_elapsed_time.t = time.time()


def bound_duty(d):
    return max(0, min(MAX_DUTY_CYCLE, d))


MILLI = 100  # TODO RENAME


def to_duty_cycle(milli_percent):
    proportion = float(milli_percent) / 100 / MILLI
    raw_duty_cycle = proportion * MAX_DUTY_CYCLE
    debug("rdc, prop", raw_duty_cycle, proportion)
    return raw_duty_cycle


def to_milli_percent(duty_cycle):
    return float(duty_cycle) / (2**16 - 1) * 100 * MILLI
