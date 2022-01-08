import asyncio
import io
import random
import time
import warnings
from datetime import datetime
from threading import Thread

import pandas as pd
import requests
import yfinance
from bs4 import BeautifulSoup as bs
from dateutil.tz import gettz
from replit import db

from atr_intraday import add_indicators_intraday
from keepalive import keep_alive
from momentum import accumulation_dist
from swing_intraday import find_swing

warnings.simplefilter(action='ignore')

nifty_100_quality = [
    "HINDUNILVR", "ITC", "HCLTECH", "RELIANCE", "BAJFINANCE", "TCS", "INFY",
    "DIVISLAB", "KOTAKBANK", "TITAN", "ASIANPAINT", "LT", "BHARTIARTL",
    "WIPRO", "BAJAJ-AUTO", "TECHM", "HDFCBANK", "HEROMOTOCO", "NTPC",
    "AXISBANK", "M&M", "GRASIM", "ULTRACEMCO", "ICICIBANK", "SBILIFE",
    "TATACONSUM", "SUNPHARMA", "CIPLA", "SHREECEM", "ADANIPORTS", "HDFCLIFE",
    "HDFC", "EICHERMOT", "TATAMOTORS", "UPL", "TATAPOWER", "TATASTEEL",
    "KOTAKBANK", "TRENT", "ASIANPAINT", "WHIRLPOOL"
]

top_gainers = [
    "TCS", "HDFCBANK", "NYKAA", "KOTAKBANK", "COALINDIA", "INDUSINDBK",
    "CIPLA", "LICHSGFIN", "GAIL", "TATAMTRDVR", "PFC", "NIFTYBEES", "TECHM",
    "HINDCOPPER", "ZOMATO", "INDIANB", "APOLLOTYRE", "GODREJPROP", "ITC",
    "RBLBANK", "RELIANCE", "HDFCLIFE", "DABUR", "BSOFT", "FSL", "INDUSTOWER",
    "ADANIPOWER", "ADANIENT", "INFY", "GLENMARK", "WIPRO", "ABFRL", "FORTIS",
    "TATAMOTORS", "SCI", "HCLTECH", "BALRAMCHIN", "BHARTIARTL", "MOTHERSUMI",
    "TATAPOWER", "SONACOMS", "RECLTD", "AUROPHARMA", "BANDHANBNK", "NTPC",
    "SRF", "INDIACEM", "REDINGTON", "M&MFIN", "MANAPPURAM", "UPL",
    "LAURUSLABS", "CADILAHC", "DELTACORP", "OIL", "SUNPHARMA", "BSE",
    "CHOLAFIN", "HINDPETRO", "IOC", "POONAWALLA", "LATENTVIEW", "MOL", "BPCL",
    "DHANI", "PAYTM", "BIOCON", "TITAN", "HDFC", "RAIN", "SBICARD",
    "IBULHSGFIN", "POWERGRID", "M&M", "APOLLOHOSP", "GREAVESCOT", "TALBROAUTO",
    "IRB", "TTML", "SIRCA", "JMCPROJECT"
]

defaultstocks = [
    'HINDUNILVR', 'POLYCAB', 'BHARTIARTL', 'NAVINFLUOR', 'VIPIND', 'AUBANK',
    'AMBER', 'APLAPOLLO', 'BATAINDIA', 'HDFCLIFE', 'ICICIGI', 'KPITTECH',
    'LAURUSLABS', 'PIDILITIND', 'GLS', 'BSE', 'TATACONSUM', 'TATAELXSI',
    'INFOBEAN', 'HAPPSTMNDS', 'IEX', 'JUBLINGREA', 'ASAHIINDIA', 'HDFCBANK',
    'RELIANCE', 'FINPIPE', 'APOLLOPIPE', 'RSYSTEMS'
]

extra = [
    'VINATIORGA', 'ASTRAL', 'HCLTECH', 'TCS', 'SEQUENT', 'MARICO', 'LTTS',
    'INFY', 'MINDTREE', 'RELAXO', 'TATACHEM', 'KOTAKBANK', 'TRENT', 'TVSMOTOR',
    'ASIANPAINT', 'DEEPAKNTR', 'WHIRLPOOL', 'BSOFT', 'PERSISTENT', 'BORORENEW',
    'CLEAN', 'ULTRACEMCO', 'LTI', 'SIEMENS', 'PAYTM', '	BIOCON', 'INDIGO',
    'GMMPFAUDLR', 'VOLTAS'
]


