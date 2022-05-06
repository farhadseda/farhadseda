import dash
from dash import html
import plotly.graph_objects as go
from dash import dcc
import plotly.express as px
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash.dash_table import DataTable, FormatTemplate
from dash.exceptions import PreventUpdate
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
import time
import pytz
from datetime import timedelta
from wordcloud import WordCloud, STOPWORDS
import random
import predictions
import nltk

# Helper Functions
def getCoinIDs():
    validCoins = ['Bitcoin','Litecoin','Ethereum','Dogecoin','XRP']
    url = "https://api.coingecko.com/api/v3/coins/list"
    parameters = {
    }
    headers = {
    'Accepts': 'application/json'
    }
    session = Session()
    session.headers.update(headers)
    gotData = 0
    while gotData == 0:
        try:
            response = session.get(url, params=parameters)
            coins = json.loads(response.text)
            gotData = 1
        except json.decoder.JSONDecodeError as e:
            continue
        time.sleep(3)
    
    coinIDs = []
    for coin in coins:
        if coin['name'] in validCoins:
            coinIDs.append({'label':coin['name'],'value':coin['id']})
    return coinIDs

def getCoinName(coinID):
    coinIDs = getCoinIDs()
    for coin in coinIDs:
        if coin['value'] == coinID:
            return coin['label']

def populateTable(coinIDs):
    pred = predictions.Predictions()
    headers = {
    'Accepts': 'application/json'
    }
    session = Session()
    session.headers.update(headers)
    
    currentPrice = []
    marketCap = []
    volume = []
    change = []
    coinName = []
    coinID = []
    newsSentiment = []
    socialSentiment = []
    pricePrediction = []
    coinIDToName = {}
    for coin in coinIDs:
        coinIDToName[coin['value']] = coin['label']

    url = "https://api.coingecko.com/api/v3/simple/price"
    parameters = {
        'ids':",".join(coinIDToName.keys()),
        'vs_currencies':'usd',
        'include_market_cap': 'true',
        'include_24hr_vol': 'true',
        'include_24hr_change': 'true'
    }
    gotData = 0
    while gotData == 0:
        try:
            response = session.get(url, params=parameters)
            priceData = json.loads(response.text)
            gotData = 1
        except json.decoder.JSONDecodeError as e:
            continue
        time.sleep(3)

    for key in priceData.keys():
        coin_name = coinIDToName[key]
        df_tweets = pred.get_tweets_for_today(coin_name)
        df_news = pred.get_news_for_today(coin_name)
        print(coin_name)
        print(df_news)
        if len(df_news) >= 1 and len(df_tweets) >= 1:
            twitter_signals = pred.tweets_to_signal(df_tweets).reset_index()
            news_signals = pred.news_to_signal(df_news)
            combined_signals = pd.concat([twitter_signals, news_signals], axis=1).drop(columns=['index'])
            #combined_signals = news_signals.append(twitter_signals, ignore_index=True)
            #combined_signals = pd.DataFrame(combined_signals.mean(axis='index')).T.drop(columns=['index'])
            prediction = pred.get_prediction(combined_signals, coin_name)
            nSent = (float(news_signals['compound']) - 0.5) / 0.5
            if nSent < -1.0:
                nSent = -1.0
            elif nSent > 1.0:
                nSent = 1.0
            sSent = (float(twitter_signals['compound']) - 0.5) / 0.5
            if sSent < -1.0:
                sSent = -1.0
            elif sSent > 1.0:
                sSent = 1.0
            newsSentiment.append(nSent)
            socialSentiment.append(sSent)
            pricePrediction.append(float(prediction) * 3.0 / 100.0)
        elif len(df_news) >= 1:
            news_signals = pred.news_to_signal(df_news)
            nSent = (float(news_signals['compound']) - 0.5) / 0.5
            if nSent < -1.0:
                nSent = -1.0
            elif nSent > 1.0:
                nSent = 1.0
            newsSentiment.append(nSent)
            socialSentiment.append(0.0)
            pricePrediction.append(0.0)
        elif len(df_tweets) >= 1:
            twitter_signals = pred.tweets_to_signal(df_tweets).reset_index()
            sSent = (float(twitter_signals['compound']) - 0.5) / 0.5
            if sSent < -1.0:
                sSent = -1.0
            elif sSent > 1.0:
                sSent = 1.0
            newsSentiment.append(0.0)
            socialSentiment.append(sSent)
            pricePrediction.append(0.0)
        else:
            newsSentiment.append(0.0)
            socialSentiment.append(0.0)
            pricePrediction.append(0.0)
        
        coinID.append(key)
        coinName.append(coin_name)
        currentPrice.append(priceData[key]['usd'])
        marketCap.append(priceData[key]['usd_market_cap'])
        volume.append(priceData[key]['usd_24h_vol'])
        change.append(priceData[key]['usd_24h_change'] / 100.0)
            
    
    df = pd.DataFrame()
    df['CoinID'] = coinID
    df['Coin Name'] = coinName
    df['Current Price'] = currentPrice
    df['Market Cap'] = marketCap
    df['24 HR Volume'] = volume
    df['24 HR Change'] = change 
    df['News Sentiment'] = newsSentiment
    df['Twitter Sentiment'] = socialSentiment
    df['24 HR Price Prediction'] = pricePrediction
    df = df.sort_values(by='Market Cap', ascending=False).reindex()
    return df
        
