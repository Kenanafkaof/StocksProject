import requests

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
print(movers)
global stock_data
stock_data = {
    'summary': summary,
    'movers': movers
}