def get_intraday_stocks(onlyFutures=True):
    try:
        code = '33489' if onlyFutures else '57960'
        data = {
            'scan_clause': '( {' + code + '} ( [0] 10 minute high <= [=1] 1 hour high and [0] 10 minute low >= [=1] 1 hour low and [-1] 15 minute high <= [=1] 1 hour high and [-1] 15 minute low >= [-1] 1 hour low and [-2] 15 minute high <= [=1] 1 hour high and [-2] 15 minute low >= [=1] 1 hour low and [-3] 15 minute high <= [=1] 1 hour high and [-3] 15 minute low >= [=1] 1 hour low and [-4] 15 minute high <= [=1] 1 hour high and [-4] 15 minute low >= [=1] 1 hour low and [-5] 15 minute high <= [=1] 1 hour high and [-5] 15 minute low >= [=1] 1 hour low and [-6] 30 minute high <= [=1] 1 hour high and [-6] 30 minute low >= [=1] 1 hour low and [-7] 30 minute high <= [=1] 1 hour high and [-7] 30 minute low >= [=1] 1 hour low and [-8] 30 minute high <= [=1] 1 hour high and [-8] 30 minute low >= latest low and [-9] 30 minute high <= [=1] 1 hour high and [-9] 30 minute low >= [=1] 1 hour low and [-10] 30 minute high <= [=1] 1 hour high and [-10] 30 minute low >= [-10] 30 minute low and [-11] 30 minute high <= [=1] 1 hour high and [-11] 30 minute low >= [=1] 1 hour low and latest close > 100 ) ) '
        }

        with requests.Session() as s:
            r = s.get('https://chartink.com/screener/rectangle-for-next-day-trade')
            soup = bs(r.content, 'lxml')
            s.headers['X-CSRF-TOKEN'] = soup.select_one('[name=csrf-token]')['content']
            r = s.post('https://chartink.com/screener/process', data=data).json()
            # print(r.json())
            df = pd.DataFrame(r['data'])
            return df['nsecode'].tolist()
    except:
        print("error")
    return get_nse_200_stocks()


def get_nse_200_stocks():
    url = 'https://www1.nseindia.com/content/indices/ind_nifty500Multicap502525_list.csv'
    s = requests.get(url).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    res = df['Symbol'].tolist()
    res = random.sample(res, 50)
    return list(res)


def get_nse_500_stocks():
    urls = ['https://www1.nseindia.com/content/indices/ind_nifty500list.csv',
            'https://www1.nseindia.com/content/indices/ind_niftymidcap150list.csv',
            'https://www1.nseindia.com/content/indices/ind_niftysmallcap250list.csv',
            'https://www1.nseindia.com/content/indices/ind_niftymicrocap250_list.csv']

    res = []
    for url in urls:
        try:
            s = requests.get(url).content
            df = pd.read_csv(io.StringIO(s.decode('utf-8')))
            stocks = df['Symbol'].tolist()
            for s in stocks:
                if s not in res:
                    res.append(s)
        except:
            print("error")
    print(len(res))
    return list(res)


def calculate_indicator_val_intraday():
    period = '3d'
    isbse = 0
    delete_keys(['atr_intraday_all'])
    stocks = get_nse_200_stocks()
    while True:
        dtobj = datetime.now(tz=gettz('Asia/Kolkata'))

        hour = int(dtobj.strftime("%H"))
        minutes = int(dtobj.strftime("%M"))

        while 9 <= hour <= 15:
            frames = {}
            if len(stocks) > 0 and (minutes % 10 == 1 or minutes % 10 == 6):
                print(stocks)
                for i in stocks:
                    ticker = yfinance.Ticker(ticker=i + '.NS')
                    # print(str(ticker))
                    dtobj = datetime.now(tz=gettz('Asia/Kolkata'))
                    frames[i] = ticker.history(interval='5m',
                                               period=period,
                                               end=dtobj)
                    # print(frames[i].tail(5))
                print("done loading df")
                for i in stocks:
                    # ticker = yfinance.Ticker(ticker=i+'.NS')
                    # print(str(ticker))
                    df = frames[i]
                    # for j in range(0, 75):
                    df_copy = df
                    # print(str(df_copy.tail()))
                    add_indicators_intraday(i, period, df_copy, isbse)
                    update_keys(['atr_intraday'])
            # print("stop" + str(dtobj))
            time.sleep(30)
            dtobj = datetime.now(tz=gettz('Asia/Kolkata'))
            hour = int(dtobj.strftime("%H"))
            minutes = int(dtobj.strftime("%M"))
            # break
        # if hour == 8:
        # print("Deleting intraday all")
        # delete_keys(['atr_intraday_all'])
        print("done")
        time.sleep(60 * 30)