def populateInitialTable(coinIDs):
    
    headers = {
    'Accepts': 'application/json'
    }
    session = Session()
    session.headers.update(headers)
    
    currentPrice = []
    marketCap = []
    volume = []
    change = []
    coinName = []
    coinID = []
    newsSentiment = []
    socialSentiment = []
    pricePrediction = []
    coinIDToName = {}
    for coin in coinIDs:
        coinIDToName[coin['value']] = coin['label']

    url = "https://api.coingecko.com/api/v3/simple/price"
    parameters = {
        'ids':",".join(coinIDToName.keys()),
        'vs_currencies':'usd',
        'include_market_cap': 'true',
        'include_24hr_vol': 'true',
        'include_24hr_change': 'true'
    }
    gotData = 0
    while gotData == 0:
        try:
            response = session.get(url, params=parameters)
            priceData = json.loads(response.text)
            gotData = 1
        except json.decoder.JSONDecodeError as e:
            continue
        time.sleep(3)

    for key in priceData.keys():
        coin_name = coinIDToName[key]
        coinID.append(key)
        coinName.append(coin_name)
        currentPrice.append(priceData[key]['usd'])
        marketCap.append(priceData[key]['usd_market_cap'])
        volume.append(priceData[key]['usd_24h_vol'])
        change.append(priceData[key]['usd_24h_change'] / 100.0)
        newsSentiment.append('Loading...')
        socialSentiment.append('Loading...')
        pricePrediction.append('Loading...')
    
    df = pd.DataFrame()
    df['CoinID'] = coinID
    df['Coin Name'] = coinName
    df['Current Price'] = currentPrice
    df['Market Cap'] = marketCap
    df['24 HR Volume'] = volume
    df['24 HR Change'] = change 
    df['News Sentiment'] = newsSentiment
    df['Twitter Sentiment'] = socialSentiment
    df['24 HR Price Prediction'] = pricePrediction
    df = df.sort_values(by='Market Cap', ascending=False).reindex()
    return df

