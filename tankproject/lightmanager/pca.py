import time
import threading

import RPi.GPIO as g
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685

def bound(minimum, maximum, x):
    return min(maximum, max(minimum, x))

class PWMController:
    MAX_DUTY_CYCLE = 2**16-1
    MAX_FREQUENCY = 2441

    def __init__(self, n_channels=8, frequency=PWMController.MAX_FREQUENCY):
        self.pca = PCA9685(busio.I2C(SCL, SDA))
        self.n_channels = n_channels
        self.pca.frequency = frequency

    @staticmethod
    def to_duty_cycle(percent):
        percent = float(percent)
        duty_cycle = percent/100 * PWMController.MAX_DUTY_CYCLE
        return int(bound(0, PWMController.MAX_DUTY_CYCLE, duty_cycle))

    @staticmethod
    def to_percent(duty_cycle):
        duty_cycle = float(duty_cycle)
        percent = duty_cycle/PWMController.MAX_DUTY_CYCLE * 100
        return percent

    def set_brightness(self, percent, *channels):
        for c in channels:
            self[c].brightness = to_duty_cycle(percent)

    def get_channels(self):
        return self.pca.channels[:self.n_channels]

    def __getitem__(self, i):
        return self.get_channels()[i]

    def __iter__(self):
        for channel in self.get_channels()
            yield channel


def smooth_set_brightness(percent, channel, fade_time=1, steps=None, step_time=.01):
    # TODO
    #print('start', channel, int(time.time()%1000))
    if fade_time == 0:
        return set_brightness(percent, channel)

    if steps is None:
        steps = fade_time / step_time

    initial_duty_cycle = pca.channels[channel].duty_cycle
    final_duty_cycle = to_duty_cycle(percent)
    ratio = abs((.000001+initial_duty_cycle)/(.000001+final_duty_cycle))
    #print(initial_duty_cycle, final_duty_cycle, ratio)
    tol = 2e-2
    if 1 - tol < ratio < 1 + tol:
        return
    getting_brighter = final_duty_cycle > initial_duty_cycle
    clip_function = min if getting_brighter else max

    step_duty_cycle = (final_duty_cycle - initial_duty_cycle) / steps
    step_time = fade_time / steps
    for step in range(1, int(steps+1)):
        brightness = step*step_duty_cycle + initial_duty_cycle
        clipped_brightness = clip_function(brightness, final_duty_cycle)
        _set_brightness(brightness, channel)
        time.sleep(step_time)
    #print(final_duty_cycle, clipped_brightness, brightness)
    #print('stop', channel, int(time.time()%1000))

def setall(percent=1, cmax=n_channels):
    for channel in range(cmax):
        set_brightness(percent, channel)

def myround(x):
    if x < .2:
        return round(x, 2)
    if x < 1:
        return round(x, 1)
    return round(x)

def show_all():
    print(pca.channels, len(pca.channels))
    dutys = [c.duty_cycle for c in pca.channels[:n_channels]]
    percents = list(map(to_percent, dutys))
    print('\n'.join([f'{i}:{channel_names[i]}: {myround(p)}%' for (i, p) in enumerate(percents)]))
    print('python3 multichannel.py ' + ' '.join([f'--{channel_names[i]} {myround(p)}' for (i, p) in enumerate(percents)]))

def main():
    if args.test:
        test()
        return

    if args.scale:
        return scale(args.scale)

    threads = []

    brightness = get_channel_order_percents(args)
    for channel, percent in enumerate(brightness):
        t = threading.Thread(target=smooth_set_brightness, args=(percent, channel, args.fadetime))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

def test():
    n_channels = 8
    controller = PWMController(n_channels)
    brightnesses = [0]*n_channels
    controller.set_brightness(0, range(n_channels))
    time.sleep(1)
    for i in range(n_channels):
        brightnesses[i] = 1
        for j, b in enumerate(brightnesses):
            set_brightness(b, j)
        time.sleep(1)
        brightnesses[i] = 0
    setall(0)

def scale(delta):
    factor = 1 + delta
    for i, c in list(enumerate(pca.channels))[:n_channels]:
        _set_brightness(c.duty_cycle * factor, i)

if __name__ == '__main__':
    main()
    show_all()
#io.run(main())
'''
red, spot white, blue, warm white, violet,  amber, green, cool white
'''
