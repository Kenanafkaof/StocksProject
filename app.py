from flask import Flask, request, render_template
import requests
import json
import random
import os
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
import yfinance as yf
import sqlite3


# Database structure - 'id' INTEGER | 'name' VARCHAR(255) | 'email' VARCHAR(255)
connection = sqlite3.connect('database.db', check_same_thread=False)
#connection.execute("DROP TABLE stocks;");

# Setting row_factory property of
# connection object to sqlite3.Row(sqlite3.Row is an implementation of
# row_factory).

connection.row_factory = sqlite3.Row
# cursor
db = connection.cursor()

app = Flask(__name__)
@app.route('/')
@app.route('/submit',methods = ['POST', 'GET'])
def submit():
    if request.method == "POST":
       #return render_template('index.html', button_load=button)
       global ticker
       form_data = request.form['ticker']
       ticker = form_data.lower()
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
           global stock_yahoo
           stock_yahoo = {
                'ticker': ticker.upper(),
                'price': currentPrice,
                'company':companyName,
                'logo':companyLogo,
                'recommendation': companyRecommendation
           }
           walletinvestor()
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
               five_years_string = str(round(five_year_profit, 2))
               one_years_string = str(round(one_year_profit, 2))
               if float(one_year_profit) < 0:
                   global negative_one
                   negative_one = True
               if float(one_year_profit) > 0:
                   negative_one = False
               global stock_data
               stock_data = {
                    'oneYear': oneYearFinal,
                    'fiveYear': fiveYearsFinal,
                    'one_year_profit': one_years_string,
                    'five_year_profit': five_years_string
               }

               graph_compare = [float(stock_yahoo['price']), float(oneYearFinal), float(fiveYearsFinal)]
               global graph_nums
               graph_nums = [stock_yahoo['price'], oneYearFinal, fiveYearsFinal]
               global graph_data
               graph_data = max(graph_compare)
               global graph_definition
               graph_definition = ["Current Price", "One Year", "Five Years"]
           else:
               one_year_profit = float(oneYearFinal) - float(stock_yahoo['price'])
               one_years_string = str(round(one_year_profit, 2))
               if float(one_year_profit) < 0:
                   negative_one = True
               if float(one_year_profit) > 0:
                   negative_one = False
               stock_data = {
                   'oneYear': oneYearFinal,
                   'fiveYear': 'None',
                   'one_year_profit': one_years_string,
                   'five_year_profit':'None'
               }
               graph_compare = [float(stock_yahoo['price']), float(oneYearFinal)]
               graph_nums = [stock_yahoo['price'], oneYearFinal, 0]
               graph_data = max(graph_compare)
               graph_definition = ["Current Price", "One Year", "Five Years - Unknown"]
       try:
           yahoofinance()
       except:
           nodata = 'Error with stock. Check ticker or try another.'
           return render_template('index.html', nodata=nodata)

       with sqlite3 .connect("database.db") as con:
            cur = connection.cursor()
            cur.execute("INSERT INTO stocks (Col1,Col2,Col3, Col4) VALUES (?,?,?,?)",(ticker.upper(),stock_yahoo['price'],oneYearFinal,fiveYearsFinal))
            connection.commit()
       try:
           if negative_one is True:
               print('Stock is negative')
               global stock_profit
               stock_profit = {
                'negative': 'True'
               }
               return render_template('index.html', max=graph_data, data=stock_data, stock_yahoo=stock_yahoo, graph=graph_nums, value=graph_definition, stock_profit=stock_profit)
           if negative_one is False:
               return render_template('index.html', max=graph_data, data=stock_data, stock_yahoo=stock_yahoo, graph=graph_nums, value=graph_definition)
       except:
           return render_template('index.html', max=graph_data, data=stock_data, stock_yahoo=stock_yahoo, graph=graph_nums, value=graph_definition)


    else:
        return render_template('index.html')
@app.route('/loading/', methods=['GET'])
def loading_model():
    button = {
    'clicked': 'True'
    }
    return render_template('index.html', button_load=button)
    submit()
@app.route('/index/', methods=['GET'])
def home():
    data = 'No Data Found'
    return render_template('index.html', nodata=data)
@app.route('/stocklist/', methods=['GET'])
def stocklist():
    cur = connection.cursor()
    cur.execute("SELECT * FROM stocks")
    data = cur.fetchall()
    return render_template('stocklist.html', data=data)
@app.route('/monitor/', methods=['GET'])
def monitor():
    return render_template('monitoring.html')
@app.route('/login/', methods=['GET'])
def login():
    return render_template('login.html')
