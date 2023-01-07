import time
import traceback
from lightmanager import utils

from lightmanager import mylogger
logger = mylogger.Logger()

MAX_DUTY_CYCLE = 2**16 - 1
FREQUENCY = 2441


class BasePCA:
    def __init__(self, models):
        self._pca = None
        self.models = models

    def get_pca(self):
        return self._pca

    def set_brightness(
        self, channel_id, milli_percent, relative=False, scale=False, channels=None
    ):
        duty_cycle = to_duty_cycle(milli_percent)
        logger.log(
            "channel_id, mp, dc, relative, scale, channels",
            channel_id,
            milli_percent,
            duty_cycle,
            relative,
            scale,
            channels,
        )

        channels = channels or self.get_pca().channels

        # TODO: consider checking DB instead for performance.
        # hm, but not as accurate - what if external change happened?
        duty_cycle_before = channels[channel_id].duty_cycle
        assert not (relative and scale)
        if relative:
            duty_cycle += duty_cycle_before
        if scale:
            duty_cycle = duty_cycle_before * milli_percent

        duty_cycle = bound_duty(int(duty_cycle))
        channel = self.models.get_channel(channel_id)
        update = not utils.close_rel(duty_cycle, duty_cycle_before)
        if update:
        # TODO: try except?
            channel.milli_percent = to_milli_percent(duty_cycle)
            channel.save()

        get_elapsed_time()
        # assert before != after

        return channel.color_abbreviation, channel.milli_percent, duty_cycle, update


    def set_brightnesses(self, milli_percents, relative=False, scale=False):
        logger.log("set_brightnesses", milli_percents)
        channels = self.get_pca().channels

        milli_percent_by_color_abbreviation = {}
        update_duty_cycle_by_cid = {}

        for cid, mp in milli_percents.items():
            color_abbreviation, milli_percent, duty_cycle, update = self.set_brightness(cid, mp, relative, scale, channels)
            if update:
                update_duty_cycle_by_cid[cid] = duty_cycle
            milli_percent_by_color_abbreviation[color_abbreviation] = milli_percent

        # set all at once in tight loop to make transition fast
        # TODO: threads? is it even thread safe under the hood? different addresses, so hopefully...
        for channel_id, duty_cycle in update_duty_cycle_by_cid.items():
            channels[channel_id].duty_cycle = duty_cycle

        logger.log(milli_percent_by_color_abbreviation)

        return milli_percent_by_color_abbreviation

    def get_duty_cycles(self):
        return [channel.duty_cycle for channel in self.get_pca().channels]


def get_elapsed_time(show=True):
    now = time.time()
    delta = now - get_elapsed_time.t
    get_elapsed_time.t = now
    if show:
        logger.log("elapsed time: ", delta)
    return delta


get_elapsed_time.t = time.time()


def bound_duty(d):
    return max(0, min(MAX_DUTY_CYCLE, d))


MILLI = 100  # TODO RENAME


def to_duty_cycle(milli_percent):
    proportion = float(milli_percent) / 100 / MILLI
    raw_duty_cycle = proportion * MAX_DUTY_CYCLE
    logger.log("rdc, prop", raw_duty_cycle, proportion)
    return raw_duty_cycle


def to_milli_percent(duty_cycle):
    return int(round(float(duty_cycle) / (2**16 - 1) * 100 * MILLI))
