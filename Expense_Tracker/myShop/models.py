from django.db import models

class Succulent(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='succulents/')  
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return self.name


class Pot(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='pots/')  
    material = models.CharField(max_length=100)
    height = models.CharField(max_length=20)
    width = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return self.name

