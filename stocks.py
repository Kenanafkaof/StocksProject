import requests
import time
import random
import json
import yfinance as yf
from bs4 import BeautifulSoup


ticker = "JWN"
start_time = time. time()
def yahoofinance():
    global stock_ticker
    stock_ticker = yf.Ticker(ticker)
    stock_data = stock_ticker.info
    dump = json.dumps(stock_data)
    data = json.loads(dump)
    currentPrice = data['currentPrice']
    companyName = data['shortName']
    companyLogo = data['logo_url']
    companyRecommendation = data['recommendationKey']
    if companyRecommendation == 'strong_buy':
        companyRecommendation = 'Strong Buy'
    if companyRecommendation == 'buy':
        companyRecommendation = 'Buy'
    if companyRecommendation == 'hold':
        companyRecommendation = 'Hold'
    if companyRecommendation == 'underperform':
        companyRecommendation = 'Underperform'
    if companyRecommendation == 'sell':
        companyRecommendation = 'Sell'
    print(companyRecommendation)
    global stock_yahoo
    stock_yahoo = {
        'price': currentPrice,
        'company':companyName,
        'logo':companyLogo,
        'recommendation': companyRecommendation
    }
    #walletinvestor()
def recommendations():
    stock_ticker = yf.Ticker(ticker)
    rec = stock_ticker.recommendations
    print(rec)
    print("--- %s seconds ---" % (time. time() - start_time))
def walletinvestor():
    walletUrl = "https://walletinvestor.com/stock-forecast/" + ticker + "-stock-prediction"
    wallet = requests.request("GET", walletUrl)
    soup = BeautifulSoup(wallet.content, 'html.parser')
    global oneYear
    oneYear = soup.find_all('a', {'class':'forecast-currency-href'})[1].text
    try:
        global fiveYears
        fiveYears = soup.find_all('a', {'class':'forecast-currency-href'})[2].text
        global oneYearFinal
        oneYearFinal = oneYear.replace(' USD ', '')
        global fiveYearsFinal
        fiveYearsFinal = fiveYears.replace(' USD', '')
    except:
        oneYearFinal = oneYear.replace(' USD ', '')
        fiveYearsFinal = 'None'
    if fiveYearsFinal != 'None':
        one_year_profit = float(oneYearFinal) - float(stock_yahoo['price'])
        five_year_profit = float(fiveYearsFinal) - float(stock_yahoo['price'])
        five_years_string = str(round(one_year_profit, 2))
        one_years_string = str(round(five_year_profit, 2))
        if float(oneYearFinal) < float(stock_yahoo['price']):
            global negative_one
            negative_one = 'negative'
        if float(fiveYearsFinal) < float(stock_yahoo['price']):
            negative_one = 'negative'
        global stock_data
        stock_data = {
            'one_year_profit': one_years_string,
            'five_year_profit':five_years_string,
        }
        if negative_one:
            stock_profit = {
                'negative': negative_one
            }

        graph_nums = [float(stock_yahoo['price']), float(oneYearFinal), float(fiveYearsFinal)]
        global graph_data
        graph_data = max(graph_nums)
        global graph_definition
        graph_definition = ["Current Price", "One Year", "Five Years"]
    else:
        stock_data = {
            'one_year_profit': one_year_profit,
            'five_year_profit':five_year_profit,
        }


if __name__ == "__main__":
    yahoofinance()
    print("--- %s seconds ---" % (time. time() - start_time))
