from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (AddTradeView, TradeView, PortfolioTradeView, PortfolioView, PortfolioReturnView)

urlpatterns = [
    path('trade/add/',AddTradeView.as_view(),name="add_trade"),
    path('trade/<int:id>/',TradeView.as_view(),name="trade"),
    path('trade/<str:tickerSymbol>/',PortfolioTradeView.as_view(),name="portfolio_trades"),
    path('portfolio/',PortfolioView.as_view(),name="portfolio"),
    path('portfolio/returns/',PortfolioReturnView.as_view(),name="portfolio_return"),
]
