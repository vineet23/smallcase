from django.http import Http404
from typing import List, Optional
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Portfolio,Trade
from .serializers import PortfolioSerializer,TradeSerializer


def createPortfolioSerializer(price: float ,tickerSymbol: str ,shares: int) -> 'PortfolioSerializer':
    """Create a portfolio serializer object.

    Creates a portfolio serializer object with the help of data passed in as args.

    Args:
        price: A float indicating average price of a portfolio.
        tickerSymbol: A string Representing ticker symbol of a portfolio.
        shares: An integer indicating shares of a portfolio.

    Returns:
        PortfolioSerializer object created using passed data.
    """

    #create data to create a portfolio for ticker symbol
    data = {}
    data['average_price'] = price
    data['ticker_symbol'] = tickerSymbol
    data['shares'] = shares
    return PortfolioSerializer(data=data)


def getSharesAveragePrice(trades: List['Trade']) -> (int,float):
    """Calculate shares and average price for a portfolio with passed in trades.

    Args:
        trades: List of trades for a portfolio.

    Returns:
        A tuple containing calculated shares and average price.
    """

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


def addTrade(trade: 'Trade', check: Optional[bool]= False) -> bool:
    """Add and check if addition of a trade is valid or not.

    Add and check if addition of a trade is possible in a portfolio for a passed
    in trade, if check is true then portfolio is not updated else portfolio is updated with
    new calculated value.

    Args:
        trade: A Trade object to be added.
        check: Optional; A bool to indicate to update portfolio for the given trade or not.

    Returns:
        bool to indicate if addition of trade is possible or not.
    """

    #get the portfolio with the help of ticker symbol in trade
    try:
        portfolio = Portfolio.objects.get(ticker_symbol=trade.ticker_symbol)
    #if portfolio does not exists
    except Portfolio.DoesNotExist:
        #check if trade type is sell then return false as it is not possible to sell on non existing portfolio
        if trade.trade_type == "sell":
            return False
        #create a portfolio for ticker symbol
        portfolioSerializer = createPortfolioSerializer(trade.price, trade.ticker_symbol, trade.shares)
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
            #when new non saved trade is added
            trades.append(trade)
        else:
            #when a saved trade is added, add it according to its id
            for index,t in enumerate(trades):
                if t.id > trade.id:
                    trades.insert(index,trade)
                    break
            #check if trade was added earlier or not
            if (index == len(trades)-1 and trades[-1].id != trade.id):
                trades.append(trade)
        #get the shares and average price from the passed in trades
        shares,averagePrice = getSharesAveragePrice(trades)
        #as shares is less than zero, it is not possible to add a trade 
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


def deleteTrade(trade: 'Trade', check: Optional[bool]= False) -> bool:
    """Delete and check if deletion of a trade is valid or not.

    Delete and check if deletion of a trade is possible in a portfolio for a passed
    in trade, if check is true then portfolio is not updated else portfolio is updated with
    new calculated value.

    Args:
        trade: A Trade object to be added.
        check: Optional; A bool to indicate to update portfolio for the given trade or not.

    Returns:
        bool to indicate if deletion of trade is possible or not.
    """

    #get the portfolio with the help of ticker symbol in trade
    try:
        portfolio = Portfolio.objects.get(ticker_symbol=trade.ticker_symbol)
    except Portfolio.DoesNotExist:
        return False
    try:
        trades = Trade.objects.filter(ticker_symbol=trade.ticker_symbol).order_by('id')[::1]
        #remove the passed trade from trades
        for index,t in enumerate(trades):
            if t.id == trade.id:
                trades.pop(index)
                break
        #get the shares and average price from the passed in trades
        shares,averagePrice = getSharesAveragePrice(trades)
        #as shares is less than zero, it is not possible to add a trade 
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


def updateTrade(newTrade: 'Trade', oldTrade: 'Trade') -> bool:
    """Update and check if updating a trade is valid or not.

    Update and check if updating a trade is possible in a portfolio for a passed
    in trade and update portfolio with new calculated value.

    Args:
        newTrade: A trade object with new data.
        oldTrade: A trade object to be updated.

    Returns:
        bool to indicate if deletion of trade is possible or not.
    """

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
            #create a portfolio for ticker symbol
            portfolioSerializer = createPortfolioSerializer(newTrade.price, newTrade.ticker_symbol, newTrade.shares)
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
        if (deleteTrade(oldTrade,True) and addTrade(newTrade,True)):
            #update respective trade portfolio and return True
            deleteTrade(oldTrade)
            addTrade(newTrade)
            return True
        return False


class AddTradeView(APIView):

    def post(self, request):
        """POST method for addition of a trade.

        Adds a trade if valid and return the response.

        Returns:
            Response of the added trade or error if not possible
        """

        #get the data from the request
        data = request.data.copy()
        #create a trade serializer with data and check if data is valid
        serializer = TradeSerializer(data=data)    
        if serializer.is_valid():
            #create the trade object
            trade = serializer.create(serializer.validated_data)
            #check if addition of trade is valid 
            if(addTrade(trade)):
                #if valid save the trade
                trade.save()
                s = TradeSerializer(trade)
                return Response(s.data)
            #if not then return error
            return Response({'error':'trade adding not possible'},status=400)
        #if data is not valid return the errors
        return Response(serializer.errors,status=400)    
        

