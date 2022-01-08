from threading import Thread

from flask import Flask
from flask import json
from replit import db
# from swing_intraday import plot_chart_intraday

app = Flask(  # Create a flask app
	__name__,
	template_folder='templates',  # Name of html file folder
	static_folder='static'  # Name of directory for static files
)

@app.route('/')
def home():
    return 'Welocme'

@app.route("/add-ha/<stock>")
def add_stock(stock):
    res = {}
    res['indicator'] = 'Stock added successfully'
    res['buy'] = []
    res['sell'] = []
    extra = []
    current = []
    if 'intraday-extra' in db.keys():
      current = list(db['intraday-extra'])
    extra.extend(current)
    extra.append(stock)
    db['intraday-extra'] = list(set(extra))

    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/extra-ha")
def extra_stock():
    res = {}
    res['indicator'] = 'Extra Stocks'
    res['buy'] = []
    res['sell'] = []
    extra = []
    current=[]
    if 'intraday-extra' in db.keys():
      current = list(db['intraday-extra'])
    
    extra.extend(current)
    res['buy'] = extra
    
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/intraday-ha")
def intraday_stocks():
    res = {}
    res['indicator'] = 'HA intraday stocks - today'
    res['buy'] = []
    res['sell'] = []
    cur = []
    extra = []

    if 'stocks' in db.keys():
      cur = list(db['stocks'])

    if 'intraday-extra' in db.keys():
      extra = db['intraday-extra']
    
    for stk in extra:
      if stk.upper() not in cur:
        cur.append(stk)
    
    res['buy'] = cur
    
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    return response



@app.route("/reset-ha")
def reset_stocks():
    res = {}
    res['indicator'] = 'All stocks removed successfully'
    res['buy'] = []
    res['sell'] = []
    if 'intraday-extra' in db.keys():
      del db['intraday-extra']
    
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    return response



@app.route("/del-ha/<stock>")
def del_stock(stock):
    res = {}
    res['indicator'] = 'Stock removed successfully'
    res['buy'] = []
    res['sell'] = []
    extra = []
    current=[]
    if 'intraday-extra' in db.keys():
      current = list(db['intraday-extra'])
    
    extra.extend(current)
    
    if stock in extra:
      extra.remove(stock)
    db['intraday-extra'] = list(set(extra))
    
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/ha-stocks')
def ha_stocks():
    res = {}
    res['indicator'] = 'HA stocks'
    res['buy'] = []
    res['sell'] = []
    for key in db.keys():
      if '_ha' in key:
        val = dict(db[key])
        val['stock'] = key.replace('_ha', '')
        res['buy'].append(str(val))

    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/atr')
def atr():
    res = {}
    res['indicator'] = 'ATR'
    res['buy'] = []
    res['sell'] = []
    buy_key = 'atr_buy_latest'
    if buy_key in db.keys():
        res['buy'] = list(db[buy_key])
    sell_key = 'atr_sell_latest'
    if sell_key in db.keys():
        res['sell'] = list(db[sell_key])

    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    return response

# @app.route('/plot-intraday/<stock>')
# def plot_intraday(stock):
#     res = {}
#     res['indicator'] = 'Plot - Intraday'
#     res['buy'] = []
#     res['sell'] = []
#     # stock = request.args.get("stock")
#     buy_key = plot_chart_intraday(stock)
#     res['buy'].append(buy_key)

#     response = app.response_class(
#         response=buy_key,
#         status=200,
#         mimetype='application/json'
#     )
#     return response


@app.route('/atr-intraday')
def atr_intraday():
    res = {}
    res['indicator'] = 'ATR - Intraday'
    res['buy'] = []
    res['sell'] = []
    buy_key = 'atr_intraday_buy_latest'
    if buy_key in db.keys():
        res['buy'] = list(db[buy_key])
    sell_key = 'atr_intraday_sell_latest'
    if sell_key in db.keys():
        res['sell'] = list(db[sell_key])

    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    return response


import numpy as np


