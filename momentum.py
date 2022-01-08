import logging

# from matplotlib import  pyplot as plt
import yfinance
# matplotlib.use('Agg')
from nsetools import Nse


# import matplotlib

def chai_momentum(stock, period, isbse=0):
    try:
        print(stock)
        short_ema_1 = 10
        short_ema_2 = 6
        long_ema_1 = 50
        long_ema_2 = 14

        df, ticker = HA(stock, period, isbse)

        # print( len(df.index.array))
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
        EMA_comp_2_mod = ((long_ema_1 - short_ema_1) / (long_ema_2 - short_ema_2)) * EMA_comp_2

        SMA_comp_1 = EMA_comp_1.rolling(window=1).mean()
        SMA_comp_2_mod = EMA_comp_2_mod.rolling(window=1).mean()

        # print(EMA_comp_2_mod)

        # EMA_comp_2_mod_current = EMA_comp_2_mod[1:]
        # EMA_comp_2_mod_previous = EMA_comp_2_mod.shift(1)[1:]
        # EMA_comp_1_current = EMA_comp_1[1:]
        # EMA_comp_1_previous = EMA_comp_1.shift(1)[1:]

        # pd.DataFrame(
        #     {'long': long,
        #      'long_risky': long_risky,
        #      'long_exit_soft': long_exit_soft,
        #      #  'short': short,
        #      'long_exit': long_exit
        #      #  'short_exit': short_exit
        #      },
        #     index=current.index)
        # df.iloc[0, 'buy'] = 0
        # df.iloc[0, 'sell'] = 0
        # print(df)
        # for j in range(1, len(df)):
        #     if df.loc[j-1, 'buy'] == 1 or (EMA_comp_2_mod[j] > EMA_comp_1[j] and (EMA_comp_2_mod[j - 1] < EMA_comp_1[j - 1]) and EMA_comp_2_mod[j]  > 0):  # line 9
        #         df.loc[j, 'buy'] = 1
        #         df.loc[j, 'sell'] = 0
        #         logging.info('Buy momentum stock: ' + stock)
        #         print('Buy momentum stock: ' + stock)
        #     elif df.loc[j-1, 'sell'] == 1 or EMA_comp_2_mod[j] < EMA_comp_1[j]:
        #         df.loc[j, 'sell'] = 1
        #         df.loc[j, 'buy'] = 0
        #     else:
        #         df.loc[j, 'buy'] = 0
        #         df.loc[j, 'sell'] = 0
        #     # xmax = len(df.index.array)
        #     # # logging.info('Checking ' + stock)
        # plt.plot(SMA_comp_1, color="seagreen")
        # plt.plot(SMA_comp_2_mod, color="blue")
        # plt.hlines(y=0, xmin=0, xmax=xmax)
        # # print(EMA_comp[i])
        # # print(EMA_comp[prev_i])
        # plt.show()
        if SMA_comp_2_mod[i] > SMA_comp_1[i] and (SMA_comp_2_mod[prev_i] < SMA_comp_1[prev_i]) and SMA_comp_2_mod[
            i] > 0:  # line 9
            logging.info('Buy momentum stock: ' + stock)
            print('Buy momentum stock: ' + stock)
            sector = ''
            if 'sector' in ticker.info.keys():
                sector = ' - ' + str(ticker.info['sector'])
            return stock + sector
        # elif df.loc[i, 'sell'] == 1 and df.loc[i - 1, 'sell'] == 0:
        #     logging.info('Sell momentum stock: ' + stock)
        #     print('Sell momentum stock: ' + stock)
    except Exception as e:
        logging.warning(str(e) + ' ' + stock)
    return None


