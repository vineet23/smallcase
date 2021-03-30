from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Portfolio,Trade
from .serializers import PortfolioSerializer,TradeSerializer


def getSharesAveragePrice(trades):
    shares = 0
    averagePrice = 0
    if len(trades)==0:
        return (shares,averagePrice)
    #initialize shares and average price with the first trade
    shares = trades[0].shares
    averagePrice = trades[0].price
    #for every trade after first one
    for trade in trades[1:]:
        if shares<=0:
            return (shares,averagePrice)
        #trade type is buy then,
        if trade.trade_type == "buy":
            #calaculate weighted average of the previous and current trade
            product = (averagePrice*shares)+(trade.price*trade.shares)
            shares+=trade.shares
            averagePrice = round(product/shares,2)
        #trade type is sell then update the shares
        else:
            shares-=trade.shares
    return (shares,averagePrice)


def updatePortfolio(trade):
    #get the portfolio with the help of ticker symbol in trade
    try:
        portfolio = Portfolio.objects.get(ticker_symbol=trade.ticker_symbol)
    #if portfolio does not exists
    except Portfolio.DoesNotExist:
        #check if trade type is sell then return false as it is not possible to sell on non existing portfolio
        if trade.trade_type == "sell":
            return False
        #create data to create a portfolio for ticker symbol
        data = {}
        data['average_price'] = trade.price
        data['ticker_symbol'] = trade.ticker_symbol
        data['shares'] = trade.shares
        #pass the data to portfolio serializer
        portfolioSerializer = PortfolioSerializer(data=data)
        #if data is valid then save the portfolio and return true
        if portfolioSerializer.is_valid():
            portfolio = portfolioSerializer.save()
            return True
        #data is invalid, return false
        return False
    #if portfolio already exists 
    try:
        #get all the trades for the given ticker symbol
        trades = Trade.objects.filter(ticker_symbol=trade.ticker_symbol)[::1]
        #get the shares and average price from the passed in trades
        shares,averagePrice = getSharesAveragePrice(trades)
        if shares<=0:
            return False
        #update the selected portfolio with new shares and average price and return true
        portfolio.shares=shares
        portfolio.average_price= averagePrice
        portfolio.save()
        return True
    #if no trade exists, return false
    except (Trade.DoesNotExist,IndexError):
        return False



class AddTradeView(APIView):

    def post(self,request):
        #get the data from the request
        data = request.data.copy()
        #create a trade serializer with data and check if data is valid
        serializer = TradeSerializer(data=data)    
        if serializer.is_valid():
            #save and get the trade object
            trade = serializer.save()
            #check if addition of trade is valid 
            if(updatePortfolio(trade)):
                return Response(serializer.data)
            #if not then delete the saved trade
            trade.delete()
            return Response({'error':'trade adding not possible'},status=400)
        #if data is not valid return the errors
        return Response(serializer.errors,status=400)    
        


class TradeView(APIView):

    def getTrade(self,id):
        try:
            return Trade.objects.get(id=id)
        except Trade.DoesNotExist:
            raise Http404

    def get(self,request,id,format=None):
        trade = self.getTrade(id)
        serializer = TradeSerializer(trade)
        return Response(serializer.data)

    def put(self,request,id,format=None):
        #get the trade and create a copy of old data
        trade = self.getTrade(id)
        oldTradeData = TradeSerializer(trade).data.copy()
        #update the trade and check if data is valid
        serializer = TradeSerializer(trade, data=request.data, partial=True)
        if serializer.is_valid():
            #save and get the updated trade object
            newTrade = serializer.save()
            #check if trade update is valid
            if(updatePortfolio(newTrade)):
                return Response(serializer.data)
            #if not then revert the updated trade to old one
            newSerializer = TradeSerializer(newTrade, data=oldTradeData)
            if newSerializer.is_valid():
                newSerializer.save()
            return Response({'error':'trade update not possible'},status=400)
        #if data is not valid return the errors
        return Response(serializer.errors,status=400)

    def delete(self,request,id,format=None):
        trade = self.getTrade(id)
        serializer = TradeSerializer(trade)
        trade.delete()
        return Response(serializer.data)

