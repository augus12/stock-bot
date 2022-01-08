import pandas as pd

from common import IndicatorPos


async def atr_strategy(df, stock, lookback, nATRMultip=6.3):
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
        for i in range(1, len(high)):
            c = close[i]
            c_prev = close[i - 1]
            if c > xATRTrailingStop[i - 1] and c_prev > xATRTrailingStop[i - 1]:
                xATRTrailingStop.append(max(xATRTrailingStop[i - 1], c - nLoss[i]))
            else:
                if (c < xATRTrailingStop[i - 1]) and c_prev < xATRTrailingStop[i - 1]:
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
        indicator = IndicatorPos()
        if pos[-1] == -1 and pos[-2] != -1:
            print("sell: " + stock)
            indicator.isSell = True
            indicator.position = -1
        elif pos[-1] == 1 and pos[-2] != 1:
            print("buy: " + stock)
            indicator.isBuy = True
            indicator.position = 1
        else:
            indicator.position = pos[-1]
        return indicator
    except Exception as e:
        print("error: " + str(e))
    return IndicatorPos()

# asyncio.run(get_supertrend_stocks(nse_stocks, '2mo', 3, 21, 0))
# asyncio.run(get_atr_stocks(nse_stocks_new, '1y', 6.3, 21, 1))