def acc_dist(stock, period, short_ema, long_ema, threshold=0, isbse=0):
    try:
        df, ticker = HA(stock, period, isbse)
        print(stock)
        # print( len(df.index.array))
        df['Acc'] = df['Volume'] * ((df['Close'] - df['Open']) / (df['High'] - df['Low']))
        df['Acc_Cumulative'] = df['Acc'].cumsum()
        EMAs = [short_ema, long_ema]
        for i in EMAs:
            df["EMA_" + str(i)] = df['Acc_Cumulative'].ewm(span=i, adjust=False).mean()
        i = df.index.array[-1]
        print(str(i))
        prev_i = df.index.array[-2]
        EMA_short = df['EMA_' + str(short_ema)]
        EMA_long = df['EMA_' + str(long_ema)]
        EMA_comp = EMA_short - EMA_long
        xmax = len(df.index.array)
        logging.info('Checking ' + stock)
        # plt.plot(range(0, xmax),df['Acc_Cumulative'], color="seagreen")
        # plt.plot(range(0, xmax),df['EMA_6'], color="red")
        # plt.plot(range(0, xmax),df['EMA_14'], color="blue")
        SMA_comp = EMA_comp.rolling(window=1).mean()
        # plt.plot(SMA_comp, color="blue")
        # plt.show()
        # plt.hlines(y=0, xmin=0, xmax=xmax)
        print(EMA_comp[i])
        print(EMA_comp[prev_i])

        SMA_comp_max = SMA_comp.max()
        if SMA_comp_max > 1 and (SMA_comp_max - SMA_comp[i]) / (SMA_comp_max * 1.0) <= 0.1:
            logging.info(stock + " : max accumulation ")
            print(stock + " : max accumulation " + str(SMA_comp_max) + " " + str(SMA_comp[i]))
            sector = ''
            if 'sector' in ticker.info.keys():
                sector = ' - ' + str(ticker.info['sector'])
            # plt.show()
            # print(ticker.info)
            return stock + str(sector)

            # factor = -50 if EMA_comp[prev_i] < 0 else 50
        # if EMA_comp[i] >= threshold > EMA_comp[prev_i] and EMA_comp[i] > EMA_comp[prev_i]:  # line 9
        #     logging.info('Found chaikin acc: ' + stock)
        #     print('Found chaikin acc: ' + stock)
        #     # exc = '.NS' if isbse == 0 else '.BO'
        #     # name = stock + exc
        #     # ticker = yfinance.Ticker(name)
        #     # info = {}
        #     # try:
        #     #     info = ticker.get_info()
        #     #     logging.info(str(info))
        #     # except:
        #     #     pass
        #     # filt_info = {}
        #     # if 'previousClose' in info:
        #     #     filt_info['previousClose'] = info['previousClose']
        #     # if 'trailingPE' in info:
        #     #     filt_info['trailingPE'] = info['trailingPE']
        #     # if 'forwardPE' in info:
        #     #     filt_info['forwardPE'] = info['forwardPE']
        #     # if 'industry' in info:
        #     #     filt_info['industry'] = info['industry']
        #     # if 'sector' in info:
        #     #     filt_info['sector'] = info['sector']
        #     return stock
    except Exception as e:
        logging.warning(str(e) + ' ' + stock)
    return None


def accumulation_dist(stocks, period, isbse=0):
    res = []
    try:
        print(len(stocks))

        if len(stocks) == 0:
            nse = Nse()
            stocks = nse.get_stock_codes().keys()
        response = [chai_momentum(i, period, isbse) for i in list(stocks)]
        res = [val for val in response if val is not None]
        # logging.info("success: ")
        # print("success: ")
        return list(set(res))
    except Exception as e:
        print("error " + str(e))
        stocks = []
    return res


def HA(stock, period, is_bse):
    exc = '.NS' if is_bse == 0 else '.BO'
    name = stock + exc
    ticker = yfinance.Ticker(ticker=name)
    df_daily = ticker.history(interval="1d", period=period)
    df = df_daily.copy(deep=True)
    logic = {'Open': 'first',
             'High': 'max',
             'Low': 'min',
             'Close': 'last',
             'Volume': 'sum'}

    df = df.resample('W').apply(logic)
    # print(df)
    # print(ticker.get_info())
    df['Act_Close'] = df['Close']
    df["SMA_100"] = df['Close'].rolling(window=100).mean()
    df["SMA_50"] = df['Close'].rolling(window=50).mean()
    df = df.assign(HA_Close=(df['Open'] + df['High'] + df['Low'] + df['Close']) / 4)
    # print("h2")
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
        # print("h1")

    if idx:
        df.set_index(idx, inplace=True)

    df['High'] = df[['HA_Open', 'HA_Close', 'High']].max(axis=1)
    df['Low'] = df[['HA_Open', 'HA_Close', 'Low']].min(axis=1)

    df['Open'] = df['HA_Open']
    df['Close'] = df['HA_Close']

    # plot_chart(df)
    return df, ticker
# from nse_stocks import nifty_100_quality
# from nse_stocks import nse_stocks

# asyncio.run(chaikin_momentum(nse_stocks, '2y', 0))
# asyncio.run(puppies(nse_stocks_new, 0))
# max_acc = ['MPHASIS', 'SCHAEFFLER', 'VTL', 'UTIAMC', 'ORIENTELEC', 'ZENSARTECH', 'JUBLINGREA', 'JSL',
#            'ALLCARGO', 'JSLHISAR', 'HERANBA', 'ARVINDFASN', 'GIPCL', 'RANEHOLDIN', 'SHAREINDIA', 'XCHANGING',
#            'NELCAST', 'MIRZAINT', 'NITINSPIN', 'HITECH', 'ARTEMISMED', 'NIPPOBATRY', 'AHLWEST', 'MMP', 'PODDARMENT',
#            'AHLEAST', 'DCMNVL', 'ORBTEXP', 'ASPINWALL', 'MARALOVER', 'JOCIL', 'VIPCLOTHNG', 'GEEKAYWIRE', 'TAINWALCHM',
#            'BANARBEADS']
#
# success = ['JINDALSAW', 'SANOFI', 'GODREJAGRO', 'BLUESTARCO', 'PFC', 'ZENSARTECH', 'LAXMIMACH', 'CYIENT', 'PRSMJOHNSN', 'GAEL', 'INTELLECT', 'MMTC', 'JINDALSAW', 'BLUESTARCO', 'LAXMIMACH', 'CYIENT', 'PRSMJOHNSN', 'GAEL', 'MMTC', 'ADANIPORTS', 'ITC', 'GRASIM']
# accumulation_dist(nse_stocks, '2y')
