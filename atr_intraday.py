import logging
from datetime import datetime

import pandas as pd
import yfinance
from dateutil.tz import gettz
from replit import db

from common import IndicatorPos


def get_historical_data_intraday(symbol, period, isbse, skip):
    exc = '.NS' if isbse == 0 else '.BO'
    name = symbol + exc
    ticker = yfinance.Ticker(ticker=name)
    dtobj = datetime.now(tz=gettz('Asia/Kolkata'))
    df = ticker.history(interval='5m', period=period, end=dtobj)
    if symbol == 'CUB':
        print(df['Close'][:-skip].tail())

    return ticker, df[:-skip]

def add_indicators_intraday(stock, period, df, isbse=0):
    try:
        # ticker, df = get_historical_data_intraday(stock, period, isbse, end)
        # sf = df['Close']
        # date = str(pd.DataFrame({'Date': sf.index, 'Values': sf.values})['Date'].tolist()[-1]).split(" ")[0]

        ind_chai, price = ema(df, stock)

        # chaik, price = chai_momentum(df, stock)
        ind_atr, price = atr_strategy(df, stock, 21)
        score = ind_atr.position + ind_chai.position

        all = db['atr_intraday_all'] if 'atr_intraday_all' in db.keys() else {}
        if stock in all.keys() and all[stock]['action'] != 'exit_buy':
            insert_intraday(stock, 'atr_intraday', ind_atr, ind_chai, price, ['trend', 'momentum'], 1)
        else:
            # print(str(all[stock]['action']))
            print(str(ind_atr.isBuy))
            if  ind_atr.isBuy and ind_chai.isBuy:
                print("Found Intraday buy: " + stock + " price: " + str(price))
                insert_intraday(stock, 'atr_intraday', ind_atr, ind_chai, price, ['trend', 'momentum'])
            else:
              if 'atr_intraday_all' in db.keys():
                if stock in db['atr_intraday_all'].keys():
                  data = db['atr_intraday_all']
                  data[stock]['last_price'] = price
                  data[stock]['trend'] = ind_atr.position
                  data[stock]['momentum'] = ind_chai.position
                  db['atr_intraday_all'] = data

            # if ind_atr.isSell or ind_atr.isBuy:
            #     print("Found Intraday: " + stock + " price: " + str(price))
            #     insert_intraday(stock, 'atr_intraday', ind_atr, ind_chai, price, ['trend', 'momentum'])



    except Exception as e:
        print("Error: " + str(e))


def atr_strategy(df, stock, lookback, nATRMultip=5):
    try:
        high = df['High']
        low = df['Low']
        close = df['Close']
        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift(1)))
        tr3 = pd.DataFrame(abs(low - close.shift(1)))
        frames = [tr1, tr2, tr3]
        tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
        xATR = tr.ewm(lookback).mean()
        nLoss = nATRMultip * xATR
        xATRTrailingStop = [df['Close'][0] - nLoss[0]]
        pos = [0]
        count = 0

        for i in range(1, len(high)):
            c = close[i]
            c_prev = close[i - 1]
            if c > xATRTrailingStop[i - 1] and c_prev > xATRTrailingStop[i - 1]:
                xATRTrailingStop.append(max(xATRTrailingStop[i - 1], c - nLoss[i]))
            else:
                if (c < xATRTrailingStop[i - 1]) and c_prev < xATRTrailingStop[i - 1]:
                    # print(xATRTrailingStop[i - 1])
                    # print(close)
                    # print(nLoss[i])
                    xATRTrailingStop.append(min(xATRTrailingStop[i - 1], c + nLoss[i]))
                else:
                    if c > xATRTrailingStop[i - 1]:
                        xATRTrailingStop.append(c - nLoss[i])
                    else:
                        xATRTrailingStop.append(c + nLoss[i])
            if c_prev < xATRTrailingStop[i - 1] < c:
                pos.append(1)
            else:
                if c_prev > xATRTrailingStop[i - 1] > c:
                    pos.append(-1)
                else:
                    pos.append(pos[i - 1])
        for i in range(3, 30):
            if pos[-i] == -1:
              count += 1
      
        min_close = close[-20:-3].min()
        max_close = close[-20:-3].max()
        is_consolidating = min_close >= 0.996 * max_close and  close[-1] >= max_close*1.001 and close[-1] <= max_close*1.01

        if is_consolidating :
          print('{} is consolidating.', format(stock))

        indicator = IndicatorPos()
        if pos[-1] == -1 and pos[-2] == -1:
            print("sell: " + stock)
            indicator.isSell = True
            indicator.position = -2
        elif is_consolidating:
            print("buy consolidating: " + stock)
            indicator.isBuy = True
            indicator.position = 5
        # elif (pos[-1] == 1 and count >=20):
        #     print("buy: " + stock)
        #     indicator.isBuy = True
        #     indicator.position = 2
        else:
            indicator.position = pos[-1]
        return indicator, df['Close'][-1]
    except Exception as e:
        print("error: " + str(e))
    return IndicatorPos(), 0


