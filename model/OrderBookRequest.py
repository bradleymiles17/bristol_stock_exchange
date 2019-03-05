from typing import Optional
import time


class OrderBookRequest:
    timestamp = None


class NewOrder(OrderBookRequest):
    def __init__(self, trader_id, symbol, qty, is_buy, price: Optional[float]):
        self.timestamp = time.time()
        self.trader_id = trader_id
        self.symbol = symbol
        self.qty = qty
        self.is_buy = is_buy
        self.price = price

    def __str__(self):
        return '[TID:%s %s %s P=%.2f Q=%s]' % \
               (self.trader_id, self.symbol, "BID" if self.is_buy else "ASK", self.price, self.qty)


class Cancel(OrderBookRequest):
    def __init__(self, order: NewOrder):
        self.timestamp = time.time()
        self.order = order


class Amend(OrderBookRequest):
    def __init__(self, order: NewOrder, new_price: Optional[float], new_qty: Optional[int]):
        self.timestamp = time.time()
        self.order = order
        self.new_price = new_price
        self.new_qty = new_qty
