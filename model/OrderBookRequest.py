from typing import Optional
import time


class OrderBookRequest:
    timestamp = None


class NewOrder(OrderBookRequest):
    def __init__(self, trader_id, symbol, is_buy, qty, price: Optional[float]):
        self.timestamp = time.time()
        self.trader_id = trader_id
        self.symbol = symbol
        self.is_buy = is_buy
        self.qty = qty
        self.price = price

    def __str__(self):
        return '[TID:%s %s %s Q=%s P=%.2f]' % \
               (self.trader_id, self.symbol, "BID" if self.is_buy else "ASK", self.qty, self.price)


class Cancel(OrderBookRequest):
    def __init__(self, qid: int):
        self.timestamp = time.time()
        self.qid = qid


class Amend(OrderBookRequest):
    def __init__(self, qid, new_price: Optional[float], new_qty: Optional[int]):
        self.timestamp = time.time()
        self.qid = qid
        self.new_price = new_price
        self.new_qty = new_qty