def ema(df, stock):
    try:
        short_ema_1 = 10
        long_ema_1 = 21
        very_short = 5
        EMAs = [short_ema_1, very_short, long_ema_1]
        for i in EMAs:
            df["EMA_" + str(i)] = df['Close'].ewm(span=i, adjust=False).mean()

        df["Vol_EMA_21"] = df['Volume'].ewm(span=30, adjust=False).mean()
        i = df.index.array[-1]
        prev_i = df.index.array[-2]
        prev_p_i = df.index.array[-3]

        close = df['Close']
        open_df = df['Open']
        ema_df = df['EMA_21']
        short_ema_df = df['EMA_10']
        vol_ema = df["Vol_EMA_21"] 
        vol = df["Volume"] 
        # v_s_ema = df['EMA_5']

        indicator = IndicatorPos()
        if close[prev_i] > ema_df[prev_i] and close[i] > ema_df[i] and (vol[i] >= 2*vol_ema[i] or vol[prev_i] >= 2*vol_ema[prev_i]):
                #  and close[i] >= 1.003 * open[i]  
           
            print(vol[i])
            print(vol_ema[i])
            indicator.position = 3
            print("ema buy "+ str(close[i]))
            indicator.isBuy = True
        elif close[i] < short_ema_df[i] and close[prev_i] < short_ema_df[prev_i] :
            print("exit buy ema " + str(close[i]))
            indicator.position = 0
            indicator.isSell = True
        elif close[prev_i] > ema_df[prev_i] and close[i] > ema_df[i]:
            indicator.position = 3
            # indicator.isBuy = True
        elif close[i] > ema_df[i]:
            indicator.position = 2
        elif close[prev_i] < ema_df[prev_i] and close[
            i] < ema_df[i]:
            print("exit buy ema: " + str(close[i]))
            indicator.position = -1
            indicator.isSell = True
        else:
            indicator.position = -1
        return indicator, close[i]
    except Exception as e:
        print("error: " + str(e))
    return IndicatorPos(), 0


def chai_momentum(df, stock):
    try:
        short_ema_1 = 10
        short_ema_2 = 6
        long_ema_1 = 50
        long_ema_2 = 14

        df['Acc'] = df['Volume'] * ((df['Close'] - df['Open']) / (df['High'] - df['Low']))
        df['Acc_Cumulative'] = df['Acc'].cumsum()
        EMAs = [short_ema_1, long_ema_1, short_ema_2, long_ema_2]
        for i in EMAs:
            df["EMA_" + str(i)] = df['Acc_Cumulative'].ewm(span=i, adjust=False).mean()
        i = df.index.array[-1]
        prev_i = df.index.array[-2]
        EMA_short_1 = df['EMA_' + str(short_ema_1)]
        EMA_long_1 = df['EMA_' + str(long_ema_1)]
        EMA_comp_1 = EMA_short_1 - EMA_long_1

        EMA_short_2 = df['EMA_' + str(short_ema_2)]
        EMA_long_2 = df['EMA_' + str(long_ema_2)]
        EMA_comp_2 = EMA_short_2 - EMA_long_2

        multiplier = 5

        score = 0


        EMA_comp_2_mod = ((long_ema_1 - short_ema_1) / (long_ema_2 - short_ema_2)) * EMA_comp_2

        extra = True if (EMA_comp_2_mod[prev_i] < 0 and EMA_comp_2_mod[i] > -multiplier * EMA_comp_2_mod[prev_i]) or (
                EMA_comp_2_mod[prev_i] > 0 and EMA_comp_2_mod[i] > multiplier * EMA_comp_2_mod[prev_i]) else False
        extra_sell = True if (EMA_comp_2_mod[prev_i] < 0 and EMA_comp_2_mod[i] < multiplier * EMA_comp_2_mod[
            prev_i]) or (EMA_comp_2_mod[prev_i] > 0 and EMA_comp_2_mod[i] < -multiplier * EMA_comp_2_mod[
            prev_i]) else False

        if extra:
            score += 2

        if EMA_comp_2_mod[i] > EMA_comp_1[i]:
            score += 1

        if EMA_comp_2_mod[i] > 10000:
            score += 1

        if extra_sell:
            score -= 1

        if EMA_comp_2_mod[i] < EMA_comp_1[i]:
            score -= 1
        if EMA_comp_2_mod[i] < -10000:
            score -= 1

        indicator = IndicatorPos()
        if score > 2:  # line 9
            logging.info('Found momentum stock: ' + stock)
            print('Found momentum stock: ' + stock + ' ' + str(EMA_comp_2_mod[i]))
            indicator.isBuy = True
            indicator.position = score
        elif score < -2:  # line 9
            logging.info('Sell momentum stock: ' + stock)
            print('Sell momentum stock: ' + stock + ' ' + str(EMA_comp_2_mod[i]))
            indicator.isSell = True
            indicator.position = score
        else:
            indicator.position = score
        return indicator, df['Close'][i]
    except Exception as e:
        logging.warning(str(e) + ' ' + stock)
    return IndicatorPos(), 0