def getGraphData():
    cIDs = getCoinIDs()
    count = 0
    for coin in cIDs:
        url = "https://api.coingecko.com/api/v3/coins/" + coin['value'] + "/market_chart"
        parameters = {
            'id':coin['value'],
            'vs_currency':'usd',
            'days':3
        }
        headers = {
        'Accepts': 'application/json'
        }
        session = Session()
        session.headers.update(headers)
        gotData = 0
        while gotData == 0:
            try:
                response = session.get(url, params=parameters)
                marketData = json.loads(response.text)
                gotData = 1
            except json.decoder.JSONDecodeError as e:
                continue
            time.sleep(3)
        if count == 0:
            df = pd.DataFrame(marketData['prices'],columns=['Date',coin['value'] + ' Price'])
            count +=1
        else:
            df = pd.concat([df, pd.DataFrame(marketData['prices'],columns=['Date',coin['value'] + ' Price']).drop(columns=['Date'])], axis=1)
    df = df.dropna()
    return df.to_dict('records')

def getWordCloud(colors,wordSource,coinID):
    stopwords = set(STOPWORDS)
    pred = predictions.Predictions()
    coin_name = getCoinName(coinID)
    if wordSource == 'Twitter':
        df_tweets = pred.get_tweets_for_today(coin_name)
        if len(df_tweets) >= 1:
            words = ' '.join(df_tweets['text'])
        else:
            words = 'No new tweets'
    elif wordSource == 'News':
        df_news = pred.get_news_for_today(coin_name)
        if len(df_news) >= 1:
            words = ' '.join(df_news['Title']) + ' ' + ' '.join(df_news['Description'])
        else:
            words = 'No new news articless'
    elif wordSource == 'Loading':
        words = 'Loading data will be here soon be here soon Loading Loading Loading'
    
    wordcloud = WordCloud(width = 800, height = 800,
                background_color ='black',
                stopwords = stopwords,
                min_font_size = 10).generate(words)

    fig = px.imshow(wordcloud)
    fig.update_layout({'title':wordSource,'title_x':0.5,
                            'plot_bgcolor': colors['background'],
                            'paper_bgcolor': colors['background'],
                            'xaxis': {
                                'showgrid': False, # thin lines in the background
                                'zeroline': False, # thick line at x=0
                                'visible': False,  # numbers below
                                },
                            'yaxis': {
                                'showgrid': False, # thin lines in the background
                                'zeroline': False, # thick line at x=0
                                'visible': False,  # numbers below
                                },
                            'font': {
                                'color': colors['text']
                            }
                            })
    return fig

nltk.download('vader_lexicon')

# Get Coin IDs
coinIDs = getCoinIDs()

# Creating Web App and Layouts
application = app = dash.Dash(__name__)
application = app.server

# Set styling
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Initial App Layout
app.layout = html.Div(style={'backgroundColor': colors['background']},children = 
[
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='tableStore', storage_type='local'),
    dcc.Interval(
            id='interval-component',
            interval=5*60000, # in milliseconds
            n_intervals=0
        ),
    dcc.Store(id='graphStore', storage_type='local'),
    dcc.Interval(
            id='graphInterval',
            interval=5*60000, # in milliseconds
            n_intervals=0
        )
])

# Get table data and format table columns
#tableDF = populateTable(coinIDs)
#tableDF = tableDF.sort_values(by='Market Cap', ascending=False).reindex()
money = FormatTemplate.money(2)
percentage = FormatTemplate.percentage(2)

columns = [
                dict(id='Coin Name', name='Coin Name'),
                dict(id='Current Price', name='Current Price', type='numeric', format=money),
                #dict(id='Market Cap', name='Market Cap', type='numeric', format=money),
                #dict(id='24 HR Volume', name='24 HR Volume', type='numeric', format=money),
                dict(id='24 HR Change', name='24 HR Change', type='numeric', format=percentage),
                dict(id='News Sentiment', name='News Sentiment', type='numeric', format=percentage),
                dict(id='Twitter Sentiment', name='Twitter Sentiment', type='numeric', format=percentage),
                dict(id='24 HR Price Prediction', name='24 HR Price Prediction', type='numeric', format=percentage)
                ]