def calculate_indicator_val_intraday_heiken():
    # res = random.sample(defaultstocks, 10)
    while True:
        dtobj = datetime.now(tz=gettz('Asia/Kolkata'))
        hour = int(dtobj.strftime("%H"))
        minute = int(dtobj.strftime("%M"))
        if hour == 19:
            stocks = get_intraday_stocks()[-20:]
            db['stocks'] = stocks
            print(stocks)
            print("start acc")
            stocks_acc = accumulation_dist(get_nse_500_stocks(), '2y')
            db['max_accumulation'] = stocks_acc
            print(stocks_acc)
            time.sleep(60 * 60)

        stocks = []
        # cou = -70
        while 9 <= hour <= 15:
            if 'stocks' in db.keys():
                stocks = list(db['stocks'])

            if len(stocks) > 0 and (minute % 10 == 1 or minute % 10 == 6):
                print("start")
                find_swing(stocks)
                # cou += 1
                update_keys(['ha_intraday'])
                print("stop")
            time.sleep(30)
            dtobj = datetime.now(tz=gettz('Asia/Kolkata'))
            hour = int(dtobj.strftime("%H"))
            minute = int(dtobj.strftime("%M"))
        print("done ha")
        time.sleep(60 * 15)


def intraday():
    t = Thread(target=calculate_indicator_val_intraday)
    t.start()


def intraday_ha():
    t = Thread(target=calculate_indicator_val_intraday_heiken)
    t.start()


async def run_app():
    print("hi")
    keep_alive()
    intraday()
    intraday_ha()
    # nse = Nse()
    while True:
        # dtobj = datetime.now(tz=gettz('Asia/Kolkata'))
        # print(dtobj)
        # hour = int(dtobj.strftime("%H"))
        # if hour == 23:
        #     all_stock_codes = [i.split(" ")[0] for i in nse.get_stock_codes()]
        #     await calculate_indicator_val(all_stock_codes, '1y', 0)
        #     update_keys(['atr', 'chaikin'])
        time.sleep(3600)


def HA(df):
    # print(ticker.get_info())
    df['Act_Close'] = df['Close']
    df['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4

    idx = df.index.name
    df.reset_index(inplace=True)

    for i in range(0, len(df)):
        if i == 0:
            df.loc[df.index[i], 'HA_Open'] = (df.loc[df.index[i], 'Open'] +
                                              df.loc[df.index[i], 'Close']) / 2
        else:
            df.loc[df.index[i],
                   'HA_Open'] = (df.loc[df.index[i - 1], 'HA_Open'] +
                                 df.loc[df.index[i - 1], 'HA_Close']) / 2

    if idx:
        df.set_index(idx, inplace=True)

    df['High'] = df[['HA_Open', 'HA_Close', 'High']].max(axis=1)
    df['Low'] = df[['HA_Open', 'HA_Close', 'Low']].min(axis=1)

    df['Open'] = df['HA_Open']
    df['Close'] = df['HA_Close']

    # plot_chart(df)
    return df


def update_keys(ind):
    for i in ind:
        buy_key = i + '_buy'
        data_buy = db[buy_key] if buy_key in db.keys() else []
        db[buy_key + '_latest'] = data_buy
        sell_key = i + '_sell'
        data_sell = db[sell_key] if sell_key in db.keys() else []
        db[sell_key + '_latest'] = data_sell
        if buy_key in db.keys():
            del db[buy_key]
        if sell_key in db.keys():
            del db[sell_key]


def delete_keys(ind):
    for i in ind:
        buy_key = i
        if buy_key in db.keys():
            del db[buy_key]


asyncio.run(run_app())
# print((get_nse_500_stocks()))
