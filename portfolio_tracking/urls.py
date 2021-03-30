from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (AddTradeView,TradeView)

urlpatterns = [
    path('trade/add/',AddTradeView.as_view(),name="add_trade"),
    path('trade/<int:id>/',TradeView.as_view(),name="trade"),
]
