import os
from binance.client import Client
import pandas as pd
import datetime, time
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

def GetHistoricalData(symbol, apikey="", apisecret=""):
    my_client = Client(apikey,apisecret) 
    # Calculate the timestamps for the binance api function
    untilThisDate = datetime.datetime.now()
    sinceThisDate = untilThisDate - datetime.timedelta(minutes = 1440)
    # Execute the query from binance - timestamps must be converted to strings !
    candle = my_client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, str(sinceThisDate), str(untilThisDate))

    df = pd.DataFrame(candle, columns=['dateTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore'])
    df.dateTime = pd.to_datetime(df.dateTime, unit='ms').dt.strftime("%X")
    df['close'] = df['close'].astype(float).astype(int)
    df['volume'] = df['volume'].astype(float).astype(int)
    df = df.drop(['open', 'high', 'low', 'closeTime','quoteAssetVolume', 'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore'], axis=1)
    df = df.set_index('dateTime')
    return df

def getAllTradingCoins(apikey="", apisecret=""):
    my_client = Client(apikey,apisecret) 
    info = my_client.get_all_tickers()
    coins = []
    for each in info:
        if "USDT" in each['symbol']:
            coins.append(each['symbol'])
    return coins

def getAccountInfos(apikey="", apisecret=""):
    my_client = Client(apikey,apisecret) 
    info = my_client.get_account()
    df = pd.DataFrame(info["balances"])
    df["free"] = df["free"].astype(float).round(4)
    df = df[df["free"] > 0]
    return df

def getAvgPrice(query, apikey="", apisecret=""):
    my_client = Client(apikey,apisecret)
    try:
        avg_price = my_client.get_avg_price(symbol=query+'USDT')
        return int(float(avg_price['price']))
    except:
        return 0