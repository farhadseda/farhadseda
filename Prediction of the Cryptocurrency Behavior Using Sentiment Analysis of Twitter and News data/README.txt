
DESCRIPTION - Describe the package in a few paragraphs

This application seeks to provide users with an interactive platform that enables them
to visually explore crypto trends based on news and twitter sentiment. Users can use this
application to day trade with recommendations from our classifier on individual crypto coins.

Our web application is hosted in AWS and leverages the CoinGecko API to retrieve cryptocurrency
data, the Twitter API for social media data, and the News API to retrieve data from reputable
cryptocurrency news outlets.

We use Twitter API, News API and CoinGecko API to retrieve 1 month historic Twitter, News and
crypto price data. Next, we combine this data and label it as buy/sell or hold based on the 3
percent price change threshold. We run sentiment analysis on twitter and news data using VADER
and TextBlob libraries and train our model using this data.

We tested a number of classifiers to identify and use the one with the highest accuracy and came
to the conclusion that the Linear Discriminant Model(LDA) performed best for this task. LDA
classifier projects the features in higher dimensional space onto a lower-dimensional space that
helps reduce the dimensionality and resource costs. (you can see details of classifier evaluation
in a Results section).

We have placed our model training code and data logic under "/model_training" directory.
Training data we used is placed under "/model_training/training_data". We used Models.ipynb and
LagDays.ipynb files to train our models and run experiments with lag day. We saved our models
under the "/saved_classifiers" directory.

Our frontend code reads saved models and queries Twitter and News data for the day. It then
runs sentiment analysis on that data and feeds processed data to the model to get a prediction
for the crypto price change.

INSTALLATION - How to install and setup your code

Please install all the dependencies specified under
/frontend/requirements.txt

EXECUTION - How to run a demo on your code

You can find latest deployment of our web app at:
http://latest-env.eba-pvd28apw.us-east-1.elasticbeanstalk.com/

From the web app, you will see a table on the landing page that includes the coin name, current price, 24 hr price change, news sentiment, 
twitter sentiment, and the ML model's 24 hr price prediction. Clicking on one of the rows will bring you to a more detailed view of the coin
where you will see a time series graph of the coin price over the last 3 days along with the projected price movement over the next 24 hours.
Below the time series graph the coin's table row is included in addition to both a news and twitter word cloud for the last 24 hours of news articles
and tweets. To return to the table landing page, you can click the button in the top left corner of the page.

If you would like to run it on your local server please follow this steps:
1. Download all files in the frontend folder
2. Run application.py locally
3. Open http://127.0.0.1:8080 in a web browser

