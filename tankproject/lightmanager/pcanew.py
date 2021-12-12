import board
import busio
import adafruit_pca9685

pca = None
MAX_DUTY_CYCLE = 2**16-1

def get_pca(frequency=None):
    global pca
    if not pca:
        i2c_bus = busio.I2C(board.SCL, board.SDA)
        pca = adafruit_pca9685.PCA9685(i2c_bus)

    if frequency and pca.frequency != frequency:
        pca.frequency = frequency

    return pca

def myround(x):
    if x < .1:
        return round(x, 2)
    if x < 1:
        return round(x, 1)
    return round(x)

def bound_duty(d):
    return max(0, min(MAX_DUTY_CYCLE, d))

def to_duty_cycle(milli_percent):
    proportion = float(milli_percent)/100/1000
    raw_duty_cycle = proportion * MAX_DUTY_CYCLE
    print('rdc, prop', raw_duty_cycle, proportion)
    return bound_duty(int(raw_duty_cycle))

def to_milli_percent(duty_cycle):
    return float(duty_cycle) / (2**16-1)*100*1000

def set_brightness(channel, milli_percent): 
    duty_cycle = to_duty_cycle(milli_percent)
    print('mp, dc', milli_percent, duty_cycle)
    pca = get_pca()
    pca.channels[channel].duty_cycle = duty_cycle
    return pca