class TradeView(APIView):

    def getTrade(self, id:int):
        """Get the trade with passed in trade id.

        Args:
            id: An integer indicating trade id.

        Raises:
            Http404: An error occured when id is not valid.
        """

        try:
            return Trade.objects.get(id=id)
        except Trade.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        """GET method to get a trade.

        Args:
            id: An integer indicating trade id.

        Returns:
            Response of the trade or error if not possible.
        """

        # with the help of trade id
        trade = self.getTrade(id)
        serializer = TradeSerializer(trade)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        """UPDATE method for updation of a trade.

        update a trade if valid and return the response.

        Args:
            id: An integer indicating trade id.

        Returns:
            Response of the updated trade or error if not possible
        """

        #get the trade with the help of trade id
        trade = self.getTrade(id)
        #update the trade and check if data is valid
        serializer = TradeSerializer(trade, data=request.data, partial=True)
        if serializer.is_valid():
            #create the updated trade object
            newTrade = serializer.update(trade,serializer.validated_data)
            #check if trade update is valid
            if(updateTrade(newTrade,trade)):
                #if valid then update the trade
                newTrade.save()
                s = TradeSerializer(newTrade)
                return Response(s.data)
            #if not then return error
            return Response({'error':'trade update not possible'},status=400)
        #if data is not valid return the errors
        return Response(serializer.errors,status=400)

    def delete(self, request, id, format=None):
        """DELETE method for deletion of a trade.

        delete a trade if valid and return the response.

        Args:
            id: An integer indicating trade id.

        Returns:
            Response of the deleted trade or error if not possible
        """

        #get the trade with the help of trade id
        trade = self.getTrade(id)
        serializer = TradeSerializer(trade)
         #check if trade delete is valid
        if(deleteTrade(trade)):
            #if valid then delete the trade and return it
            trade.delete()
            return Response(serializer.data)
        #if not then return error
        return Response({'error':'trade delete not possible'},status=400)


class TradesView(APIView):

    def get(self, request):
        """GET method to get trades along with all portfolio.

        Returns:
            Response of the trades with portfolio or error if not possible.
        """

        #get the list of portfolios
        portfolio = Portfolio.objects.all()[::1]
        data = []
        #for every portfolio get the trades and return it
        for p in portfolio:
            try:
                trades = Trade.objects.filter(ticker_symbol=p.ticker_symbol)
                tradeSerializer = TradeSerializer(trades, many=True)
                portfolioSerializer = PortfolioSerializer(p)
                d = portfolioSerializer.data
                d['trades'] = tradeSerializer.data
                data.append(d)
            except Trade.DoesNotExist:
                return Response({'error':'trades does not exists for a portfolio'},status=200)
        return Response(data,status=200)


class PortfolioTradeView(APIView):

    def get(self, request, tickerSymbol, format=None):
        """GET method to get trades for a portfolio.

        Args:
            tickerSymbol: A string indicating ticker symbol for portfolio.

        Returns:
            Response of the trades with portfolio.
        """

        try:
            #get all the trades for the ticker symbol
            trades = Trade.objects.filter(ticker_symbol=tickerSymbol)
            tradeSerializer = TradeSerializer(trades, many=True)
            tradeData = tradeSerializer.data
            #get the portfolio for the ticker symbol
            portfolio = Portfolio.objects.get(ticker_symbol=tickerSymbol)
            portfolioSerializer = PortfolioSerializer(portfolio)
            portfolioData = portfolioSerializer.data
        except Trade.DoesNotExist:
            tradeData = []
            portfolioData = {}
        except Portfolio.DoesNotExist:
            portfolioData = {}
        return Response({'portfolio':portfolioData,'trades':tradeData},status=200)


class PortfolioView(APIView):

    def get(self, request):
        """GET method to get all portfolio.

        Returns:
            Response of portfolios.
        """

        portfolios = Portfolio.objects.all()
        serializer = PortfolioSerializer(portfolios, many=True)
        return Response(serializer.data)


class PortfolioReturnView(APIView):

    def currentPrice(self, tickerSymbol:str) -> float:
        """Get the current price for the passed in ticker symbol.

        Args:
            tickerSymbol: A string representing ticker symbol.

        Returns:
            A float value representing the current price of the ticker symbol.
        """

        return 100

    def get(self, request):
        """GET method to get return amount from all the portfolios.

        Returns:
            Response containing the calculated return amount.
        """
        portfolio = Portfolio.objects.all()[::1]
        amount = 0
        for p in portfolio:
            amount += (self.currentPrice(p.ticker_symbol) - p.average_price) * p.shares
        return Response({'returns':amount},status=200)