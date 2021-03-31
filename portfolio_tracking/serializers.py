from rest_framework import serializers
from .models import Trade, Portfolio
from datetime import datetime
from django.utils import timezone


class PortfolioSerializer(serializers.ModelSerializer):
    """Serialize the portfolio.

    Serialize the passed in portfolio instance and create, update and delete a portfolio
    with the help of data
    """
    
    class Meta:
        model = Portfolio
        fields = "__all__"


class TradeSerializer(serializers.ModelSerializer):
    """Serialize the trade.

    Serialize the passed in trade instance and create, update and delete a trade
    with the help of data
    """
    
    class Meta:
        model = Trade
        fields = "__all__"

    def create(self, validated_data) -> 'Trade':
        """create a trade object

        Creates a trade object with the help of validated data and returns it

        Returns:
            A trade object
        """
        return Trade(**validated_data)

    def update(self, instance:'Trade', validated_data) -> 'Trade':
        """updates a trade instance

        Creates a new trade object with help of old instance and validated data

        Returns:
            A trade object with updated data
        """

        ticker_symbol = validated_data.get('ticker_symbol',instance.ticker_symbol)
        price = validated_data.get('price',instance.price)
        shares = validated_data.get('shares',instance.shares)
        trade_type = validated_data.get('trade_type',instance.trade_type)
        trade = Trade(id=instance.id,ticker_symbol=ticker_symbol,price=price,shares=shares,
                trade_type=trade_type,timestamp=datetime.now(tz=timezone.utc))
        return trade