@app.route('/createlogin/', methods=['GET'])
def signUp():
    return render_template('createlogin.html')
@app.route('/clearData',methods = ['POST', 'GET'])
def clearData():
    file = open("results.txt","w")
    file.close()
    with open("results.txt") as f:
        global file_meaning
        file_meaning = f.read()
    return render_template('index.html', list=file_meaning)
@app.route('/getfile', methods=['GET','POST'])
def getfile():
    if request.method == 'POST':
        file = request.files['file']
        file_content = file.read()
        file_data = file.read().decode("latin-1")
        filename = secure_filename(file.filename)
        file_text = file_content.decode('utf-8').upper()
        file_decode = str(file_content, 'utf-8')
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        UPLOAD_FOLDER = path
        global l
        l = []
        i = 0
        l = 0
        global stock_data
        stock_data = []
        trending_data = []
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
                print(response)


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
                        global fiveYearsFinal
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
                    loss_gain = float(average)
                    print('Total made after one year:', totalmade)
                except:
                    print('Error!')
                try:
                    finalfive = fiveYearsFinal
                    global five_profit
                    five_profit = float(finalfive) - float(marketPrice)
                    print('Profit five', five_profit)
                except:
                    five_profit = 'No Data'
                    print('Error!')

            calculateProfitLoss()
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
        ticker = []
        total = []
        price = []
        five = []
        with open(UPLOAD_FOLDER, "r") as file:
            for line in file:
                multiScrape()
                try:
                    total.append(totalmade)
                except:
                    pass
                ticker.append(line)
                price.append(marketPrice)
                five.append(five_profit)
        for i in range(len(ticker)):
            ticker[i] = ticker[i].upper()
        for i in range(len(stock_data)):
            stock_data[i] = stock_data[i].upper()
        with open("results.txt") as f:
            global file_meaning
            file_meaning = f.read()
        return render_template('index.html',
                       stock_ticker=ticker,
                       stock_profit=total,
                       stock_price=price,
                       stock_five=five,
                       stock_data=stock_data,
                       file=file_data,
                       file_meaning=file_meaning)
    else:
        result = request.args.get['myfile']
@app.route('/recommendations', methods=['GET','POST'])
def recommendations():
    url = "https://tr-frontend-cdn.azureedge.net/bff/preprod/header/payload.json"

    querystring = {"ver":"27250574"}

    payload = ""
    headers = {
        "authority": "tr-frontend-cdn.azureedge.net",
        "sec-ch-ua": "^\^Google"
    }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

    data = response.json()
    i = 0
    l = 0
    global stock_data

    stock_data = []
    company_data = []
    trending_data = []
    for i in range(len(data['popular'][i]['ticker'])):
        ticker = data['popular'][i]['ticker']
        i +=1
        stock_data.append(ticker)
    for l in range(len(data['trending'][l]['ticker'])):
        trending = data['trending'][l]['ticker']
        l +=1
        stock_data.append(trending)
    for i in range(len(stock_data)):
        stock_data[i] = stock_data[i].upper()

    return render_template('stockrecommendations.html', stock_data=stock_data)
@app.route('/submitrecommendations', methods=['GET','POST'])
def submitrecommendations():
    if request.method == 'POST':
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
                msft = yf.Ticker(line)
                global company_name
                company_name = msft.info['longName']
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
                print(response)


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
                        global fiveYearsFinal
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
                    loss_gain = float(average)
                    print('Total made after one year:', totalmade)
                except:
                    print('Error!')
                try:
                    finalfive = fiveYearsFinal
                    global five_profit
                    five_profit = float(finalfive) - float(marketPrice)
                    print('Profit five', five_profit)
                except:
                    five_profit = 'No Data'
                    print('Error!')

            calculateProfitLoss()
        ticker = []
        total = []
        price = []
        five = []
        company_name = []
        for i in range(len(stock_data)):
            stock_data[i] = stock_data[i].lower()
            line = stock_data[i]
            multiScrape()
            try:
                total.append(totalmade)
            except:
                pass
            ticker.append(line)
            price.append(marketPrice)
            five.append(five_profit)

            #stock_list = [ticker, total, price]
        for i in range(len(ticker)):
            ticker[i] = ticker[i].upper()
        for i in range(len(stock_data)):
            stock_data[i] = stock_data[i].upper()
        return render_template('stockrecommendations.html',
                       stock_ticker=ticker,
                       stock_profit=total,
                       stock_price=price,
                       stock_five=five,
                       stock_data=stock_data)
