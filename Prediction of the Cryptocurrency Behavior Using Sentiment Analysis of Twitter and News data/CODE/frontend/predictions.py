from matplotlib.pyplot import axis
from load_models import LoadModels
from datetime import datetime, timedelta
from twitter_request import TwitterRequest
from news_request import NewsRequest
import pandas as pd
from common_utils import Utils
import pytz


class Predictions:

    def __init__(self):
        self.load_models = LoadModels()
        # Load all models
        self.load_models.load()
        self.twitter_request = TwitterRequest()
        self.news_request = NewsRequest()
        self.change_threshold = 0.03

    def get_news_for_today(self, coin_name):
        start_date = datetime.today()
        end_date = datetime.today()
        df = self.news_request.get_news_period(start_date, end_date, coin_name)
        return df

    def news_to_signal(self, df):
        news_signals = self.news_request.sentiment_analysis(df).reset_index()
        news_signals = news_signals.drop(['Date'], axis=1)
        return news_signals

    def get_tweets_for_today(self, coin_name):
        tz = pytz.timezone('US/Mountain')
        start_date = datetime.now(tz) - timedelta(days=1)
        # Twitter API requirment is that the end_date is at least 10 seconds prior to the request time.
        end_date = datetime.now(tz) - timedelta(minutes=5)
        df = self.twitter_request.get_twits_for_period(
            start_date, end_date, coin_name, max_results=100)
        return df

    def tweets_to_signal(self, df):
        tweetter_signals = self.twitter_request.populate_sentiment_score(df).reset_index()
        tweetter_signals = tweetter_signals.drop(['Date'], axis=1)
        return tweetter_signals

    def get_prediction(self, X, coin_name):
        model = self.load_models.get_model_for_coin(coin_name)
        results = model.predict(X)
        return results
