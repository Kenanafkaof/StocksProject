  def scrapeData():
       user_agent_list = [
       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
       'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
       ]

       for i in range(1,4):
           user_agent = random.choice(user_agent_list)
       url = "https://query1.finance.yahoo.com/v8/finance/chart/" + ticker

       querystring = {"region":"US","lang":"en-US","includePrePost":"false","interval":"2m","useYfid":"true","range":"1d","corsDomain":"finance.yahoo.com",".tsrc":"finance"}
       headers = {'User-Agent': user_agent}
       payload = ""

       response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

       def yahooFinance():
           msft = yf.Ticker(ticker)
           global company_name
           company_name = msft.info['longName']
           data = response.json()
           symbol = data['chart']['result'][0]['meta']['symbol']
           global marketPrice
           marketPrice = data['chart']['result'][0]['meta']['regularMarketPrice']
           previousClose = data['chart']['result'][0]['meta']['previousClose']
           print('\nTicker:', symbol, ' | Price: ', marketPrice, ' | Previous Close: ', previousClose)
       yahooFinance()


       url = "https://tr-frontend-cdn.azureedge.net/bff/prod/stock/" + ticker + "/payload.json"
       querystring = {"ver":"1634823300969"}

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
           global score
           score = rating
           print('Buy Rating:', string, ' || One Year Prediction:', score)

       response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
       if response.status_code == 200:
           data = response.json()
           tipRanks()
       else:
           print('Error!')

       walletUrl = "https://walletinvestor.com/stock-forecast/" + ticker + "-stock-prediction"
       def walletinvestor():
           try:
               wallet = requests.request("GET", walletUrl, headers=headers)
               soup = BeautifulSoup(wallet.content, 'html.parser')
               global oneYear
               oneYear = soup.find_all('a', {'class':'forecast-currency-href'})[1].text
               try:
                   global fiveYears
                   fiveYears = soup.find_all('a', {'class':'forecast-currency-href'})[2].text
                   print('One Year Prediction: ', oneYear, ' | Five Year Prediction: ', fiveYears)
                   global oneYearFinal
                   oneYearFinal = oneYear.replace(' USD ', '')
                   print(oneYearFinal)
                   global fiveYearsFinal
                   fiveYearsFinal = fiveYears.replace(' USD', '')
               except:
                   oneYearFinal = oneYear.replace(' USD', '')
                   print('One Year Prediction: ', oneYear)
                   fiveYearsFinal = 'None'
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
               pass
           try:
               finalRank = finalamount
               totalmade = finalRank - marketPrice
               average = finalamount
           except:
               average = 'No Data'
               totalmade = 'No Data'
               print('Error with nonetype data')
           try:
               finalfive = fiveYearsFinal
               global five_profit
               five_profit = float(finalfive) - float(marketPrice)
               print('Profit five', five_profit)
           except:
              print('Error')
              #fiveYearsFinal = 'No Data'
              #five_profit = 'No Data'
       calculateProfitLoss()
       global stock_data
       stock_data = {
           'companyname': company_name,
           'ticker': ticker.upper(),
           'total': totalmade,
           'gain': average,
           'price': marketPrice,
           'five': fiveYearsFinal,
           'fiveprofit':five_profit
       }
       global graph_data
       graph_data = [marketPrice, average, fiveYearsFinal]
       global graph_definition
       graph_definition = ["Current Price", "One Year", "Five Years"]
  scrapeData()

         with sqlite3 .connect("database.db") as con:
              cur = connection.cursor()
              cur.execute("INSERT INTO stocks (Col1,Col2,Col3, Col4) VALUES (?,?,?,?)",(ticker.upper(),stock_yahoo['price'],oneYearFinal,fiveYearsFinal))
              connection.commit()
