import time
import traceback
imported = False

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
        traceback.print_exc()

    return imported

#pca = None
MAX_DUTY_CYCLE = 2**16-1
PCA = None

def get_pca(frequency=None):
    global PCA
    if PCA:
        print('already initialized pca, returning', PCA)
        return PCA

    #global pca
    #if not pca:
    if not import_all():
        print('failed to get pca')
        return
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    PCA = adafruit_pca9685.PCA9685(i2c_bus)
    PCA.frequency = 2441

    #if frequency is not None and pca.frequency != frequency:
        #print('setting freq', frequency)
        #pca.frequency = frequency
    print('made new pca, returning: ', PCA)
    return PCA

def myround(x):
    if x < .1:
        return round(x, 2)
    if x < 1:
        return round(x, 1)
    return round(x)

def bound_duty(d):
    return max(0, min(MAX_DUTY_CYCLE, d))

MILLI = 100 # TODO RENAME
def to_duty_cycle(milli_percent):
    proportion = float(milli_percent)/100/MILLI
    raw_duty_cycle = proportion * MAX_DUTY_CYCLE
    print('rdc, prop', raw_duty_cycle, proportion)
    return bound_duty(int(raw_duty_cycle))

def to_milli_percent(duty_cycle):
    return float(duty_cycle) / (2**16-1)*100*MILLI

def set_brightness(channel, milli_percent):
    duty_cycle = to_duty_cycle(milli_percent)
    print('chan, mp, dc', channel, milli_percent, duty_cycle)
    pca = get_pca()
    if not pca:
        return
    before = [c.duty_cycle for c in pca.channels]
    print(pca.channels[channel].duty_cycle, duty_cycle)
    if abs(pca.channels[channel].duty_cycle/(duty_cycle+.0000001) - 1) < .005:
        print('no change')
        return
    pca.channels[channel].duty_cycle = duty_cycle
    after = [c.duty_cycle for c in pca.channels]
    print(before)
    print(after)
    #assert before != after

def set_brightnesses(milli_percents):
    print('set_brightnesses', milli_percents)
    pca = get_pca()
    if not pca:
        print('not pca')
        return

    before = {i:c.duty_cycle for (i, c) in enumerate(pca.channels)}
    want = {cid: to_duty_cycle(milli_percents[cid]) for cid in milli_percents}
    return
    for i, c in enumerate(pca.channels):
        if i in want:
            # prevents flashing
            if c.duty_cycle != want[i]:
                print(f'setting channel {i} = {want[i]}')
                c.duty_cycle = want[i]
    return [c.duty_cycle for c in pca.channels]

