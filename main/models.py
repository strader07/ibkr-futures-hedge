
from django.db import models


class Position(models.Model):
    name = models.CharField(max_length=512, null=True, blank=True, verbose_name='Name')
    is_active = models.BooleanField(default=False, verbose_name='Active')
    symbol = models.CharField(max_length=512, null=True, blank=True, verbose_name='Symbol')
    num_contract = models.IntegerField(default=3, verbose_name='Num. Contract')
    tick = models.FloatField(null=True, blank=True, verbose_name="Tick Size")

    long_dpp = models.FloatField(null=True, blank=True, verbose_name="DPP For Long")
    long_dpp_up = models.IntegerField(default=4, verbose_name='Long DPP Up')
    long_dpp_dn = models.IntegerField(default=4, verbose_name='Long DPP Down')
    short_dpp = models.FloatField(null=True, blank=True, verbose_name="DPP For Short")
    short_dpp_up = models.IntegerField(default=4, verbose_name='Short DPP Up')
    short_dpp_dn = models.IntegerField(default=4, verbose_name='Short DPP Down')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name='Updated At')
