from django.db import models

# Create your models here.

class PCA9685(models.Model):
    frequency = models.IntegerField(default=2441)

class PWMChannel(models.Model):
    controller = models.ForeignKey(PCA9685, on_delete=models.CASCADE)
    index = models.IntegerField(unique=True)
    milli_percent = models.IntegerField(default=0)
    color = models.CharField(max_length=30)
    driver_current = models.IntegerField(default=700) # mA
    color_abbreviation = models.CharField(max_length=20)

    def __str__(self):
        return ' | '.join(map(str, (self.color, round(self.milli_percent))))

    '''
    '''

