import time
import traceback
import utils

imported = False
DEBUG = False

def debug(*x):
    if DEBUG:
        print(*x)

def get_elapsed_time(show=True):
    now = time.time()
    delta = now - get_elapsed_time.t
    get_elapsed_time.t = now
    if show:
        debug('elapsed time: ', delta)
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

#pca = None
MAX_DUTY_CYCLE = 2**16-1
PCA = None

def get_pca(frequency=None):
    global PCA
    if PCA:
        debug('already initialized pca, returning', PCA)
        return PCA

    #global pca
    #if not pca:
    if not import_all():
        debug('failed to get pca')
        return
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    PCA = adafruit_pca9685.PCA9685(i2c_bus)
    PCA.frequency = 2441

    #if frequency is not None and pca.frequency != frequency:
        #debug('setting freq', frequency)
        #pca.frequency = frequency
    debug('made new pca, returning: ', PCA)
    return PCA

def bound_duty(d):
    return max(0, min(MAX_DUTY_CYCLE, d))

MILLI = 100 # TODO RENAME
def to_duty_cycle(milli_percent):
    proportion = float(milli_percent)/100/MILLI
    raw_duty_cycle = proportion * MAX_DUTY_CYCLE
    debug('rdc, prop', raw_duty_cycle, proportion)
    return raw_duty_cycle

def to_milli_percent(duty_cycle):
    return float(duty_cycle) / (2**16-1)*100*MILLI

def set_brightness(channel, milli_percent, relative=False, scale=False, pca=None):
    duty_cycle = to_duty_cycle(milli_percent)
    debug('chan, mp, dc, relative, scale', channel, milli_percent, duty_cycle, relative, scale)

    pca = pca or get_pca()
    if not pca:
        return

    duty_cycle_before = pca.channels[channel].duty_cycle
    assert not (relative and scale)
    if relative:
        duty_cycle += duty_cycle_before
    if scale:
        duty_cycle = duty_cycle_before * milli_percent

    duty_cycle = bound_duty(int(duty_cycle))
    if utils.close(duty_cycle, duty_cycle_before):
        return

    pca.channels[channel].duty_cycle = duty_cycle
    #after = [c.duty_cycle for c in pca.channels]
    #debug(before)
    #debug(after)
    get_elapsed_time()
    #assert before != after

def set_brightnesses(milli_percents, relative=False, scale=False):
    debug('set_brightnesses', milli_percents)
    pca = get_pca()
    if not pca:
        debug('not pca')
        return

    for cid, mp in milli_percents.items():
        set_brightness(cid, mp, relative, scale, pca)
