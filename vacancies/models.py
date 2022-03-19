from django.db import models


class Vacancies(models.Model):
    name = models.CharField(max_length=255, null=False)
    salary = models.CharField(max_length=80, default='')
    min = models.PositiveIntegerField(default=0)
    max = models.PositiveIntegerField(default=0)
    cur = models.CharField(max_length=20)
    link = models.URLField(max_length=255)

    def __str__(self):
        return self.name
