from pyrogram import Client, filters
import re
import config
import ccxt
from pybit.unified_trading import HTTP

channel_id = "-1002164329867"  # твой ID канала

app = Client("my_bot")

exchange = ccxt.bybit({
    'apiKey': config.api_key,
    'secret': config.api_secret,
    'options': {'defaultType': 'future'}  # Используем фьючерсный рынок
})

client = HTTP(
    api_key=config.api_key,
    api_secret=config.api_secret
)

def get_decimals(symbol):
    markets = exchange.load_markets()
    return markets[symbol]['precision']['price']

def get_order_book(symbol):
    orderbook = exchange.fetchOrderBook(symbol=symbol, limit=10)
    bid = orderbook['bids'][0][0] if orderbook['bids'] else None
    ask = orderbook['asks'][0][0] if orderbook['asks'] else None
    return bid, ask

def get_balance():
    balance = exchange.fetch_balance()
    return balance['USDT']['free']  # доступный баланс USDT

def place_order(action, symbol, price, qty, take_profit, stop_loss):
    side = "Sell" if action == "short" else "Buy"
    opposite_side = "Buy" if action == "short" else "Sell"

    # Ставим начальный ордер
    client.place_active_order(
        side=side,
        symbol=symbol,
        order_type="Limit",
        price=price,
        qty=qty,
        time_in_force="GoodTillCancel",
        reduce_only=False,
        close_on_trigger=False
    )
    print(f"Поставили {action} ордер на {symbol} по цене {price}")

    # Ставим тейк-профит
    client.place_active_order(
        side=opposite_side,
        symbol=symbol,
        order_type="Limit",
        price=take_profit,
        qty=qty,
        time_in_force="GoodTillCancel",
        reduce_only=True,
        close_on_trigger=True
    )
    print(f"Поставили тейк-профит ордер на {symbol} по цене {take_profit}")

    # Ставим стоп-лосс
    client.place_active_order(
        side=opposite_side,
        symbol=symbol,
        order_type="Stop",
        stop_px=stop_loss,
        qty=qty,
        base_price=price,
        time_in_force="GoodTillCancel",
        reduce_only=True,
        close_on_trigger=True
    )
    print(f"Поставили стоп-лосс ордер на {symbol} по цене {stop_loss}")

def handle_trade(coin, action, price, take_profit, stop_loss):
    symbol = f"{coin}/USDT"
    balance = get_balance()
    
    trade_amount = balance * config.trade_percent
    max_trade_amount = balance * config.max_percent

    bid, ask = get_order_book(symbol)
    current_price = ask if action == "short" else bid

    if current_price:
        decimals = get_decimals(symbol)
        price = round(price, decimals)
        take_profit = round(take_profit, decimals)
        stop_loss = round(stop_loss, decimals)

        qty = trade_amount / current_price
        if qty * current_price > max_trade_amount:
            qty = max_trade_amount / current_price
        qty = round(qty, 4)  # Округляем количество монет до 4 знаков после запятой

        place_order(action, symbol, price, qty, take_profit, stop_loss)
    else:
        print(f"Не удалось получить текущую цену для {symbol}")

@app.on_message(filters.chat(channel_id))
def new_message(client, message):
    text = message.text
    if text:
        match = re.search(r'#bybit #(\w+)\s*🐠 (Long|Short)\s*🐠 Price: ([\d.]+)\s*🐠 Take: ([\d.]+)\s*\(\+[\d.]+%\)\s*🐠 Stop: ([\d.]+)\s*\(-[\d.]+%\)', text)
        if match:
            coin = match.group(1)
            action = match.group(2).lower()  # переводим в нижний регистр 'long' или 'short'
            price = float(match.group(3))
            take_profit = float(match.group(4))
            stop_loss = float(match.group(5))
            
            # Вызываем функцию, которая обрабатывает торговлю
            handle_trade(coin, action, price, take_profit, stop_loss)
            print(f"Parsed Message: {coin}, {action}, {price}, {take_profit}, {stop_loss}")

app.run()
