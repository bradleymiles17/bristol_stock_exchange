from .Order import Order


# Orderbook_half is one side of the book: a list of bids or a list of asks, each sorted best-first
class Orderbook_Half:

    def __init__(self, is_buy, worst_price):
        # booktype: bids or asks?
        # dictionary of orders received, indexed by Quote ID
        self.orders = {}
        # limit order book, dictionary indexed by price, with order info
        self.lob = {}

        # summary stats
        self.is_buy = is_buy
        self.__worst_price = worst_price
        self.lob_depth = 0  # how many different prices on lob?

    def get_order_by_id(self, qid: int) -> Order:
        return self.orders.get(qid)

    def get_orders(self):
        orders = []
        for id in self.orders:
            orders.append(str(self.orders[id]))

        return orders

    def add_order(self, order: Order):
        self.orders[order.qid] = order
        self.build_lob()
        return True

    def delete_order_by_id(self, qid: int) -> bool:
        if self.orders.get(qid) is not None:
            del self.orders[qid]
            self.build_lob()
            return True
        return False

    def delete_order(self, order: Order) -> bool:
        if self.orders.get(order.qid) is not None:
            del self.orders[order.qid]
            self.build_lob()
            return True
        return False

    def get_best_price(self):
        if len(self.lob) > 0:
            prices = sorted(self.lob, reverse=True) if self.is_buy else sorted(self.lob)
            return prices[0]
        else:
            return None

    def get_worst_price(self):
        if len(self.lob) > 0:
            prices = sorted(self.lob) if self.is_buy else sorted(self.lob, reverse=True)
            return prices[0]
        else:
            return None

    def get_best_order(self):
        if len(self.lob) > 0:
            return self.lob[self.get_best_price()][0]
        else:
            return None

    def get_order_n(self):
        return len(self.orders)

    def get_qty(self):
        qty = 0
        for qid in self.orders:
            order = self.orders.get(qid)
            qty += order.qty
        return qty

    def is_empty(self):
        return len(self.orders) == 0

    # anonymize a lob, strip out order details, format as a sorted list
    # NB for asks, the sorting should be reversed
    def get_anonymize_lob(self):
        lob_anon = []
        for price in sorted(self.lob, reverse=True) if self.is_buy else sorted(self.lob):

            qty = 0
            for order in self.lob[price]:
                qty += order.qty

            lob_anon.append([price, qty])

        return lob_anon

    # take a list of orders and build a limit-order-book (lob) from it
    # NB the exchange needs to know arrival times and trader-id associated with each order
    # returns lob as a dictionary (i.e., unsorted)
    # also builds anonymized version (just price/quantity, sorted, as a list) for publishing to traders
    def build_lob(self):
        self.lob = {}
        for qid in self.orders:
            order = self.orders.get(qid)

            if order.price in self.lob:
                self.lob[order.price].append(order)
            else:
                self.lob[order.price] = [order]


# Orderbook for a single instrument: list of bids and list of asks
class Orderbook:

    def __init__(self, symbol):
        bse_sys_min_price = 1  # minimum price in the system, in cents/pennies
        bse_sys_max_price = 1000  # maximum price in the system, in cents/pennies

        self.symbol = symbol
        self.bids = Orderbook_Half(True, bse_sys_min_price)
        self.asks = Orderbook_Half(False, bse_sys_max_price)
        self.tape = []
        self.quote_id = 0  # unique ID code for each quote accepted onto the book

    def get_next_quote_id(self):
        id = self.quote_id
        self.quote_id = self.quote_id + 1
        return id

    def get_order_by_id(self, qid: int):
        bid = self.bids.get_order_by_id(qid)
        ask = self.asks.get_order_by_id(qid)

        if bid is not None:
            return bid
        elif ask is not None:
            return ask
        else:
            return None
