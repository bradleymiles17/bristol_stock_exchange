import time


# an Order/quote has a trader id, a type (buy/sell) price, quantity, and unique i.d.
class Order:
    BID = "BID"
    ASK = "ASK"

    def __init__(self, qid, tid, otype, price, qty):
        self.qid = qid  # quote i.d. (unique to each quote)
        self.time = time.time()  # timestamp
        self.tid = tid  # trader i.d.
        self.otype = otype  # order type
        self.price = price  # price
        self.qty = qty  # quantity

    def __str__(self):
        return '[QID:%d TID:%s T=%5.2f %s P=%03d Q=%s]' % \
               (self.qid, self.tid, self.time, self.otype, self.price, self.qty)
