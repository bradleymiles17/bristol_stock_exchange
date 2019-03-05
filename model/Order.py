from .OrderBookRequest import OrderBookRequest


# an Order/quote has a trader id, a type (buy/sell) price, quantity, and unique i.d.
class Order:

    def __init__(self, timestamp, qid, tid, symbol, is_buy, price, qty, request: OrderBookRequest):
        self.timestamp = timestamp  # timestamp
        self.qid = qid  # quote i.d. (unique to each quote)
        self.tid = tid  # trader i.d.
        self.symbol = symbol
        self.is_buy = is_buy  # order type [BUY || ASK]
        self.price = price  # price
        self.qty = qty  # quantity
        self.request = request

    def __str__(self):
        return '[QID:%d TID:%s T=%5.2f %s P=%.2f Q=%s]' % \
               (self.qid, self.tid, self.timestamp, "BID" if self.is_buy else "ASK", self.price, self.qty)
