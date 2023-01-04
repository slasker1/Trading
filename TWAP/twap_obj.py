import yfinance as yf

class Initialize:
   #Research topic selection
   def __init__(self, ticker, time):
      self.ticker = ticker
      self.time = time
      self.twap = self.returnTWAP()
   def displaySelection(self):
      print("Ticker: ", self.ticker, "\nTime: ", self.time, "\nTWAP: ", self.twap)

   def returnTWAP(self):
       ticker_hist = yf.download(tickers=self.ticker, period="1y",
                                 interval="1d", group_by='ticker',
                                 auto_adjust=True, prepost=True,
                                 threads=True, proxy=None)
       ticker_hist['Daily_TWAP'] = (ticker_hist['Open'] + ticker_hist['High'] + ticker_hist['Low'] + ticker_hist[
           'Close']) / 4
       TWAP = ticker_hist.tail(int(self.time))['Daily_TWAP'].mean()
       return TWAP