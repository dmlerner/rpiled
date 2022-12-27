import time
import traceback
from lightmanager import utils
from lightmanager import pca

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


class PCA(pca.BasePCA):
    def get_pca(self, frequency=None):
        if self.hardware_pca:
            debug("already initialized pca, returning", self.hardware_pca)
            return self.hardware_pca
        self.hardware_pca = create_hardware_pca()
        return self.hardware_pca

