#from django.db import models
from languages.fields import LanguageField
import currencies
from django.contrib.gis.db import models

# Create your models here.
class Provider(models.Model):
    CURRENCIES_CHOICES = ()
    currencies_list = list(currencies.MONEY_FORMATS.keys())
    for elt in currencies_list:
        CURRENCIES_CHOICES += ((elt, elt),)
    name = models.CharField(max_length=250)
    email = models.EmailField(blank=False, unique=True)
    phone = models.CharField(max_length=100)
    language = LanguageField()
    currency = models.CharField(choices=CURRENCIES_CHOICES, max_length=3)
    
    def __str__(self):
        return self.name

class ServiceArea(models.Model):
    provider = models.ForeignKey(
        to=Provider,
        null=False,
        blank=False,
        on_delete=models.PROTECT
    )
    price = models.FloatField()
    area_name = models.CharField(max_length=250)
    area = models.PolygonField()
