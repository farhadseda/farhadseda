import os
import time
import requests
import pandas as pd
from datetime import timedelta
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

class TwitterRequest(object):
    def __init__(self):
        # To set your environment variables in your terminal run the following line:
        # export 'BEARER_TOKEN'='<your_bearer_token>'
        self.bearer_token = 'AAAAAAAAAAAAAAAAAAAAANOUbgEAAAAAK0lsi%2BtZf6CtVhoYUxHs78EGoDU%3DgTSsYd1wHd9oSPcqbgndxsq92lfakvkbSn02pKqwzOTBNqAQP4' 
        # [query,start_time,end_time,since_id,until_id,max_results,next_token,pagination_token,sort_order,expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields]
        # Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
        # expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
        # query_params = {'query': '(from:twitterdev -is:retweet) OR #twitterdev','tweet.fields': 'author_id'}
        self.query_params = {
            'query': 'bitcoin -is:retweet lang:en',
            'tweet.fields': 'author_id,created_at',
            'max_results': 10,
        }

    # end_date - date (ISO 8601) The newest, most recent UTC timestamp to which the Tweets will be provided
    # start_date - date (ISO 8601) The oldest UTC timestamp (from most recent seven days) from which the Tweets will be provided.
    def set_query_params(self, start_date, end_date, search_term = 'Bitcoin', max_results = 100):
        start_time = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        print("start_time: ", start_time)
        print("end_time: ", end_time)
        query = '{0} -is:retweet lang:en'.format(search_term)
        query_params = {
            'query': query,
            'tweet.fields': 'author_id,created_at',
            'end_time': end_time,
            'start_time': start_time,
            'max_results': max_results,
        }
        self.query_params = query_params
    
    def bearer_oauth(self, r):
        """
        Method required by bearer token authentication.
        """
        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2RecentSearchPython"
        return r

    def connect_to_endpoint(self, url, params):
        response = requests.get(url, auth=self.bearer_oauth, params=params)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()

    def populate_sentiment_score(self, df):
        twitter_score = pd.DataFrame()
        twitter_score['Date'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')
        twitter_score['compound'] = df['text'].apply(lambda x: SIA().polarity_scores(x)['compound'])
        twitter_score['positive'] = df['text'].apply(lambda x: SIA().polarity_scores(x)['pos'])
        twitter_score['neutral'] = df['text'].apply(lambda x: SIA().polarity_scores(x)['neu'])
        twitter_score['negative'] = df['text'].apply(lambda x: SIA().polarity_scores(x)['neg'])
        twitter_score['polarity'] = df['text'].apply(lambda x: TextBlob(x).sentiment.polarity)
        twitter_score['subjective'] = df['text'].apply(lambda x: TextBlob(x).sentiment.subjectivity)
        twitter_daily_score = twitter_score.groupby(['Date']).agg(['mean'])
        twitter_daily_score.columns = ['compound','positive', 'neutral','negative','polarity','subjective']
        return twitter_daily_score
    
    def execute(self):
        search_url = 'https://api.twitter.com/2/tweets/search/recent'
        json_response = self.connect_to_endpoint(search_url, self.query_params)
        df = pd.json_normalize(json_response['data'])
        return df

    def execute_historic(self):
        search_url = 'https://api.twitter.com/2/tweets/search/all'
        # Historic data queries are rate limited at 1 request a second
        time.sleep(1)
        json_response = self.connect_to_endpoint(search_url, self.query_params)
        df = pd.json_normalize(json_response['data'])
        return df

    # function to combine all news article for for a given period
    def get_twits_for_period(self, start_date, end_date, search_term = 'Bitcoin', max_results = 100, search_historic = False):
        df_twits = pd.DataFrame()
        current_day = start_date
        while current_day < end_date:
            self.set_query_params(current_day, current_day + timedelta(days=1), search_term, max_results)
            df = self.execute_historic() if search_historic else self.execute()
            df_twits = pd.concat([df_twits, df])
            current_day = current_day + timedelta(days=1)
        return df_twits