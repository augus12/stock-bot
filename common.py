import yfinance
from replit import db


class IndicatorPos:
    def __init__(self, isBuy=False, isSell=False, position=0):
        self.isBuy = isBuy
        self.isSell = isSell
        self.position = position


async def get_historical_data(symbol, period, isbse):
    exc = '.NS' if isbse == 0 else '.BO'
    name = symbol + exc
    ticker = yfinance.Ticker(ticker=name)
    df = ticker.history(interval="1d", period=period)
    return ticker, df


def insert(stock, prefix, indicator, date):
    data = {}
    if stock in db.keys():
        data = db[stock]

    if indicator.isBuy:
        data[prefix + '_buy'] = date
        lis_key = prefix + '_buy'
        ind_list = db[lis_key] if lis_key in db.keys() else []
        ind_list.append(stock)
        db[lis_key] = list(set(ind_list))

    if indicator.isSell:
        data[prefix + '_sell'] = date
        lis_key = prefix + '_sell'
        ind_list = db[lis_key] if lis_key in db.keys() else []
        ind_list.append(stock)
        db[lis_key] = list(set(ind_list))
    data[prefix] = indicator.position
    db[stock] = data