def create_summary(stock, price, p_indicator, s_indicator, val_keys, prev, action, common):
    prev[val_keys[0]] = p_indicator.position
    prev[val_keys[1]] = s_indicator.position
    if action is not None:
        if 'action' in prev.keys():
            if prev['action'] != action:
                prev[action + '_price'] = price
        else:
            prev[action + '_price'] = price
        if action == 'exit_buy':
            profit = prev['profit'] if 'profit' in prev.keys() else 0
            cur_profit = (prev['exit_buy_price'] - prev['buy_price']) / prev['buy_price']
            profit += cur_profit * 100
            prev['profit'] = profit
            trades = prev['trades'] if 'trades' in prev.keys() else 0
            trades += 1
            prev['trades'] = trades
        prev['action'] = action
    prev['last_price'] = price
    if common == 1:
        prev['is_new'] = False
    else:
        prev['is_new'] = True
    return prev


def insert_intraday(stock, prefix, p_indicator, s_indicator, price, val_keys, common=0):
    all_key = prefix + '_all'
    if p_indicator.position > 2:
        lis_key = prefix + '_buy'
        ind_list = db[lis_key] if lis_key in db.keys() else []
        ind_list.append(stock)
        db[lis_key] = list(set(ind_list))

    if p_indicator.position < -2:
        lis_key = prefix + '_sell'
        ind_list = db[lis_key] if lis_key in db.keys() else []
        ind_list.append(stock)
        db[lis_key] = list(set(ind_list))

    prev = {}
    score = p_indicator.position + s_indicator.position
    action = None

    if common == 1:
        action = 'exit_buy' if p_indicator.isSell and s_indicator.isSell else None 
    else:
        action = 'buy' if p_indicator.isBuy and s_indicator.isBuy else  None

        # ('exit_sell' if score > -1 else None)

    if all_key in db.keys():
        data = db[all_key]
        if stock in db[all_key].keys():
            prev = data[stock]
            if common == 1 and 'action' in prev.keys() and prev['action'] == 'buy' and p_indicator.position > 0 and prev['buy_price'] > price and ((price - prev['buy_price']) / prev['buy_price'] < -0.02):
                action = 'exit_buy'
            elif common == 1 and 'action' in prev.keys() and prev['action'] == 'buy' and action == 'exit_buy' and prev[
                'buy_price'] >= price and ((price - prev['buy_price']) / prev['buy_price'] > -0.006):
                action = None
            elif common == 1 and 'action' in prev.keys() and prev['action'] == 'buy' and (p_indicator.isSell or s_indicator.isSell) and prev[
                'buy_price'] <= price and ((price - prev['buy_price']) / prev['buy_price'] > 0.006):
                action = 'exit_buy'
            # if common == 1 and 'action' in prev.keys() and prev['action'] == 'buy' and prev[
            #     'buy_price'] > price and ((price - prev['buy_price']) / prev['buy_price'] < -0.005):
            #     action = 'exit_buy'
            elif common == 1 and 'action' in prev.keys() and prev['action'] == 'buy' and action == 'exit_buy' and prev[
                'buy_price'] <= price and ((price - prev['buy_price']) / prev['buy_price'] < 0.003):
                action = None
            elif common == 1 and 'action' in prev.keys() and prev['action'] == 'buy' and prev[
                'buy_price'] <= price and ((price - prev['buy_price']) / prev['buy_price'] >= 0.03):
                action = 'exit_buy'
            # elif common == 1 and 'action' in prev.keys() and prev['action'] == 'buy' and score <= 2 and prev[
            #     'buy_price'] < price and ((price - prev['buy_price']) / prev['buy_price'] >= 0.008):
            #     action = 'exit_buy'
            # if common == 1 and 'action' in prev.keys() and prev['action'] == 'buy' and prev[
            #     'buy_price'] < price and ((price - prev['buy_price']) / prev['buy_price'] >= 0.008):
            #     action = 'exit_buy'
            if 'action' in prev.keys() and prev['action'] == 'buy' and action == 'exit_sell':
                action = None
            elif 'action' in prev.keys() and prev['action'] == 'sell' and action == 'exit_buy':
                action = None
            cur = create_summary(stock, price, p_indicator, s_indicator, val_keys, prev, action, common)
            data[stock] = cur
            db[all_key] = data
        else:
            data = db[all_key]
            cur = create_summary(stock, price, p_indicator, s_indicator, val_keys, prev, action, common)
            data[stock] = cur
            db[all_key] = data
    else:
        data = {}
        cur = create_summary(stock, price, p_indicator, s_indicator, val_keys, prev, action, common)
        data[stock] = cur
        db[all_key] = data
