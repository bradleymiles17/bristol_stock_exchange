from .OrderBookRequest import OrderBookRequest


# an Order/quote has a trader id, a type (buy/sell) price, quantity, and unique i.d.
class Order:

    def __init__(self, qid, timestamp, tid, symbol, is_buy, qty, price, request: OrderBookRequest):
        self.qid = qid  # quote i.d. (unique to each quote)
        self.timestamp = timestamp  # timestamp
        self.tid = tid  # trader i.d.
        self.symbol = symbol
        self.is_buy = is_buy  # order type [BUY || ASK]
        self.qty = qty  # quantity
        self.price = price  # price
        self.request = request

    def __str__(self):
        return '[QID:%d T=%5.2f TID:%s %s P=%.2f Q=%s]' % \
               (self.qid, self.timestamp, self.tid, "BID" if self.is_buy else "ASK", self.price, self.qty)
