from model.Orderbook import Orderbook
from model.Order import Order
from model.OrderBookRequest import *
from model.OrderBookResponse import *


# Exchange's internal orderbook
class Exchange:
    lob = Orderbook("BAM")

    def transaction_observer(self, response: OrderBookResponse):
        print(response)

    # def marketdata_observer(self respnse: ):

    volume = 0

    def __init__(self, debug):
        super().__init__()
        self.verbose = debug

    # new order
    # cancel
    # amend
    def process_order_book_request(self, request):

        def is_invalid_request(request):
            return False

        if isinstance(request, NewOrder):
            if is_invalid_request(request):
                self.transaction_observer(Rejected(time.time(), "Invalid Order", request))
            else:
                self.transaction_observer(Acknowledged(time.time(), request))
                order_book_order = Order(
                    self.lob.get_next_quote_id(),
                    request.timestamp,
                    request.trader_id,
                    request.symbol,
                    request.is_buy,
                    request.qty,
                    request.price,
                    request
                )
                self.process_new_order(order_book_order)
        elif isinstance(request, Cancel):
            print("Cancel Request")

            removed_bid = self.lob.bids.book_remove_by_id(request.qid)
            removed_ask = self.lob.bids.book_remove_by_id(request.qid)

            if removed_ask or removed_bid:
                self.transaction_observer(Acknowledged(time.time(), request))
            else:
                self.transaction_observer(Rejected(time.time(), "Order not found", request))
        elif isinstance(request, Amend):
            print ("Amend Request")

    def process_new_order(self, order_book_order: Order):

        def is_limit_order_executable(order, opposite_order):
            if order.is_buy:
                return order.price >= opposite_order.price
            else:
                return order.price <= opposite_order.price

        current_time = time.time()

        order_book = self.lob.bids if order_book_order.is_buy else self.lob.asks
        opposite_book = self.lob.asks if order_book_order.is_buy else self.lob.bids

        # LIMIT ORDER
        if order_book_order.price is not None:
            if opposite_book.is_empty() or (not is_limit_order_executable(order_book_order, opposite_book.get_best_order())):
                order_book.book_add(order_book_order)
                # updateBBO()
            else:
                self.match_order(order_book_order, opposite_book)

        # MARKER ORDER
        else:
            if opposite_book.is_empty():
                self.transaction_observer(Rejected(current_time, "No opposing orders in queue", order_book_order.request))
            else:
                self.match_order(order_book_order, opposite_book)

    def match_order(self, order: Order, opposite_book):
        opposite_order = opposite_book.get_best_order()

        currentTime = time.time()

        if order.qty < opposite_order.qty:
            opposite_order.qty = opposite_order.qty - order.qty
            self.volume += order.qty

            self.transaction_observer(Filled(currentTime, order.price, order.qty, [order.request, opposite_order.request]))
            # self.marketdataObserver(LastSalePrice(currentTime, order.symbol, order.price, order.qty, volume))

        elif order.qty > opposite_order.qty:
            opposite_book.book_remove(opposite_order)

            order.qty = order.qty - opposite_order.qty

            self.volume += order.qty

            self.transaction_observer(Filled(currentTime, order.price, opposite_order.qty, [order.request, opposite_order.request]))
            # self.marketdataObserver(LastSalePrice(currentTime, order.symbol, order.price, order.qty, volume))

            self.process_new_order(order)

        else:
            opposite_book.book_remove(opposite_order)

            self.volume += order.qty

            self.transaction_observer(
                Filled(currentTime, order.price, order.qty, [order.request, opposite_order.request])
            )
            # self.marketdataObserver(LastSalePrice(currentTime, order.symbol, order.price, order.qty, self.volume))

    def publish_orders(self):
        public_data = {
            'bids': self.lob.bids.get_orders(),
            'asks': self.lob.asks.get_orders()
        }

        return public_data

    # this returns the LOB data "published" by the exchange,
    # i.e., what is accessible to the traders
    def publish_lob(self):
        public_data = {
            'time': time.time(),
            'bids': {
                'best': self.lob.bids.get_best_price(),
                'worst': self.lob.bids.get_worst_price(),
                'qty': self.lob.bids.get_qty(),
                'lob': self.lob.bids.get_anonymize_lob()
            },
            'asks': {
                'best': self.lob.asks.get_best_price(),
                'worst': self.lob.asks.get_worst_price(),
                'qty': self.lob.asks.get_qty(),
                'lob': self.lob.asks.get_anonymize_lob()
            },
            'QID': self.lob.quote_id
            # 'tape': self.transactionObserver
        }

        return public_data