@app.route('/monitoringstock', methods=['GET','POST'])
def monitoringstock():
    if request.method == 'POST':
        form_data = request.form['ticker']
        ticker = form_data.upper()
        print(ticker)
        global max_price
        max_price = request.form['maxprice']
        global delay
        delay = request.form['delay']
        def monitor():
            user_agent_list = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            ]
            def stock_info():
                get_info = requests.get('https://api.polygon.io/v1/meta/symbols/' + ticker + '/company?apiKey=Rl5aUP_HvvRlwH1P5FOZ7NxcuFpKE_o6')
                print(get_info)
                data = get_info.json()
                global company_name
                company_name = data["name"]
                global image
                image = data["logo"]
                global similar_stocks
                similar_stocks = data["similar"]
                check_market()
            def check_market():
                market = requests.get('https://api.polygon.io/v1/marketstatus/now?apiKey=Rl5aUP_HvvRlwH1P5FOZ7NxcuFpKE_o6')
                market_data = market.json()
                global closedMarket
                closedMarket = False
                global closed
                closed = market_data["market"]
                if closed == 'closed':
                    closedMarket = True
                else:
                    closedMarket = False
                yahooFinance()
            def yahooFinance():
                for i in range(1,4):
                    user_agent = random.choice(user_agent_list)
                url = "https://query1.finance.yahoo.com/v8/finance/chart/" + ticker
                querystring = {"region":"US","lang":"en-US","includePrePost":"false","interval":"2m","useYfid":"true","range":"1d","corsDomain":"finance.yahoo.com",".tsrc":"finance"}
                headers = {'User-Agent': user_agent}
                payload = ""
                current_info = requests.request("GET", url, data=payload, headers=headers, params=querystring)
                price = current_info.json()
                global marketPrice
                marketPrice = price['chart']['result'][0]['meta']['regularMarketPrice']
                previousClose = price['chart']['result'][0]['meta']['previousClose']
            def stockMonitor():
                while int(marketPrice) > int(max_price):
                    yahooFinance()
                    if int(marketPrice) <= int(max_price):
                        print('Price within limit!')
                        break
                    time.sleep(int(delay))
                    print(marketPrice)
            stock_info()
            if closedMarket is True:
                print('Done')
            if closedMarket is False:
                print('Starting monitoring!')
                stockMonitor()
            global stock_return
            stock_return = {
                'price': marketPrice,
                'company': company_name,
                'image': image,
                'ticker': ticker,
                'maxprice': max_price,
                'market':closed,
                'delay':delay
            }
        try:
            monitor()
        except:
            error = 'No data found/error in ticker'
            return render_template('monitoring.html', error=error)
        return render_template('monitoring.html', data=stock_return, list=similar_stocks)

    if request.method == 'GET':
        return render_template('monitoring.html')
@app.route('/trending', methods=['GET','POST'])
def trending():
    if request.method == 'POST':
        url = "https://yh-finance.p.rapidapi.com/news/v2/get-details"

        querystring = {"uuid":"9803606d-a324-3864-83a8-2bd621e6ccbd","region":"US"}

        headers = {
            'x-rapidapi-host': "yh-finance.p.rapidapi.com",
            'x-rapidapi-key': "67575a40dcmshed3bbbae22f05f3p156d25jsn7be2ae7c923d"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)

        news = response.json()
        movers = news['data']['contents'][0]['content']['finance']['stockTickers']
        summary = news['data']['contents'][0]['content']['summary']
        global stock_data
        stock_data = {
            'summary': summary
        }
        return render_template('monitoring.html', news_data=stock_data, movers=movers)
@app.route('/research', methods=['GET','POST'])
def research():
    if request.method == 'POST':
        try:
            global ticker
            form_data = request.form['ticker']
            ticker = form_data.lower()
            main = yf.Ticker(ticker)
            recs = main.info
            news = main.news
            dump = json.dumps(recs)
            data = json.loads(dump)
            dumpSecond = json.dumps(news)
            dataSecond = json.loads(dumpSecond)
            print(dataSecond[0]['title'])
            recs = {
                'ticker': data['symbol'],
                'price': data['currentPrice'],
                'targetPrice': data['targetMeanPrice'],
                'dayLow': data['dayLow'],
                'marketCap': data['marketCap'],
                'company': data['shortName'],
                'news': dataSecond[0]['title'],
                'link': dataSecond[0]['link']
            }
            return render_template('index.html', recs=recs)
        except:
            recs = 'Lacking stock data'
            return render_template('index.html', recs=recs)


if __name__ == "__main__":
    app.run(debug=True)
