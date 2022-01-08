import logging

from common import IndicatorPos


async def chai_momentum(df, stock):
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

        EMA_comp_2_mod = ((long_ema_1 - short_ema_1) / (long_ema_2 - short_ema_2)) * EMA_comp_2
        extra = EMA_comp_2_mod[i] > 10000
        indicator = IndicatorPos()
        if EMA_comp_2_mod[i] > EMA_comp_1[i] and (EMA_comp_2_mod[prev_i] < EMA_comp_1[prev_i]) and extra:  # line 9
            logging.info('Found momentum stock: ' + stock)
            print('Found momentum stock: ' + stock + ' ' + str(EMA_comp_2_mod[i]))
            indicator.isBuy = True
            indicator.position = 2
        elif EMA_comp_2_mod[i] < EMA_comp_1[i] < -50000 and (EMA_comp_2_mod[prev_i] > EMA_comp_1[prev_i]):  # line 9
            logging.info('Sell momentum stock: ' + stock)
            print('Sell momentum stock: ' + stock + ' ' + str(EMA_comp_2_mod[i]))
            indicator.isSell = True
            indicator.position = -1
        elif EMA_comp_1[i] > 0:
            indicator.position = 1
        else:
            indicator.position = -1
        return indicator
    except Exception as e:
        logging.warning(str(e) + ' ' + stock)
    return IndicatorPos()


