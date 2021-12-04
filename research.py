import requests
import time
import random
import json
import yfinance as yf
from bs4 import BeautifulSoup


ticker = "MSFT"


main = yf.Ticker(ticker)


recs = main.recommendations
print(recs)
