import sys
from .Order import Order


class Orderbook_Entry:

    def __init__(self):
        self.qty = 0
        self.orders = []

    def add_order(self, order):
        self.qty = self.qty + order.qty
        self.orders.append(order)


# Orderbook_half is one side of the book: a list of bids or a list of asks, each sorted best-first
class Orderbook_Half:

    def __init__(self, booktype, worst_price):
        # booktype: bids or asks?
        self.booktype = booktype
        # dictionary of orders received, indexed by Trader ID
        self.orders = {}
        # limit order book, dictionary indexed by price, with order info
        self.lob = {}

        # summary stats
        self.__worst_price = worst_price
        self.lob_depth = 0  # how many different prices on lob?

    def get_best_price(self):
        if len(self.lob) > 0:
            lob_anon = self.get_anonymize_lob()
            if self.booktype == Order.BID:
                return lob_anon[-1][0]   # MUST CHANGE
            elif self.booktype == Order.ASK:
                return lob_anon[0][0]   # MUST CHANGE
            else:
                sys.exit("Booktype not set")
        else:
            return None

    def get_best_tid(self):
        if len(self.lob) > 0:
            return self.lob[self.get_best_price()].orders[0].tid
        else:
            return None

    def get_worst_price(self):
        if len(self.lob) > 0:
            lob_anon = self.get_anonymize_lob()
            if self.booktype == Order.BID:
                return lob_anon[0][0]   # MUST CHANGE
            elif self.booktype == Order.ASK:
                return lob_anon[-1][0]   # MUST CHANGE
            else:
                sys.exit("Booktype not set")
        else:
            return self.__worst_price

    def get_qty(self):
        qty = 0
        for qid in self.orders:
            order = self.orders.get(qid)
            qty += order.qty
        return qty

    # anonymize a lob, strip out order details, format as a sorted list
    # NB for asks, the sorting should be reversed
    def get_anonymize_lob(self):
        lob_anon = []
        for price in sorted(self.lob):
            lob_anon.append([price, self.lob[price].qty])

        # if self.booktype == Order.ASK:
        #     lob_anon.reverse()

        return lob_anon

    # take a list of orders and build a limit-order-book (lob) from it
    # NB the exchange needs to know arrival times and trader-id associated with each order
    # returns lob as a dictionary (i.e., unsorted)
    # also builds anonymized version (just price/quantity, sorted, as a list) for publishing to traders
    def build_lob(self):
        self.lob = {}
        for qid in self.orders:
            order = self.orders.get(qid)
            price = order.price

            if price in self.lob:
                entry = self.lob[price]
            else:
                entry = Orderbook_Entry()

            entry.add_order(order)
            self.lob[price] = entry

        print(self.lob)

    # add order to the dictionary holding the list of orders
    # either overwrites old order from this trader
    # or dynamically creates new entry in the dictionary
    # so, max of one order per trader per list
    # checks whether length or order list has changed, to distinguish addition/overwrite
    def book_add(self, order):
        n_orders = self.get_qty()
        self.orders[order.qid] = order
        self.build_lob()

        if n_orders != self.get_qty():
            return 'Addition'
        else:
            return 'Overwrite'

    # delete order from the dictionary holding the orders
    # assumes max of one order per trader per list
    # checks that the Quote ID does actually exist in the dict before deletion
    def book_del(self, order):
        # print('book_del %s',self.orders)
        if self.orders.get(order.qid) is not None:
            del (self.orders[order.qid])
            self.build_lob()
        # print('book_del %s', self.orders)

    # delete order: when the best bid/ask has been hit, delete it from the book
    # the TraderID of the deleted order is return-value, as counterparty to the trade
    def delete_best(self):
        best_price_orders = self.lob[self.best_price]
        best_price_qty = best_price_orders[0]
        best_price_counterparty = best_price_orders[1][0][2]

        if best_price_qty == 1:
            # here the order deletes the best price
            del (self.lob[self.best_price])
            del (self.orders[best_price_counterparty])
            if self.get_qty() > 0:
                if self.booktype == Order.BID:
                    self.best_price = max(self.lob.keys())
                else:
                    self.best_price = min(self.lob.keys())
                self.lob_depth = len(self.lob.keys())
            else:
                self.best_price = self.get_worst_price()
                self.lob_depth = 0
        else:
            # best_bid_qty>1 so the order decrements the quantity of the best bid
            # update the lob with the decremented order data
            self.lob[self.best_price] = [best_price_qty - 1, best_price_orders[1][1:]]

            # update the bid list: counterparty's bid has been deleted
            del (self.orders[best_price_counterparty])
        self.build_lob()
        return best_price_counterparty


# Orderbook for a single instrument: list of bids and list of asks
class Orderbook():

    def __init__(self):
        bse_sys_min_price = 1  # minimum price in the system, in cents/pennies
        bse_sys_max_price = 1000  # maximum price in the system, in cents/pennies

        self.bids = Orderbook_Half(Order.BID, bse_sys_min_price)
        self.asks = Orderbook_Half(Order.ASK, bse_sys_max_price)
        self.tape = []
        self.quote_id = 10  # unique ID code for each quote accepted onto the book
