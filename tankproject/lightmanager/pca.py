import time
import traceback
import utils

DEBUG = False
MAX_DUTY_CYCLE = 2**16 - 1
FREQUENCY = 2441


class AbstractPCA:
    def __init__(self):
        self.hardware_pca = None

    def get_pca(self):
        return self.hardware_pca

    def set_brightness(
        self, channel, milli_percent, relative=False, scale=False, pca=None
    ):
        pass

    def set_brightnesses(self, milli_percents, relative=False, scale=False):
        pass


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