columnsInitial = [
    dict(id='Coin Name', name='Coin Name'),
    dict(id='Current Price', name='Current Price', type='numeric', format=money),
    #dict(id='Market Cap', name='Market Cap', type='numeric', format=money),
    #dict(id='24 HR Volume', name='24 HR Volume', type='numeric', format=money),
    dict(id='24 HR Change', name='24 HR Change', type='numeric', format=percentage),
    dict(id='News Sentiment', name='News Sentiment'),
    dict(id='Twitter Sentiment', name='Twitter Sentiment'),
    dict(id='24 HR Price Prediction', name='24 HR Price Prediction')
]
# Landing page layout
index_page = dbc.Container(style={'backgroundColor': colors['background']},children=[
    html.Button('Back to Table View', id='button', n_clicks=0, style = {'width': '9%', 'display': 'none','backgroundColor': colors['background'],'color': colors['text']}),
    html.H1(
        children='Crypto Sentiment',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    html.Div(children='Predict next day price movement with news and social media sentiment machine learning. Click a row on the table to see more data.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    dbc.Label('Click a cell in the table:'),
    DataTable(data=populateInitialTable(coinIDs).to_dict('records'),columns = columnsInitial,sort_action='native', id='table',
    style_header={
        'backgroundColor': 'rgb(30, 30, 30)',
        'color': colors['text']
    },
    style_data={
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': colors['text']
    },
     style_data_conditional=[
        {
            'if': {
                'filter_query': '{24 HR Change} >= 0',
                'column_id': '24 HR Change',
            },
            'backgroundColor': 'green',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{24 HR Change} < 0',
                'column_id': '24 HR Change'
            },
            'backgroundColor': 'tomato',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{News Sentiment} >= 0',
                'column_id': 'News Sentiment',
            },
            'backgroundColor': 'green',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{News Sentiment} < 0',
                'column_id': 'News Sentiment'
            },
            'backgroundColor': 'tomato',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{Twitter Sentiment} >= 0',
                'column_id': 'Twitter Sentiment',
            },
            'backgroundColor': 'green',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{Twitter Sentiment} < 0',
                'column_id': 'Twitter Sentiment'
            },
            'backgroundColor': 'tomato',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{24 HR Price Prediction} >= 0',
                'column_id': '24 HR Price Prediction',
            },
            'backgroundColor': 'green',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{24 HR Price Prediction} < 0',
                'column_id': '24 HR Price Prediction'
            },
            'backgroundColor': 'tomato',
            'color': 'white'
        }

        ]),
    DataTable(data=[[1],[2],[3]],columns = [],sort_action='native',filter_action='native', id='dummyTable'),
    DataTable(data=[[1],[2],[3]],columns = [],sort_action='native',filter_action='native', id='dummyTable2'),
    DataTable(data=[[1],[2],[3]],columns = [],sort_action='native',filter_action='native', id='dummyTable3'),
    DataTable(data=[[1],[2],[3]],columns = [],sort_action='native',filter_action='native', id='dummyTable4'),
    
])

