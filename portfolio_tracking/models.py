from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validateTradeType(value:str):
    """Checks the passed in trade type value.

    Validates that the value should be buy or sell.

    Args:
        value: String

    Raises:
        ValidationError: An error occured as value is not valid
    """

    if value!="buy" and value!="sell":
        raise ValidationError(_('Expected value buy or sell not %(value)s'),params={'value':value})


def validatePrice(value:float):
    """Checks the passed in price value.

    Validates that the value should be greater than 0.

    Args:
        value: Float

    Raises:
        ValidationError: An error occured as value is not valid
    """

    if value <= 0:
        raise ValidationError(_('Invalid price, expected value greater the 0'))


def validateShares(value:int):
    """Checks the passed in share value.

    Validates that the value should be greater than 0.

    Args:
        value: Integer

    Raises:
        ValidationError: An error occured as value is not valid
    """

    if value <= 0:
        raise ValidationError(_('Invalid shares, expected value greater than 0'))


class Portfolio(models.Model):
    """Portfolio model class

    Represents a portfolio and helps to create, delete, update and query a portfolio in database.

    Attributes:
        id: An integer representing the index value.
        ticker_symbol: A string representing the ticker symbol to which a portfolio belongs to.
        average_price: A float with 2 decimal places representing the average price of each shares in a portfolio.
        shares: An integer representing the shares count in a portfolio.
    """

    id = models.AutoField(primary_key=True)
    ticker_symbol = models.CharField(max_length=20, unique=True, blank=False, null=False)
    average_price = models.DecimalField(max_digits=99, decimal_places=2, validators=[validatePrice], blank=False, null=False)
    shares = models.PositiveIntegerField(validators=[validateShares], blank=False, null=False)

    def __str__(self) -> str:
        """Representing a portfolio in string

        Returns:
            String value of a portfolio
        """
        return self.ticker_symbol+" "+str(self.average_price)+" "+str(self.shares)


class Trade(models.Model):
    """Trade model class

    Represents a trade and helps to create, delete, update and query a trade in database

    Attributes:
        id: An integer representing the index value.
        timestamp : A string representing the date and time when a trade was last modified. 
        ticker_symbol: A string representing the ticker symbol to which a trade belongs to.
        price: A float with 2 decimal places representing the price of each shares in a trade.
        shares: An integer representing the shares count in a trade.
        trade_type: A string indicating the type of trade which is buy or sell.
    """

    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    ticker_symbol = models.CharField(max_length=20, blank=False, null=False)
    price = models.DecimalField(max_digits=99, decimal_places=2, validators=[validatePrice], blank=False, null=False)
    shares = models.PositiveIntegerField(validators=[validateShares], blank=False, null=False)
    trade_type = models.CharField(max_length=5, validators=[validateTradeType], blank=False, null=False)

    def __str__(self) -> str:
        """Representing a trade in string

        Returns:
            String value of a trade
        """
        return self.ticker_symbol+" "+str(self.shares)+" "+self.trade_type+" "+str(self.price)