def add_to_res(data, res):
    total = 0
    trades = 0
    is_new = data['is_new'] if 'is_new' in data.keys() else False
    bold = '*'
    new_entry = ' - new' if is_new else ''
    both_valid = u'\U0001F7E2' if (data['momentum'] > 0 and data['trend'] > 0) or (
            data['momentum'] < 0 and data['trend'] < 0) else u'\U0001F7E1'

    up = u'\u2B06'
    down = u'\u2B07'
    print(str(data))
    # change = data['buy_price'] - data['exit_buy_price'] if 'buy_price' in data.keys() and 'exit_buy_price' in data.keys() else None
    change = None
    change_str = "   " + str(abs(np.around(change, 2))) + "% " + (up if change > 0 else down) if change is not None else ''
    unrealised_buy = 0
    unrealised_lp = 0
    val = bold + data['stock'] + new_entry + bold + '  ' + both_valid + change_str + ' \n| m ' + str(data['momentum']) + '| t ' + str(
        data['trend'])
    if 'last_price' in data.keys():
        val = val + '| lp ' + str(np.around(data['last_price'], 2))
    if 'buy_price' in data.keys():
        val = val + '| bp ' + str(np.around(data['buy_price'], 2))
    if 'sell_price' in data.keys():
        val = val + '| sp ' + str(np.around(data['sell_price'], 2))
    if 'exit_sell_price' in data.keys():
        val = val + '| esp ' + str(np.around(data['exit_sell_price'], 2))
    if 'exit_buy_price' in data.keys():
        val = val + '| ebp ' + str(np.around(data['exit_buy_price'], 2))
    if 'profit' in data.keys():
      total += np.around(data['profit'], 2)
      trades += np.around(data['trades'], 2)
      val = val + '| profit ' + str(np.around(data['profit'], 2))
      val = val + '| trades ' + str(np.around(data['trades'], 2))
    else:
      val = val + '| ungain ' + str(np.around((np.around(data['last_price'], 2)- np.around(data['buy_price'],2))*100/ np.around(data['buy_price'],2), 2))

    val = val + '|'

    # show only new buys as else it may lead to noise
    if is_new:
        if 'action' in data.keys() and data['action'] == 'buy':
            res['buy'].append(val)
        elif 'action' in data.keys() and data['action'] == 'exit_buy':
            res['exit_buy'].append(val)
        elif 'action' in data.keys() and data['action'] == 'exit_sell':
            res['exit_sell'].append(val)
        else:
            res['sell'].append(val)
    return total, trades, unrealised_buy, unrealised_lp
    


@app.route('/ha-intraday-all')
def ha_intraday_all():
    res = {}
    res['indicator'] = 'HA - Intraday - All'
    res['buy'] = []
    res['sell'] = []
    res['exit_buy'] = []
    res['exit_sell'] = []

    if 'ha_intraday_buy_latest' in db.keys():
       res['buy'] = list(db['ha_intraday_buy_latest'])
    if 'ha_intraday_sell_latest' in db.keys():
       res['exit_buy'] = list(db['ha_intraday_sell_latest'])

    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/atr-intraday-all')
def atr_intraday_all():
    res = {}
    res['indicator'] = 'ATR - Intraday - All'
    res['buy'] = []
    res['sell'] = []
    res['exit_buy'] = []
    res['exit_sell'] = []
    all_key = 'atr_intraday_all'
    total_p = 0
    total_trades = 0

    if all_key in db.keys():
        for key in db[all_key].keys():
            data = {}
            data['stock'] = key
            for param in db[all_key][key].keys():
                data[param] = db[all_key][key][param]
            total, trades, u_bp, u_lp = add_to_res(data, res)
            total_p += total
            total_trades += trades
    
    # if total_trades > 0:
    #   res['exit_buy'].append("Avg Profit = " + str(np.around(total_p/total_trades, 2)))
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/chaikin')
def chaikin():
    res = {}
    res['indicator'] = 'Chaikin'
    res['buy'] = []
    res['sell'] = []
    buy_key = 'chaikin_buy_latest'
    if buy_key in db.keys():
        res['buy'] = list(db[buy_key])
    sell_key = 'chaikin_sell_latest'
    if sell_key in db.keys():
        res['sell'] = list(db[sell_key])

    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    return response


def run():
    print("app started")
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()
