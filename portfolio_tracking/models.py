from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validateTradeType(value):
    if value!="buy" and value!="sell":
        raise ValidationError(_('Expected value buy or sell not %(value)s'),params={'value':value})

def validatePrice(value):
    if value <= 0:
        raise ValidationError(_('Invalid price, expected value greater the 0'))

def validateShares(value):
    if value <= 0:
        raise ValidationError(_('Invalid shares, expected value greater than 0'))

class Portfolio(models.Model):
    id = models.AutoField(primary_key=True)
    ticker_symbol = models.CharField(max_length=20, unique=True, blank=False, null=False)
    average_price = models.DecimalField(max_digits=99, decimal_places=2, validators=[validatePrice], blank=False, null=False)
    shares = models.PositiveIntegerField(validators=[validateShares], blank=False, null=False)

    def __str__(self):
        return self.ticker_symbol+" "+str(self.average_price)+" "+str(self.shares)

class Trade(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    ticker_symbol = models.CharField(max_length=20, blank=False, null=False)
    price = models.DecimalField(max_digits=99, decimal_places=2, validators=[validatePrice], blank=False, null=False)
    shares = models.PositiveIntegerField(validators=[validateShares], blank=False, null=False)
    trade_type = models.CharField(max_length=5, validators=[validateTradeType], blank=False, null=False)

    def __str__(self):
        return self.ticker_symbol+" "+str(self.shares)+" "+self.trade_type+" "+str(self.price)