# Graph page layout
graph_page = html.Div(id = 'parent', children = [
    html.Button('Back to Table View', id='button', n_clicks=0, style = {'width': '9%', 'display': 'inline-block','backgroundColor': colors['background'],'color': colors['text']}),
    html.H1(
        children='Crypto Sentiment',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'width': '89%', 
            'display': 'inline-block'
        }
    ),
    html.Div(children='Predict next day price movement with news and social media sentiment machine learning.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

        dcc.Graph(id = 'line_plot',figure={'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }}),

    DataTable(columns = columns, id='graphTable',
        style_header={
        'backgroundColor': 'rgb(30, 30, 30)',
        'color': colors['text']
    },
    style_data={
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': colors['text']
    },
     style_data_conditional=[
        {
            'if': {
                'filter_query': '{24 HR Change} >= 0',
                'column_id': '24 HR Change',
            },
            'backgroundColor': 'green',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{24 HR Change} < 0',
                'column_id': '24 HR Change'
            },
            'backgroundColor': 'tomato',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{News Sentiment} >= 0',
                'column_id': 'News Sentiment',
            },
            'backgroundColor': 'green',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{News Sentiment} < 0',
                'column_id': 'News Sentiment'
            },
            'backgroundColor': 'tomato',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{Twitter Sentiment} >= 0',
                'column_id': 'Twitter Sentiment',
            },
            'backgroundColor': 'green',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{Twitter Sentiment} < 0',
                'column_id': 'Twitter Sentiment'
            },
            'backgroundColor': 'tomato',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{24 HR Price Prediction} >= 0',
                'column_id': '24 HR Price Prediction',
            },
            'backgroundColor': 'green',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{24 HR Price Prediction} < 0',
                'column_id': '24 HR Price Prediction'
            },
            'backgroundColor': 'tomato',
            'color': 'white'
        }

        ]),
        dcc.Graph(id = 'Twitter WordCloud',figure = getWordCloud(colors,'Loading',''), style = {'width': '48%', 'display': 'inline-block','color': colors['text'],}),
        dcc.Graph(id = 'News WordCloud',figure = getWordCloud(colors,'Loading',''),style = {'width': '48%', 'display': 'inline-block','color': colors['text']}),
        DataTable(data=[],columns = [],sort_action='native',filter_action='native', id='table')
        
    ])
    
# General App Layout callbacks
@app.callback(Output('tableStore', 'data'),
              Input('interval-component', 'n_intervals'))
def updateTableData(n):
    coinIDs = getCoinIDs()
    df = populateTable(coinIDs)
    return df.to_dict('records')

# Landing page callbacks
@app.callback(Output('table', 'data'),Output('table','columns'),
              Input('tableStore', 'data'), Input('table', "derived_virtual_data"),Input('url', 'pathname'))
def updateTableData(tableStore,currentTableData,path):
    if path[:6] != '/graph':
        currentTableData = pd.DataFrame(currentTableData)
        df = pd.DataFrame(tableStore)
        if len(currentTableData) > 2:
            sorter = currentTableData['Coin Name'].tolist()
            df['Coin Name'] = df['Coin Name'].astype("category").cat.set_categories(sorter)
            df = df.sort_values(['Coin Name']).reindex()
        columns = [
                    dict(id='Coin Name', name='Coin Name'),
                    dict(id='Current Price', name='Current Price', type='numeric', format=money),
                    #dict(id='Market Cap', name='Market Cap', type='numeric', format=money),
                    #dict(id='24 HR Volume', name='24 HR Volume', type='numeric', format=money),
                    dict(id='24 HR Change', name='24 HR Change', type='numeric', format=percentage),
                    dict(id='News Sentiment', name='News Sentiment', type='numeric', format=percentage),
                    dict(id='Twitter Sentiment', name='Twitter Sentiment', type='numeric', format=percentage),
                    dict(id='24 HR Price Prediction', name='24 HR Price Prediction', type='numeric', format=percentage)
                    ]
        return df.to_dict('records'), columns
    else:
        raise PreventUpdate

@app.callback(Output('url', 'pathname'), Input('table', 'active_cell'),Input('table', "derived_virtual_data"),Input('button', 'n_clicks'))
def routeToGraph(active_cell,tableData,click):
    if click > 0:
        return '/'
    elif active_cell == None:
        raise PreventUpdate
    elif active_cell != None:
        tableData = pd.DataFrame(tableData)
        return '/graph=' + tableData.iloc[active_cell['row'],0]
        
# Graph page callbacks
@app.callback(Output(component_id='graphTable', component_property= 'data'),Input('url', 'pathname'),Input('tableStore', 'data'))
def updateGraphPageTableData(path,tableStore):
    if path[:6] == '/graph':
        cID = path[7:]
        tableStore = pd.DataFrame(tableStore)
        df = tableStore.loc[tableStore['CoinID'] == cID]
        return df.to_dict('records')
    else:
        raise PreventUpdate

