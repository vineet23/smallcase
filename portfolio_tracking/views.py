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
        if shares<0:
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


def addTrade(trade,check=False):
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
            #if not check then save the portfolio
            if not (check):
                portfolio = portfolioSerializer.save()
            return True
        #data is invalid, return false
        return False
    #if portfolio already exists 
    try:
        #get all the trades for the given ticker symbol and add the new trade
        trades = Trade.objects.filter(ticker_symbol=trade.ticker_symbol).order_by('id')[::1]
        #if trade id is none i.e adding a trade or else trade is changed(updated)
        if trade.id is None:
            trades.append(trade)
        else:
            for index,t in enumerate(trades):
                if t.id > trade.id:
                    trades.insert(index,trade)
                    break
            #todo check if trade was added
        #get the shares and average price from the passed in trades
        shares,averagePrice = getSharesAveragePrice(trades)
        if shares<0:
            return False
        #if shares is zero then delete the portfolio
        if shares==0:
            #if not check then delete the portfolio
            if not (check):
                portfolio.delete()
            return True
        #if not check then update the portfolio
        if not (check):
            #update the selected portfolio with new shares and average price and return true
            portfolio.shares=shares
            portfolio.average_price= averagePrice
            portfolio.save()
        return True
    #if no trade exists, return false
    except (Trade.DoesNotExist):
        return False


def deleteTrade(trade,check=False):
    #get the portfolio with the help of ticker symbol in trade
    try:
        portfolio = Portfolio.objects.get(ticker_symbol=trade.ticker_symbol)
    except Portfolio.DoesNotExist:
        return True
    try:
        trades = Trade.objects.filter(ticker_symbol=trade.ticker_symbol).order_by('id')[::1]
        for index,t in enumerate(trades):
            if t.id == trade.id:
                trades.pop(index)
                break
        #get the shares and average price from the passed in trades
        shares,averagePrice = getSharesAveragePrice(trades)
        if shares<0:
            return False
        #if shares is zero then delete the portfolio
        if shares == 0:
            #if not check then delete the portfolio
            if not (check):
                portfolio.delete()
            return True
        #if not check then update the portfolio
        if not (check):
            #update the selected portfolio with new shares and average price and return true
            portfolio.shares=shares
            portfolio.average_price= averagePrice
            portfolio.save()
        return True
    #if no trade exists, return false
    except (Trade.DoesNotExist):
        return False


def updateTrade(newTrade,oldTrade):
    #check if ticker symbol is updated
    if newTrade.ticker_symbol == oldTrade.ticker_symbol:
        #get the portfolio with the help of ticker symbol in new trade
        try:
            portfolio = Portfolio.objects.get(ticker_symbol=newTrade.ticker_symbol)
        #if portfolio does not exists
        except Portfolio.DoesNotExist:
            #check if trade type is sell then return false as it is not possible to sell on non existing portfolio
            if newTrade.trade_type == "sell":
                return False
            #create data to create a portfolio for ticker symbol
            data = {}
            data['average_price'] = newTrade.price
            data['ticker_symbol'] = newTrade.ticker_symbol
            data['shares'] = newTrade.shares
            #pass the data to portfolio serializer
            portfolioSerializer = PortfolioSerializer(data=data)
            #if data is valid and old trade update is valid then save the portfolio and return true
            if portfolioSerializer.is_valid():
                portfolio = portfolioSerializer.save()
                return True
            #data is invalid, return false
            return False
        #if portfolio already exists 
        try:
            #get all the trades for the given ticker symbol and add the new trade in ascending id order
            trades = Trade.objects.filter(ticker_symbol=oldTrade.ticker_symbol).order_by('id')[::1]
            #update the old trade with new trade in list of trades
            for index,t in enumerate(trades):
                if t.id == oldTrade.id:
                    trades[index] = newTrade
                    break
            #get the shares and average price from the passed in trades
            shares,averagePrice = getSharesAveragePrice(trades)
            #when shares is less than zero, update not possible
            if shares<0 :
                return False
            #when shares is equal to zero then delete the portfolio
            if shares==0:
                portfolio.delete()
                return True
            #update the selected portfolio with new shares and average price and return true
            portfolio.shares=shares
            portfolio.average_price= averagePrice
            portfolio.save()
            return True
        except Trade.DoesNotExist:
            return False
    #when ticker symbol is updated
    else:
        #check if possible to delete old trade and add new trade in respective portfolio
        if (deleteTrade(oldTrade,check=True) and addTrade(newTrade,check=True)):
            #update respective portfolio and return True
            deleteTrade(oldTrade)
            addTrade(newTrade)
            return True
        return False



class AddTradeView(APIView):

    def post(self,request):
        #get the data from the request
        data = request.data.copy()
        #create a trade serializer with data and check if data is valid
        serializer = TradeSerializer(data=data)    
        if serializer.is_valid():
            #create the trade object
            trade = serializer.create()
            #check if addition of trade is valid 
            if(addTrade(trade)):
                #if valid save the trade
                serializer.save()
                return Response(serializer.data)
            #if not then return error
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
        #get the trade
        trade = self.getTrade(id)
        #update the trade and check if data is valid
        serializer = TradeSerializer(trade, data=request.data, partial=True)
        if serializer.is_valid():
            #create the updated trade object
            newTrade = serializer.create()
            #check if trade update is valid
            if(updateTrade(newTrade,trade)):
                #if valid then update the trade
                serializer.save()
                return Response(serializer.data)
            #if not then return error
            return Response({'error':'trade update not possible'},status=400)
        #if data is not valid return the errors
        return Response(serializer.errors,status=400)

    def delete(self,request,id,format=None):
        #get the trade
        trade = self.getTrade(id)
        serializer = TradeSerializer(trade)
         #check if trade delete is valid
        if(deleteTrade(trade)):
            #if valid then delete the trade and return it
            trade.delete()
            return Response(serializer.data)
        #if not then return error
        return Response({'error':'trade delete not possible'},status=400)

