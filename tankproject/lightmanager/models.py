from django.db import models

# Create your models here.

def bound_duty(d):
    return max(0, min(2**16-1, d))
def to_duty_cycle(percent):
    return bound_duty(int(float(percent)/100*(2**16-1)))
def to_percent(duty_cycle):
    return float(duty_cycle) / (2**16-1)*100

def myround(x):
    if x < .1:
        return round(x, 2)
    if x < 1:
        return round(x, 1)
    return round(x)

class PCA9685(models.Model):
    frequency = models.IntegerField(default=2441)

class PWMChannel(models.Model):
    controller = models.ForeignKey(PCA9685, on_delete=models.CASCADE)
    index = models.IntegerField(unique=True)
    duty_cycle = models.IntegerField(default=0)
    color = models.CharField()
    driver_current = models.IntegerField(default=700) # mA
    color_abbreviation = models.CharField()

    def get_percent(self):
        return self.duty_cycle # TODO

    def set_percent(self, p, pca):
        self.duty_cycle = to_duty_cycle(p)
        pca.channels[self.index].duty_cycle = self.duty_cycle

    def __str__(self):
        return ' | '.join(map(str, (self.color, round(self.get_percent()))))

    '''
    '''

