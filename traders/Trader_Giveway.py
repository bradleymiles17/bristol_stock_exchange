from model.Order import Order
from .Trader import Trader

# Trader subclass Giveaway
# even dumber than a ZI-U: just give the deal away
# (but never makes a loss)
class Trader_Giveaway(Trader):

    def getorder(self, time, countdown, lob):
        if len(self.orders) < 1:
            order = None
        else:
            quoteprice = self.orders[0].price
            order = Order(time, self.tid, self.orders[0].otype, quoteprice, self.orders[0].qty)
            self.lastquote = order
        return order
