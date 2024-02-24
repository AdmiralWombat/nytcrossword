from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Score(models.Model):
    name = models.ForeignKey(Player, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
