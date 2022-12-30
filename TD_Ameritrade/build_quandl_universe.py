import pandas as pd, quandl, yaml
from datetime import date, timedelta

with open('C:/Users/samla/OneDrive/Documents/GitHub/slasker1/quandl_api_yml.yml', 'r') as f:
    doc = yaml.safe_load(f)

pd.set_option('display.max_columns', 1000000)
pd.set_option('display.max_rows', 1000000)

quandl.ApiConfig.api_key = doc['KEY']

today = date.today()

# dd/mm/YY
curr_date = today.strftime("%Y-%m-%d")
#print("current date =", curr_date)

before_date = date.today()-timedelta(days=300)
before_date = before_date.strftime("%Y-%m-%d")
#print("history start date =", before_date)

def get_tickers():
    print("I'm collecting the universe of tickers.")
    current_tickers = quandl.get_table('SHARADAR/TICKERS', paginate=True)
    current_tickers = current_tickers[(current_tickers.scalemarketcap.isin(["6 - Mega","5 - Large"])) & (current_tickers.isdelisted == "N")]
    current_tickers = current_tickers.ticker.tolist()

    current_tickers = [i for n, i in enumerate(current_tickers) if i not in current_tickers[:n]]

    return current_tickers

def get_volume_closeadj():
    tickers = get_tickers()
    print("I've collected the tickers successfully.\n"
          +"I'm downloading all the data needed.")

    ticker_tb = quandl.get_table('SHARADAR/SEP', date={'gte': before_date, 'lte': curr_date}, ticker=tickers, paginate=True)
    ticker_tb = ticker_tb[['ticker','date','volume','closeadj']]
    ticker_tb = ticker_tb.sort_values(by='date', ascending=True)

    ticker_tb.set_index('date', inplace=True)

    hist = pd.DataFrame(columns=tickers)
    volume = pd.DataFrame(columns=tickers)

    for ticker in tickers:
        hist[ticker] = ticker_tb[(ticker_tb.ticker == ticker)]['closeadj'].tail(129)[:-4]
        volume[ticker] = ticker_tb[(ticker_tb.ticker == ticker)]['volume'].tail(204)[:-4]

    print("Filtering for Average Daily Volume criteria...")
    ADV200 = volume.mean()

    ADV_Final = ADV200.sort_values(ascending=False).head(500)
    ADV_Final_list = ADV_Final.index.to_list()
    hist = hist[ADV_Final_list]
    return hist

#print(get_volume_closeadj())