import requests
import random
import json
import os
import pickle
from bs4 import BeautifulSoup
from pathlib import Path
global l
l = []
def multiScrape():
    user_agent_list = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    ]

    for i in range(1,4):
        user_agent = random.choice(user_agent_list)
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + line
    querystring = {"region":"US","lang":"en-US","includePrePost":"false","interval":"2m","useYfid":"true","range":"1d","corsDomain":"finance.yahoo.com",".tsrc":"finance"}
    headers = {'User-Agent': user_agent}
    payload = ""
    response = requests.get(url, headers=headers, params=querystring)
    def yahooFinance():
        data = response.json()
        symbol = data['chart']['result'][0]['meta']['symbol']
        global marketPrice
        marketPrice = data['chart']['result'][0]['meta']['regularMarketPrice']
        previousClose = data['chart']['result'][0]['meta']['previousClose']
        print('\nTicker:', symbol, ' | Price: ', marketPrice, ' | Previous Close: ', previousClose)
    yahooFinance()

    url = "https://tr-frontend-cdn.azureedge.net/bff/prod/stock/" + line + "/payload.json"
    querystring = {"ver":"1634476664627"}

    payload = ""
    headers = {"sec-ch-ua": "^\^Chromium^^;v=^\^94^^, ^\^Google"}
    def tipRanks():
        try:
            try:
                string = data["similar"]["similar"][0]["analystRatings"]["consensus"]["id"]
                if string == 'strongBuy':
                    string = 'Strong Buy'
                rating = data["similar"]["similar"][0]["analystRatings"]["consensus"]["priceTarget"]["value"]
            except:
                string = data["common"]["stock"]["analystRatings"]["bestConsensus"]["id"]
                if string == 'moderateBuy':
                    string = 'Moderate Buy'
                rating = data["common"]["stock"]["analystRatings"]["bestConsensus"]["priceTarget"]["value"]
        except:
            try:
                string = data["similar"]["similar"][0]["analystRatings"]["consensus"]["id"]
                if string == 'moderateBuy':
                    string = 'Moderate Buy'
                rating = data["similar"]["similar"][0]["analystRatings"]["consensus"]["priceTarget"]["value"]
            except:
                print('Unable to get data.')
        try:
            global score
            score = rating
        except:
            pass
        #print('Buy Rating:', string, ' || One Year Prediction:', score)

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()
        tipRanks()
    else:
        print('Error!')


    walletUrl = "https://walletinvestor.com/stock-forecast/" + line + "-stock-prediction"
    def walletinvestor():
        try:
            wallet = requests.request("GET", walletUrl, headers=headers)
            soup = BeautifulSoup(wallet.content, 'html.parser')
            global oneYear
            oneYear = soup.find_all('a', {'class':'forecast-currency-href'})[1].text
            try:
                global fiveYears
                fiveYears = soup.find_all('a', {'class':'forecast-currency-href'})[2].text
                #print('One Year Prediction: ', oneYear, ' | Five Year Prediction: ', fiveYears)
                global oneYearFinal
                oneYearFinal = oneYear.replace(' USD ', '')
                fiveYearsFinal = fiveYears.replace(' USD', '')
            except:
                oneYearFinal = oneYear.replace(' USD', '')
                #print('One Year Prediction: ', oneYear)
        except IndexError:
            print('Error querying data, "data not present"')

    walletinvestor()


    def calculateProfitLoss():
        finalamount = float(oneYearFinal)
        try:
            finalRank = finalamount + float(score)
            global average
            average = finalRank/2
            print('Average total profit/loss', average)
            global totalmade
            totalmade = average - marketPrice
            print('Total made after one year:', totalmade)
        except:
            print('Error!')

    calculateProfitLoss()
with open('tickers.txt') as file:
    while (line := file.readline().rstrip()):
        multiScrape()
        with open("results.txt", "a") as myfile:
            final_price = float(marketPrice)
            loss_gain = float(average)
            list_data = myfile.write("\nTicker: " + line + " | Current Price: " + str(final_price) + " | Total Made: " + str(totalmade) + " | Price After Year: " + str(loss_gain))
            myfile.close()
        l.append(totalmade)
print(l)
