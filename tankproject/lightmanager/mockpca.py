from dataclasses import dataclass
from lightmanager import pca
from lightmanager import utils

# TODO: either rename this "local server pca" or merger with test mock pca

N_CHANNELS = 8


@dataclass
class MockChannel:
    # start with a nonzero value to make scale more useful
    duty_cycle: int = 1


class MockChannels(list):
    def get_channel(self, channel_id):
        return self[channel_id]


class MockPCA9685:
    def __init__(self, n=N_CHANNELS, frequency=pca.FREQUENCY):
        self.channels = MockChannels([MockChannel() for i in range(n)])
        self.frequency = frequency


class MockPCA(pca.BasePCA):
    def __init__(self, models):
        self._pca = MockPCA9685()
        self.models = models
