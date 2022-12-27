import time
import traceback
import utils
import pca

imported = False
DEBUG = False


def debug(*x):
    if DEBUG:
        print(*x)


# TODO: move into a utils.Timer class or otherwise DRY
def get_elapsed_time(show=True):
    now = time.time()
    delta = now - get_elapsed_time.t
    get_elapsed_time.t = now
    if show:
        debug("elapsed time: ", delta)
    return delta


get_elapsed_time.t = time.time()


def import_all():
    global imported, board, busio, adafruit_pca9685
    if imported:
        return True

    try:
        import board
        import busio
        import adafruit_pca9685

        imported = True
    except Exception:
        traceback.debug_exc()

    return imported


def create_hardware_pca():
    if not import_all():
        debug("failed to get pca")
        return

    i2c_bus = busio.I2C(board.SCL, board.SDA)
    self.hardware_pca = adafruit_pca9685.PCA9685(i2c_bus)
    self.hardware_pca.frequency = pca.FREQUENCY
    debug("made new pca, returning: ", self.hardware_pca)


class PCA(pca.AbstractPCA):
    def get_pca(self, frequency=None):
        if self.hardware_pca:
            debug("already initialized pca, returning", self.hardware_pca)
            return self.hardware_pca
        self.hardware_pca = create_hardware_pca()
        return self.hardware_pca

    def set_brightness(
        self, channel, milli_percent, relative=False, scale=False, channels=None
    ):
        duty_cycle = pca.to_duty_cycle(milli_percent)
        debug(
            "chan, mp, dc, relative, scale",
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

        duty_cycle = pca.bound_duty(int(duty_cycle))
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
            set_brightness(cid, mp, relative, scale, channels)
