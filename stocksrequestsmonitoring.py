import requests
from bs4 import BeautifulSoup
import random
import json
from datetime import datetime
from pytz import timezone
import time
user_agent_list = [
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
]
for i in range(1,4):
    user_agent = random.choice(user_agent_list)
fmt = '%H:%M:%S'
eastern = timezone('US/Eastern')
loc_dt = datetime.now(eastern)
current_time = loc_dt.strftime(fmt)
closeTime = int(float('16.00'))
openTime = int(float('09.30'))
fmt = '%H.%M'
eastern = timezone('US/Eastern')
loc_dt = datetime.now(eastern)
market_time = loc_dt.strftime(fmt)
time_to_open = int(float(loc_dt.strftime(fmt)))



stockInput = input('Enter desired stock: ')
url = "https://query1.finance.yahoo.com/v8/finance/chart/" + stockInput

querystring = {"region":"US","lang":"en-US","includePrePost":"false","interval":"2m","useYfid":"true","range":"1d","corsDomain":"finance.yahoo.com",".tsrc":"finance"}
headers = {'User-Agent': user_agent}
payload = ""

response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

soup = BeautifulSoup(response.content, 'html.parser')
print('Querying data... | Response Status: ', response.status_code)
def queryData():
    data = response.json()
    symbol = data['chart']['result'][0]['meta']['symbol']
    global marketPrice
    marketPrice = data['chart']['result'][0]['meta']['regularMarketPrice']
    previousClose = data['chart']['result'][0]['meta']['previousClose']
    print('\nTicker:', symbol, ' | Price: ', marketPrice, ' | Previous Close: ', previousClose)
queryData()

walletUrl = "https://walletinvestor.com/stock-forecast/" + stockInput + "-stock-prediction"
def querySeconData():
    try:
        wallet = requests.request("GET", walletUrl, headers=headers)
        soup = BeautifulSoup(wallet.content, 'html.parser')
        global oneYear
        oneYear = soup.find_all('a', {'class':'forecast-currency-href'})[1].text
        global fiveYears
        fiveYears = soup.find_all('a', {'class':'forecast-currency-href'})[2].text
        print('\nOne Year Prediction: ', oneYear, ' | Five Year Prediction: ', fiveYears)
    except IndexError:
        print('Error querying data, "data not present"')
print('\nQuerying new data... | Response Status: ', response.status_code)
querySeconData()
oneYearFinal = oneYear.replace(' USD', '')
fiveYearsFinal = fiveYears.replace(' USD', '')
final = int(float(oneYearFinal)) - int(marketPrice)
final2 = int(float(fiveYearsFinal)) - int(marketPrice)
print('Estimated profit/loss (one year): ' + '$' + str(final))
print('Estimated profit/loss (five years): ' + '$' + str(final2))

finished = input('\nDone or monitor? (y/n)')
def monitorPrices():
    print('Checking market time status...')
    if current_time > '16:00:00':
        print('Market Closed. Too Late!')
        proceed = input('Do you wish to proceed anyways? (y/n) ')
        if proceed == 'y':
            queryData()
    if current_time < '09:30:00':
        print('Market Closed. Too Early!')
        proceed = input('Do you wish to proceed anyways? (y/n) ')
        if proceed == 'y':
            queryData()
    else:
        print('Market Open!')
        maxprice = input('Enter max price: ')
        monitorDelay = int(input('Enter monitor delay (secs): '))
        queryData()
        while marketPrice > int(float(maxprice)):
            print('Price too high, monitoring...')
            time.sleep(monitorDelay)
            print('Sleeping...')
            if marketPrice < int(float(maxprice)):
                break
                print('Price within limit!')
            print('Checking prices...')
if finished == 'n':
    monitorPrices()
