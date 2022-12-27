from dataclasses import dataclass
import pca
import utils

N_CHANNELS = 8


@dataclass
class MockChannel:
    duty_cycle: int = 0


class MockPCA9685:
    def __init__(self, n=N_CHANNELS, frequency=pca.FREQUENCY):
        self.channels = [MockChannel() for i in range(n)]
        self.frequency = frequency


class MockPCA(pca.BasePCA):
    def __init__(self):
        self.hardware_pca = MockPCA9685()

MILLI = 100 # TODO: change this to 1000?
PERCENT = 100
MILLI_PERCENT = MILLI*PERCENT

def verify(actual, expected, close=True):
    if close:
        if all(utils.close_rel(a, e) for (a, e) in zip(actual, expected)):
            return
    elif actual == expected:
        return
    print(actual, expected)
    assert False

def test_absolute_zero():
    p = MockPCA()
    expected_duty_cycles = [0]*N_CHANNELS
    verify(p.get_duty_cycles(), expected_duty_cycles)

def test_absolute_too_low():
    p = MockPCA()
    expected_duty_cycles = [0]*N_CHANNELS
    p.set_brightness(0, -10, False, False)
    verify(p.get_duty_cycles(), expected_duty_cycles)

def test_absolute_max():
    p = MockPCA()
    expected_duty_cycles = [0]*N_CHANNELS
    p.set_brightness(0, pca.MAX_DUTY_CYCLE, False, False)
    expected_duty_cycles[0] = pca.MAX_DUTY_CYCLE
    verify(p.get_duty_cycles(), expected_duty_cycles)

def test_absolute_too_high():
    p = MockPCA()
    expected_duty_cycles = [0]*N_CHANNELS
    p.set_brightness(0, pca.MAX_DUTY_CYCLE*2, False, False)
    expected_duty_cycles[0] = pca.MAX_DUTY_CYCLE
    verify(p.get_duty_cycles(), expected_duty_cycles)

def test_absolute_happy_path():
    p = MockPCA()
    expected_duty_cycles = [0]*N_CHANNELS

    raw_proportion = .5
    brightness = raw_proportion * MILLI_PERCENT
    p.set_brightness(0, brightness, False, False)
    expected_duty_cycles[0] = pca.MAX_DUTY_CYCLE * raw_proportion
    verify(p.get_duty_cycles(), expected_duty_cycles)

def test_relative():
    pass

def test_scale():
    pass

def test():
    for k, v in globals().items():
        if k.startswith('test_'):
            print(k)
            try:
                v()
                print('passes!')
            except:
                print('fails' + '!'*20)
            print()

if __name__ == '__main__':
    test()
