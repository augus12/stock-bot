import asyncio

import pandas as pd

from chaikin import chai_momentum
from common import get_historical_data, insert
from nse_supertrend import atr_strategy


async def add_indicators(stock, period, isbse=0):
    try:
        ticker, df = await get_historical_data(stock, period, isbse)
        sf = df['Close']
        date = str(pd.DataFrame({'Date': sf.index, 'Values': sf.values})['Date'].tolist()[-1]).split(" ")[0]

        ind_chai = await chai_momentum(df, stock)
        ind_atr = await atr_strategy(df, stock, 21, 6.3)

        insert(stock, 'chaikin', ind_chai, date)
        insert(stock, 'atr', ind_atr, date)
    except Exception as e:
        print("Error: " + str(e))


async def calculate_indicator_val(stocks, period, isbse=0):
    coros = [add_indicators(i, period, isbse) for i in stocks]
    await asyncio.gather(*coros)
