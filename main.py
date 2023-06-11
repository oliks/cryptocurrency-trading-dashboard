import os
from binance.client import Client
import pandas as pd
import datetime, time
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

def hello(apikey="", apisecret=""):
    my_client = Client(apikey,apisecret) 
    info = my_client.get_all_tickers()
    coins = []
    for each in info:
        coins.append(each['symbol'])
    return coins
    
hello()