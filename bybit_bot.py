import time, ccxt, config
from pybit import HTTP

exchange = ccxt.bybit({'apiKey': config.api_key,'secret': config.api_secret})
client = HTTP(api_key=config.api_key,api_secret=config.api_secret)
symbol = config.symbol


def getOrderBook():
    global ask
    global bid
    orderbook = exchange.fetchOrderBook(symbol=symbol,limit=10)
    bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
    ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None

def get_position():
    positions = client.my_position(symbol=symbol)
    for position in positions['result']:
        if position['side'] == 'Sell':
            global sell_position_size
            global sell_position_prce
            sell_position_size = position['size']
            sell_position_prce = position['entry_price'] 

def get_buy_order():
    orders = client.get_active_order(symbol=symbol, limit=21)

    for order in orders['result']['data']:

        global tp_order
        global buy_order_size
        global buy_order_id
        tp_order = order['order_status'] != 'Cancelled' and order['order_status'] != 'Filled' and order['order_status'] == 'New' and order['side'] == "Buy" and order['reduce_only'] == True
        buy_order_size = order['qty']  
        buy_order_id = order['order_id']

def get_sell_order():
    orders = client.get_active_order(symbol=symbol, limit=21)

    for order in orders['result']['data']:
        global sell_order
        global sell_order_id
        global sell_order_size
        sell_order = order['order_status'] != 'Cancelled' and order['order_status'] != 'Filled' and order['order_status'] == 'New' and order['side'] == "Sell" and order['reduce_only'] == False
        sell_order_id = order['order_id']
        sell_order_size = order['qty']

def cancel_sell_orders():
    try:
        orders = client.get_active_order(symbol=symbol)
        for order in orders['result']['data']:
            if order['order_status'] != 'Filled' and order['side'] == 'Sell' and order['order_status'] != 'Cancelled':
                client.cancel_active_order(symbol=symbol, order_id=order['order_id'])
            else:
                pass
    except TypeError:
        pass 

def cancel_buy_orders():
    try:
        orders = client.get_active_order(symbol=symbol)
        for order in orders['result']['data']:
            if order['order_status'] != 'Filled' and order['side'] == 'Buy' and order['order_status'] != 'Cancelled':
                client.cancel_active_order(symbol=symbol, order_id=order['order_id'])
            else:
                pass
    except TypeError:
        pass