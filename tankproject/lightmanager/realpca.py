import time
import traceback
from lightmanager import utils
from lightmanager import pca

imported = False

from lightmanager import mylogger
logger = mylogger.Logger()

# TODO: move into a utils.Timer class or otherwise DRY
def get_elapsed_time(show=True):
    now = time.time()
    delta = now - get_elapsed_time.t
    get_elapsed_time.t = now
    if show:
        logger.log("elapsed time: ", delta)
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
    except Exception as e:
        traceback.print_exception(e)
        raise

    return imported


def create_hardware_pca():
    if not import_all():
        logger.log("failed to get pca")
        return

    i2c_bus = busio.I2C(board.SCL, board.SDA)
    hardware_pca = adafruit_pca9685.PCA9685(i2c_bus)
    hardware_pca.frequency = pca.FREQUENCY
    logger.log("made new pca, returning: ", hardware_pca)
    return hardware_pca


class PCA(pca.BasePCA):
    def get_pca(self, frequency=None):
        if self._pca:
            logger.log("already initialized pca, returning", self._pca)
            return self._pca
        self._pca = create_hardware_pca()
        return self._pca

