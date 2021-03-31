from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (AddTradeView, TradeView, TradesView, PortfolioTradeView, PortfolioView, PortfolioReturnView)

urlpatterns = [
    # Add a trade.
    # URL -> e.g host/api/trade/add/
    # Methods -> POST
    # Body -> ticker_symbol: str, price: float, shares: int, trade_type: str
    path('trade/add/',AddTradeView.as_view(),name="add_trade"),
    # Get, update or delete a trade with passed in trade id.
    # URL -> e.g host/api/trade/1/
    # Methods -> GET, PUT, DELETE
    # Body (for PUT) -> ticker_symbol: str, price: float, shares: int, trade_type: str
    path('trade/<int:id>/',TradeView.as_view(),name="trade"),
    # Get trades and portfolio for a passed in ticker symbol
    # URL -> e.g host/api/trade/TCS/
    # Methods -> GET
    path('trade/<str:tickerSymbol>/',PortfolioTradeView.as_view(),name="portfolio_trades"),
    # Get trades along with their portfolio
    # URL -> e.g host/api/trades/
    # Methods -> GET
    path('trades/',TradesView.as_view(),name="trades"),
    # Get all the portfolios
    # URL -> e.g host/api/portfolio/
    # Methods -> GET
    path('portfolio/',PortfolioView.as_view(),name="portfolio"),
    # Get returns from the portfolios
    # URL -> e.g host/api/portfolio/returns/
    # Methods -> GET
    path('portfolio/returns/',PortfolioReturnView.as_view(),name="portfolio_return"),
]
