import pandas as pd
from datetime import datetime, timedelta
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from newsapi.newsapi_client import NewsApiClient


class NewsRequest(object):
    def __init__(self):
        self.newsapi_key = '0e7419b7c7ab43799f8e8e197f1f3a43'#'9b5d505ebe6a48339a14649640807325'
        self.newsapi = NewsApiClient(api_key=self.newsapi_key)
        self.time_format = '%Y-%m-%d'

    def get_sources(self, category=None):
        sources = self.newsapi.get_sources()
        if category is not None:
            rez = [source['id'] for source in sources['sources']
                   if source['category'] == category and source['language'] == 'en']
        else:
            rez = [source['id']
                   for source in sources['sources'] if source['language'] == 'en']
        return rez

    # function to get all related news for a given day
    def get_news_daily(self, Date, search_term, sources_list=None):
        end_date = Date
        start_date = end_date  # - timedelta(days = 1)
        start_date = start_date.strftime('%d-%b-%Y')
        end_date = end_date.strftime('%d-%b-%Y')

        if sources_list:
            articles = self.newsapi.get_everything(q=search_term, from_param=datetime.strptime(start_date, '%d-%b-%Y'), to=datetime.strptime(
                end_date, '%d-%b-%Y'), language="en", sources=",".join(sources_list), sort_by="relevancy", page_size=100)
        else:
            articles = self.newsapi.get_everything(q=search_term, from_param=datetime.strptime(
                start_date, '%d-%b-%Y'), to=datetime.strptime(end_date, '%d-%b-%Y'), language="en", sort_by="relevancy", page_size=100)

        combined = []
        seen = set()
        for article in articles['articles']:
            # check f there is any news title repeated by different websites/agencies
            if str(article['title']) in seen:
                continue
            else:
                seen.add(str(article['title']))
            combined.append(
                (article['url'], article['title'], article['description']))
        df_news_daily = pd.DataFrame(
            combined, columns=['URL', 'Title', 'Description'])
        return df_news_daily

    # function to combine all news article for for a given period
    def get_news_period(self, start_date, end_date, search_term='Bitcoin'):
        df_news = pd.DataFrame()
        current_day = start_date
        while current_day <= end_date:
            df = self.get_news_daily(
                current_day, search_term)
            df['Date'] = current_day.strftime(self.time_format)
            df_news = pd.concat([df_news, df])
            current_day = current_day + timedelta(days=1)
        return df_news

    # function to define seniment score
    def sentiment_analysis(self, df):
        df['Content'] = df['Title'] + '. ' + df['Description']
        news_score = pd.DataFrame()
        news_score['Date'] = df['Date']
        news_score['compound'] = df['Content'].apply(
            lambda x: SIA().polarity_scores(str(x))['compound'])
        news_score['positive'] = df['Content'].apply(
            lambda x: SIA().polarity_scores(str(x))['pos'])
        news_score['neutral'] = df['Content'].apply(
            lambda x: SIA().polarity_scores(str(x))['neu'])
        news_score['negative'] = df['Content'].apply(
            lambda x: SIA().polarity_scores(str(x))['neg'])
        news_score['polarity'] = df['Content'].apply(
            lambda x: TextBlob(str(x)).sentiment.polarity)
        news_score['subjective'] = df['Content'].apply(
            lambda x: TextBlob(str(x)).sentiment.subjectivity)
        news_daily_score = news_score.groupby(['Date']).agg(['mean'])
        news_daily_score.columns = [
            'compound', 'positive', 'neutral', 'negative', 'polarity', 'subjective']
        return news_daily_score
