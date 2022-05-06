import yfinance as yf
import pandas as pd

class Utils:

    def __init__(self):
        self.time_format = '%Y-%m-%d'
        self.coin_names = ['Bitcoin', 'Litecoin',
                           'Ethereum', 'Dogecoin', 'XRP']
        self.coin_to_price_map = {
            'Bitcoin':  'BTC-USD',
            'Litecoin': 'LTC-USD',
            'Ethereum': 'ETH-USD',
            'Dogecoin': 'DOGE-USD',
            'XRP': 'XRP-USD',
        }

    def get_coin_names(self):
        return self.coin_names

    def get_ticker_from_name(self, coin_name):
        return self.coin_to_price_map[coin_name]

    # function to correlate lagged score index with prices
    def lagged_score(self, price, daily_score, lag_day = 1, change_threshold = 0.03):
        daily_score_lagged = daily_score.shift(lag_day)
        lagged = pd.merge(daily_score_lagged, price, left_index=True, right_index=True, how='left')
        lagged['label'] = [1 if x>change_threshold else -1 if x<-1*change_threshold else 0 for x in lagged['Returns']]
        lagged.dropna(inplace=True)
        return lagged

    # function to get the stock-crypto adjusted close prices and the daily return
    def get_price(self, start_date, end_date, search_term='BTC-USD'):
        start_date = start_date.strftime(self.time_format)
        end_date = end_date.strftime(self.time_format)
        price_all = yf.download(
            search_term, start=start_date, end=end_date, progress=False,)
        price = price_all[['Adj Close']]
        price['Returns'] = price['Adj Close']/price['Adj Close'].shift(1) - 1
        return price
    
