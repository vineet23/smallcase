from rest_framework import serializers
from .models import Trade, Portfolio
from datetime import datetime
from django.utils import timezone

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = "__all__"

class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = "__all__"

    def create(self, validated_data):
        return Trade(**validated_data)

    def update(self, instance, validated_data):
        ticker_symbol = validated_data.get('ticker_symbol',instance.ticker_symbol)
        price = validated_data.get('price',instance.price)
        shares = validated_data.get('shares',instance.shares)
        trade_type = validated_data.get('trade_type',instance.trade_type)
        trade = Trade(id=instance.id,ticker_symbol=ticker_symbol,price=price,shares=shares,
                trade_type=trade_type,timestamp=datetime.now(tz=timezone.utc))
        return trade