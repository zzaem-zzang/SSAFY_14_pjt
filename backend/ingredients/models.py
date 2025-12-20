from django.db import models

class Drug(models.Model):
    name = models.CharField(max_length=100)
    effect = models.TextField(blank=True)
    usage = models.TextField(blank=True)
    warning = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Symptom(models.Model):
    name = models.CharField(max_length=50)
    drugs = models.ManyToManyField(
        'Drug',               
        related_name='symptoms'
    )

    def __str__(self):
        return self.name