@app.callback(Output(component_id='graphStore', component_property= 'data'),Input('graphInterval', 'n_intervals'))
def graphStoreUpdate(n):
    return getGraphData()

@app.callback(Output(component_id='line_plot', component_property= 'figure'),Input('url', 'pathname'),Input('graphTable', "data"), Input(component_id='graphStore', component_property= 'data'))
def graph_update(path,graphTableData,graphStore):
    if path[:6] == '/graph' and graphTableData != None:
        cID = path[7:]
        df = pd.DataFrame(graphStore)
        df['Date'] = pd.to_datetime(df['Date'], unit='ms')
        eastern = pytz.timezone('US/Eastern')
        df.set_index('Date',inplace=True)
        df.index = df.index.tz_localize(pytz.utc).tz_convert(eastern)  
        dfPred = pd.DataFrame() 
        dfPred['Date'] = [df.index[-1],df.index[-1]+timedelta(days=1)]

        graphTableData = pd.DataFrame(graphTableData)
        predPrice = graphTableData['24 HR Price Prediction'].values[0]
        if predPrice > 0:
            dfPred['PredPrice1'] = [df[cID + ' Price'].iloc[-1] * 0.995, df[cID + ' Price'].iloc[-1] * 1.02]
            dfPred['PredPrice2'] = [df[cID + ' Price'].iloc[-1] * 1.005, df[cID + ' Price'].iloc[-1] * 1.04]
        elif predPrice < 0:
            dfPred['PredPrice1'] = [df[cID + ' Price'].iloc[-1] * 0.995, df[cID + ' Price'].iloc[-1] * 0.96]
            dfPred['PredPrice2'] = [df[cID + ' Price'].iloc[-1] * 1.005, df[cID + ' Price'].iloc[-1] * 0.98]
        else:
            dfPred['PredPrice1'] = [df[cID + ' Price'].iloc[-1] * 0.995, df[cID + ' Price'].iloc[-1] * 0.97]
            dfPred['PredPrice2'] = [df[cID + ' Price'].iloc[-1] * 1.005, df[cID + ' Price'].iloc[-1] * 1.03]
        fig = go.Figure([go.Scatter(x = df.index, y = df[cID + ' Price'],\
                        line = dict(color = 'firebrick', width = 4)),
                        go.Scatter(x = dfPred['Date'], y = dfPred['PredPrice1'],\
                        line = dict(color = 'blue', width = 4, dash = 'dash')),
                        go.Scatter(x = dfPred['Date'], y = dfPred['PredPrice2'],\
                        line = dict(color = 'blue', width = 4, dash = 'dash'))
                        ])
        
        fig.update_layout({'title' : getCoinName(cID),
                        'xaxis_title' : 'Date',
                        'yaxis_title' : 'Price ($)',
                        'showlegend' : False,
                            'plot_bgcolor': colors['background'],
                            'paper_bgcolor': colors['background'],
                            'font': {
                                'color': colors['text']
                            }
                            })
        return fig
    else:
        raise PreventUpdate



@app.callback(Output(component_id='Twitter WordCloud', component_property= 'figure'),Input('url', 'pathname'),Input('graphInterval', 'n_intervals'))
def updateGraphPageTableData(path,n):
    if path[:6] == '/graph':
        path = path[7:]
        return getWordCloud(colors,'Twitter',path)
    else:
        raise PreventUpdate

@app.callback(Output(component_id='News WordCloud', component_property= 'figure'),Input('url', 'pathname'),Input('graphInterval', 'n_intervals'))
def updateGraphPageTableData(path,n):
    if path[:6] == '/graph':
        path = path[7:]
        return getWordCloud(colors,'News',path)
    else:
        raise PreventUpdate  

# Callback for page layouts
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname[:6] == '/graph':
        return graph_page
    else:
        return index_page


if __name__ == '__main__': 
    application.run(port=8080)