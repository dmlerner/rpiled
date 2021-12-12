from django.db import models

# Create your models here.

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
    duty_cycle = models.IntegerField()
    color = models.CharField()
    driver_current = models.IntegerField()
    color_abbreviation = models.CharField()

    def get_percent(self):
        return self.duty_cycle # TODO

    def set_percent(self, p):
        duty_cycle = PWMChannel.to_duty_cycle(p)
            self.duty_cycle = joi

    def __str__(self):
        return ' | '.join(map(str, (self.color, round(self.get_percent()))))
