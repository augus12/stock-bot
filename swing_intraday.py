import logging

import numpy as np
import pandas as pd
import yfinance
from replit import db
# import mplfinance as mpf
# import matplotlib
# from matplotlib import pyplot as plt
# from io import BytesIO
from datetime import datetime

# matplotlib.use('Agg')

def HA(stock, period):
    name = stock + '.NS'
    ticker = yfinance.Ticker(name)
    df = ticker.history(interval="5m", period=period)
    dt = df.index.array[-1]
    dt_obj = datetime.strptime(str(dt), '%Y-%m-%d %H:%M:%S%z')
# hour = int(dt_obj.strftime("%H"))
    minute = int(dt_obj.strftime("%M"))
    print(minute)
    df = df if minute%5 == 0 else df.iloc[: -1]
    df['Act_Close'] = df['Close']
    df["SMA_100"] = df['Close'].rolling(window=100).mean()
    df["SMA_50"] = df['Close'].rolling(window=50).mean()
    df['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4

    idx = df.index.name
    df.reset_index(inplace=True)

    for i in range(0, len(df)):
        if i == 0:
            df.loc[df.index[i], 'HA_Open'] = (df.loc[df.index[i], 'Open'] + df.loc[df.index[i], 'Close']) / 2
        else:
            df.loc[df.index[i], 'HA_Open'] = (df.loc[df.index[i - 1], 'HA_Open'] + df.loc[
                df.index[i - 1], 'HA_Close']) / 2
        df.loc[df.index[i], 'MA_Diff'] = df.loc[df.index[i], 'Close'] - df.loc[df.index[i], 'SMA_50']
        df.loc[df.index[i], 'Percent'] = df.loc[df.index[i], 'MA_Diff'] / df.loc[df.index[i], 'Close']
        df.loc[df.index[i], 'near'] = df.loc[df.index[i], 'Percent'] <= 0.05

    if idx:
        df.set_index(idx, inplace=True)

    df['High'] = df[['HA_Open', 'HA_Close', 'High']].max(axis=1)
    df['Low'] = df[['HA_Open', 'HA_Close', 'Low']].min(axis=1)

    df['Open'] = df['HA_Open']
    df['Close'] = df['HA_Close']
    # print(df.tail(5))

    # plot_chart(df)
    return df


def getLongSignals(long, long_risk, long_exit_small, long_exit, price1, price2, factor1=1.0, factor2=1.0):
    long_signal = []  # 1
    long_risk_signal = []  # 2
    long_exit_small_signal = []  # 3
    long_exit_signal = []  # 4
    prev = 0
    for date, value in long.iteritems():
        if long[date] and prev != 1:
            long_signal.append(price1[date] * factor1)
            long_risk_signal.append(np.nan)
            long_exit_small_signal.append(np.nan)
            long_exit_signal.append(np.nan)
            prev = 1
        elif long_risk[date] and prev != 2:
            long_risk_signal.append(price1[date] * factor1)
            long_signal.append(np.nan)
            long_exit_small_signal.append(np.nan)
            long_exit_signal.append(np.nan)
            prev = 2
        elif long_exit[date] and prev != 4:
            long_exit_signal.append(price2[date] * factor2)
            long_signal.append(np.nan)
            long_risk_signal.append(np.nan)
            long_exit_small_signal.append(np.nan)
            prev = 4
        # elif long_exit_small[date] and prev != 3 and prev != 4:
        #     long_exit_small_signal.append(price2[date] * factor2)
        #     long_signal.append(np.nan)
        #     long_risk_signal.append(np.nan)
        #     long_exit_signal.append(np.nan)
        #     prev = 3
        else:
            long_signal.append(np.nan)
            long_risk_signal.append(np.nan)
            long_exit_small_signal.append(np.nan)
            long_exit_signal.append(np.nan)

    return long_signal, long_risk_signal, long_exit_small_signal, long_exit_signal


def get_exit_index(buy_or_sell, le_arr, l_arr, lr_arr, prev):
    for i in range(prev, -1):
        if buy_or_sell == 1 and (le_arr[i] is not np.nan):
            return i
        if buy_or_sell == 0 and ((l_arr[i] is not np.nan) or (lr_arr[i] is not np.nan)):
            return i
    return 0


nse_stocks = ["ACC", "AUBANK", "AARTIIND", "ABBOTINDIA", "ADANIENT", "ADANIGREEN", "ADANIPORTS", "ATGL", "ADANITRANS",
              "ABCAPITAL", "ABFRL", "AJANTPHARM", "APLLTD", "ALKEM", "AMARAJABAT", "AMBUJACEM", "APOLLOHOSP",
              "APOLLOTYRE", "ASHOKLEY", "ASIANPAINT", "AUROPHARMA", "DMART", "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE",
              "BAJAJFINSV", "BAJAJHLDNG", "BALKRISIND", "BANDHANBNK", "BANKBARODA", "BANKINDIA", "BATAINDIA",
              "BERGEPAINT", "BEL", "BHARATFORG", "BHEL", "BPCL", "BHARTIARTL", "BIOCON", "BBTC", "BOSCHLTD",
              "BRITANNIA", "CESC", "CADILAHC", "CANBK", "CASTROLIND", "CHOLAFIN", "CIPLA", "CUB", "COALINDIA",
              "COFORGE", "COLPAL", "CONCOR", "COROMANDEL", "CROMPTON", "CUMMINSIND", "DLF", "DABUR", "DALBHARAT",
              "DEEPAKNTR", "DHANI", "DIVISLAB", "DIXON", "LALPATHLAB", "DRREDDY", "EICHERMOT", "EMAMILTD", "ENDURANCE",
              "ESCORTS", "EXIDEIND", "FEDERALBNK", "FORTIS", "GAIL", "GMRINFRA", "GLENMARK", "GODREJAGRO", "GODREJCP",
              "GODREJIND", "GODREJPROP", "GRASIM", "GUJGASLTD", "GSPL", "HCLTECH", "HDFCAMC", "HDFCBANK", "HDFCLIFE",
              "HAVELLS", "HEROMOTOCO", "HINDALCO", "HAL", "HINDPETRO", "HINDUNILVR", "HINDZINC", "HDFC", "ICICIBANK",
              "ICICIGI", "ICICIPRULI", "ISEC", "IDFCFIRSTB", "ITC", "IBULHSGFIN", "INDIAMART", "INDHOTEL", "IOC",
              "IRCTC", "IGL", "INDUSTOWER", "INDUSINDBK", "NAUKRI", "INFY", "INDIGO", "IPCALAB", "JSWENERGY",
              "JSWSTEEL", "JINDALSTEL", "JUBLFOOD", "KOTAKBANK", "L&TFH", "LTTS", "LICHSGFIN", "LTI", "LT",
              "LAURUSLABS", "LUPIN", "MRF", "MGL", "M&MFIN", "M&M", "MANAPPURAM", "MARICO", "MARUTI", "MFSL",
              "MINDTREE", "MOTHERSUMI", "MPHASIS", "MUTHOOTFIN", "NATCOPHARM", "NMDC", "NTPC", "NAVINFLUOR",
              "NESTLEIND", "NAM-INDIA", "OBEROIRLTY", "ONGC", "OIL", "PIIND", "PAGEIND", "PETRONET", "PFIZER",
              "PIDILITIND", "PEL", "POLYCAB", "PFC", "POWERGRID", "PRESTIGE", "PGHH", "PNB", "RBLBANK", "RECLTD",
              "RELIANCE", "SBICARD", "SBILIFE", "SRF", "SANOFI", "SHREECEM", "SRTRANSFIN", "SIEMENS", "SBIN", "SAIL",
              "SUNPHARMA", "SUNTV", "SYNGENE", "TVSMOTOR", "TATACHEM", "TCS", "TATACONSUM", "TATAELXSI", "TATAMOTORS",
              "TATAPOWER", "TATASTEEL", "TECHM", "RAMCOCEM", "TITAN", "TORNTPHARM", "TORNTPOWER", "TRENT", "UPL",
              "ULTRACEMCO", "UNIONBANK", "UBL", "MCDOWELL-N", "VGUARD", "VBL", "VEDL", "IDEA", "VOLTAS", "WHIRLPOOL",
              "WIPRO", "ZEEL"]


def find_swing(stocks, cou=0, time=0, all=0, client_loop=None):
    swing_long = []
    swing_long_risky = []
    swing_long_exit = []

    result = []
    result_risky_buy = []
    result_exit = []
    # date = ""
    for stock in stocks:
        try:
            print(stock)
            df_ha = HA(stock, '3d')
            # [:cou]

            # date = str(df_ha.index[-1 + time]).split(" ")[0]
            prev = (time - 1) if time != 0 else -2
            up = u'\u2B06'
            down = u'\u2B07'

            strategy = trades(df_ha)

            df_ha['long'] = strategy['long']
            df_ha['long_risky'] = strategy['long_risky']
            df_ha['long_exit'] = strategy['long_exit']
            df_ha['long_exit_soft'] = strategy['long_exit_soft']
            index = -1 + time
            l_arr, lr_arr, les_arr, le_arr = getLongSignals(df_ha['long'],
                                                            df_ha['long_risky'],
                                                            df_ha['long_exit_soft'],
                                                            df_ha['long_exit'],
                                                            df_ha['Low'], df_ha['High'], 0.98, 1.01)
            runner = u'\U0001F3C3'
            short_ema = 9
            long_ema = 18
            EMAs = [short_ema, long_ema]
            for i in EMAs:
                df_ha["EMA_" + str(i)] = df_ha['Close'].ewm(span=i, adjust=False).mean()
            
            ema_short = df_ha["EMA_9"]
            ema_long = df_ha["EMA_18"]
            count_decline = 0
            for i in range(1, 20):
                if ema_short[-i] < ema_long[-i]: 
                  count_decline += 1

            dt = df_ha.index.array[-1]
            dt_obj = datetime.strptime(str(dt), '%Y-%m-%d %H:%M:%S%z')
            hour = int(dt_obj.strftime("%H"))
            minute = int(dt_obj.strftime("%M"))
            cur_prof = 0
            data = {} if stock+'_ha' not in db.keys() else db[stock+'_ha']
            close = df_ha['Close']
            min_close = close[-15:-2].min()
            max_close = close[-15:-2].max()
            is_consolidating_or_reversal = (min_close >= 0.996 * max_close) or count_decline >= 15


            if 'buy' in data.keys() and (le_arr[index] is not np.nan or (hour >= 15)):
                if ('buy' in data.keys() and hour == 15 and minute>=15):
                  logging.info("Manual exit: " + stock)
              # and (ema_short[-1] > df_ha['Close'][-1]):
                logging.info("Found HA exit: " + stock)
                print("Found HA exit: " + stock)
                data = {} if stock+'_ha' not in db.keys() else db[stock+'_ha']
                data['sell'] = np.around(df_ha['Act_Close'][index], 2)
                if 'buy' in data.keys():
                  profit = data['profit'] if 'profit' in data.keys() else 0
                  trades_count = data['trades'] if 'trades' in data.keys() else 0
                  trades_count += 1
                  cur_profit = np.around((data['sell'] - data['buy'])*100.0/data['buy'], 2)
                  profit += cur_profit
                  cur_prof = cur_profit
                  data['profit'] = np.around(profit, 2)
                  data['trades'] = trades_count
                  del data['buy']

                db[stock + "_ha"] = data
                running = 0
                change = cur_prof
                is_profit = u'\U0001F7E2' if change > 0 else u'\U0001F7E1'
                change_str = "   " + str(abs(change)) + "% " + (up if change > 0 else down) + ' ' + is_profit
                change_str = change_str + (" " + runner if running == 1 else "")
                result_exit.append('*' + stock + '*' + change_str)
            elif hour < 15 and (is_consolidating_or_reversal and (l_arr[index] is not np.nan or lr_arr[index] is not np.nan)):
              # and (ema_short[-2] < ema_long[-2] and ema_short[-1] > ema_long[-1]):
                logging.info("Found HA buy: " + stock)
                print("Found HA buy: " + stock)
                curr = get_exit_index(1, le_arr, l_arr, lr_arr, prev)
                data = {} if stock+'_ha' not in db.keys() else db[stock+'_ha']
                data['buy'] = np.around(df_ha['Act_Close'][index], 2)
                db[stock + "_ha"] = data
                running = 1 if curr == 0 else 0
                if curr == 0:
                    curr = -1
                change = round((df_ha['Act_Close'][curr] - df_ha['Act_Close'][prev]) * 100 / df_ha['Act_Close'][prev], 2)
                change_str = "   " + str(abs(change)) + "% " + (up if change > 0 else down)
                change_str = change_str + (" " + runner if running == 1 else "")
                result.append('*' + stock + '* ' + str(db[stock + "_ha"]['buy']) + ' ' + runner)
            elif lr_arr[index] is not np.nan:
                print("Found HA risky buy: " + stock)
                curr = get_exit_index(1, le_arr, l_arr, lr_arr, prev)
                running = 1 if curr == 0 else 0
                if curr == 0:
                    curr = -1
                change = round((df_ha['Act_Close'][curr] - df_ha['Act_Close'][prev]) * 100 / df_ha['Act_Close'][prev], 2)
                change_str = "   " + str(abs(change)) + "% " + (up if change > 0 else down)
                change_str = change_str + (" " + runner if running == 1 else "")
                result_risky_buy.append('*' + stock + '*' + change_str)

        except:
            logging.warning("error in " + stock)

    if all != -1:
        swing_long.extend(result)
        swing_long_risky.extend(result_risky_buy)
        swing_long_exit.extend(result_exit)

        swing_long = list(set(swing_long))
        swing_long_risky = list(set(swing_long_risky))
        swing_long_exit = list(set(swing_long_exit))

    res = {}
    res['indicator'] = 'HA - Intraday'
    res['buy'] = swing_long
    res['exit_buy'] = swing_long_exit
    db['ha_intraday_buy'] = swing_long
    db['ha_intraday_sell'] = swing_long_exit

    return res
    # res['exit_sell'] = []    if all != 1 and all != -1:
    #     swing_list(bot, chat_id, all, swing_long, swing_long_risky, swing_long_exit, date, client_loop,
    #                      'Swing watchlist')
    # elif all == -1:
    #     swing_list(bot, chat_id, all, result, result_risky_buy, result_exit, date, client_loop, 'Swing watchlist')




# def plot_chart_intraday(stock):
#     try:
#         plt.rc('font', size=14)
#         df = HA(stock, period='5d')
#         strategy = trades(df)
#         df['Date'] = range(df.shape[0])
#         df = df.loc[:, ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'near']]
#         strategy['Date'] = range(strategy.shape[0])
#         df['long'] = strategy['long']
#         df['long_risky'] = strategy['long_risky']
#         df['long_exit'] = strategy['long_exit']
#         df['long_exit_soft'] = strategy['long_exit_soft']

#         l_arr, lr_arr, les_arr, le_arr = getLongSignals(df.iloc[-110:]['long'], df.iloc[-110:]['long_risky'], df.iloc[-110:]['long_exit_soft'], df.iloc[-110:]['long_exit'],
#                        df.iloc[-110:]['Low'], df.iloc[-110:]['High'], 0.995, 1.005)

#         isnanl = True
#         isnanlr = True
#         isnanles = True
#         isnanle = True

#         for ele in l_arr:
#             if not np.isnan(ele):
#                 isnanl = False
#                 break

#         for ele in lr_arr:
#             if not np.isnan(ele):
#                 isnanlr = False
#                 break

#         for ele in les_arr:
#             if not np.isnan(ele):
#                 isnanles = False
#                 break

#         for ele in le_arr:
#             if not np.isnan(ele):
#                 isnanle = False
#                 break


#         go_long = mpf.make_addplot(l_arr, type='scatter', markersize=10, marker='^', color = 'green')
#         exit_long = mpf.make_addplot(le_arr, type='scatter', markersize=10, marker='v', color='red')
#         exit_long_soft = mpf.make_addplot(les_arr, type='scatter', markersize=10, marker='v', color='gray')
#         risky_long = mpf.make_addplot(lr_arr, type='scatter', markersize=10, marker='^', color='blue')

#         plots = []
#         if not isnanl:
#             plots.append(go_long)
#         if not isnanlr:
#             plots.append(risky_long)
#         if not isnanle:
#             plots.append(exit_long)
#         if not isnanles:
#             plots.append(exit_long_soft)
#         # setup = dict(type='candle', volume=True, mav=(7, 15, 22))
#         # mpf.plot(df.iloc[0: 40], **setup)
#         mpf.plot(df.iloc[-110:], type='candle', style='charles', mav=(9, 18),
#                  volume=True,addplot=plots)
#         # plt.show()
#         output = BytesIO()
#         plt.gcf().savefig(output, format="png")
#         image_as_string = output.getvalue()
#         logging.info("Sending ha plot..")
#         return image_as_string
#         # bot.send_photo(chat_id=chat_id, photo=image_as_string, caption="#" + stock)
#     except:
#         logging.warning("error in plot_chart")
#     return None

def trades(df):
    current = df[1:]
    previous = df.shift(1)[1:]
    previous_prev = df.shift(2)[1:]

    current_close_to_ma = df['near']
    # current_vol_increase = previous['Volume'] < current['Volume']
    # previous_prev_bearish = previous_prev['Close'] < previous_prev['Open']

    latest_bearish = current['Close'] < current['Open']
    # previous_bearish = previous['Close'] < previous['Open']

    # previous_reversal = (previous['Open'] < previous['High']) & (previous['Low'] < previous['Open'])
    # current_reversal = (current['Open'] < current['High']) & (current['Low'] < current['Open'])

    current_candle_longer = (np.abs(current['Close'] - current['Open']) > np.abs(previous['Close'] - previous['Open']))

    # current_candle_shorter = (np.abs(current['Close'] - current['Open']) < np.abs(previous['Close'] - previous['Open']))

    # print(np.divide(np.abs(current['Close'] - previous['Close']), previous['Close'])[-1])
    # current_candle_size = np.divide(np.abs(current['Close'] - previous['Close']), previous['Close']) <= 0.05
    current_open_eq_low = current['Open'] == current['Low']
    current_open_eq_high = current['Open'] >= 0.998 * current['High']
    # current_open_eq_high_soft = current['Open'] >= 0.985 * current['High']

    current_width = np.divide(abs(current['Open'] - current['Close']), current['Open']) >= 0.002
    long = (
            ~latest_bearish
            & current_close_to_ma
            # & current_vol_increase
            # & current_candle_size
            & current_candle_longer
            # & (((previous_reversal & previous_bearish) | (
            #     previous_prev_bearish & previous_reversal)) | previous_bearish)
            & current_open_eq_low)

    long_risky = (
            ~latest_bearish
            & ~current_close_to_ma
            # & current_vol_increase
            # & current_candle_size
            & current_candle_longer
            # & (((previous_reversal & previous_bearish) | (
            #     previous_prev_bearish & previous_reversal)) | previous_bearish)
            & current_open_eq_low)

    long_exit = (
            latest_bearish
            #  & ~previous_bearish
            & (current_open_eq_high & current_width)

    )
    long_exit_soft = (
            latest_bearish
            #      & ~previous_bearish
            & ~(current_open_eq_high & current_width)
            & (current_open_eq_high | current_width)
    )
    return pd.DataFrame(
        {'long': long,
         'long_risky': long_risky,
         'long_exit_soft': long_exit_soft,
         #  'short': short,
         'long_exit': long_exit
         #  'short_exit': short_exit
         },
        index=current.index)

# plot_chart(1,1, 'DIVISLAB')
