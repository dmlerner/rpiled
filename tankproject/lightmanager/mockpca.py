from dataclasses import dataclass
import pca

N_CHANNELS = 8


@dataclass
class MockChannel:
    duty_cycle: int = pca.MAX_DUTY_CYCLE


class MockPCA9685:
    def __init__(self, n=N_CHANNELS, frequency=pca.FREQUENCY):
        self.channels = [MockChannel() for i in range(n)]
        self.frequency = frequency


class MockPCA(pca.AbstractPCA):
    def __init__(self):
        self.hardware_pca = MockPCA9685()

    def set_brightness(
        self, channel, milli_percent, relative=False, scale=False, pca=None
    ):
        pass

    def set_brightnesses(self, milli_percents, relative=False, scale=False):
        pass
