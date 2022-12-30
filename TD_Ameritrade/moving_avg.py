import matplotlib.pyplot as plt, numpy as np, yfinance as yf

def trend_filter():
    #read data from disk
    data = yf.download(tickers="SPY",period="max",interval="1d",group_by='ticker',auto_adjust=True,prepost=True,
                       threads=True,proxy=None)

    #calculate moving averages
    data['SMA100'] = data['Close'].rolling(100).mean()
    #data['SMA200'] = data['Adj Close'].rolling(200).mean()

    #set to 1 if SPY is above SMA100
    data['Position'] = np.where(data['Close'] > data['SMA100'], 1, 0)

    current_trend = data['Position'].iloc[-1]

    if current_trend == 0:
        return "BEAR"
    elif current_trend == 1:
        return "BULL"

def trend_filter_chart():
    # read data from disk
    data = yf.download(  # or pdr.get_data_yahoo(...
        # tickers list or string as well
        tickers="SPY", period="max", interval="1d", group_by='ticker', auto_adjust=True, prepost=True, threads=True,
        proxy=None
    )

    # calculate moving averages
    data['SMA100'] = data['Close'].rolling(100).mean()
    # data['SMA200'] = data['Adj Close'].rolling(200).mean()

    # set to 1 if SPY is above SMA100
    data['Position'] = np.where(data['Close'] > data['SMA100'], 1, 0)

    current_trend = data['Position'].iloc[-1]

    data.to_csv("TLT_ON.csv")

    #plot the result
    plt.style.use('seaborn-darkgrid')
    plt.figure(figsize=(8,8))
    plt.xlabel("date")
    plt.ylabel("$ price")
    plt.title("SPY")
    plt.plot(data['SMA100'], 'r--', label="SMA100")
    #plt.plot(data['SMA200'], 'g--', label="SMA100")
    plt.plot(data['Close'], label="close")
    #plt.plot(data['Strategy'], 'g', Label= "Strategy")
    plt.legend()
    plt.show()

#trend_filter_chart()