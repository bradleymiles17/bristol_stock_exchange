from exchange.model.Orderbook import Orderbook
from exchange.model.Order import Order
from exchange.model.OrderBookRequest import *
from exchange.model.OrderBookResponse import *
from exchange.model.MarketDataEvent import *


# Exchange's internal orderbook
class Exchange:
    lob = Orderbook("BAM")

    # REFACTOR INTO UDP BROADCAST
    def transaction_observer(self, response: OrderBookResponse):
        print(response)

    def marketdata_observer(self, market_data: MarketDataEvent):
        print(market_data)

    volume = 0

    def __init__(self, debug):
        super().__init__()
        self.verbose = debug

    def process_order_book_request(self, request: OrderBookRequest):

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
                self.__process_new_order(order_book_order)
        elif isinstance(request, Cancel):
            print("Cancel Request")

            removed_bid = self.lob.bids.delete_order_by_id(request.qid)
            removed_ask = self.lob.bids.delete_order_by_id(request.qid)

            if removed_ask or removed_bid:
                self.transaction_observer(Acknowledged(time.time(), request))
                self.__update_BBO()
            else:
                self.transaction_observer(Rejected(time.time(), "Order not found", request))
        elif isinstance(request, Amend):
            print ("Amend Request")

    def __process_new_order(self, order_book_order: Order):

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
                order_book.add_order(order_book_order)
                self.__update_BBO()
            else:
                self.__match_order(order_book_order, opposite_book)

        # MARKER ORDER
        else:
            if opposite_book.is_empty():
                self.transaction_observer(Rejected(current_time, "No opposing orders in queue", order_book_order.request))
            else:
                self.__match_order(order_book_order, opposite_book)

    def __match_order(self, order: Order, opposite_book):
        opposite_order = opposite_book.get_best_order()

        currentTime = time.time()

        if order.qty < opposite_order.qty:
            opposite_order.qty = opposite_order.qty - order.qty
            self.volume += order.qty

            self.transaction_observer(Filled(currentTime, order.price, order.qty, [order.request, opposite_order.request]))
            self.marketdata_observer(LastSalePrice(currentTime, order.symbol, order.price, order.qty, self.volume))
            self.__update_BBO()

        elif order.qty > opposite_order.qty:
            opposite_book.delete_order(opposite_order)

            order.qty = order.qty - opposite_order.qty

            self.volume += opposite_order.qty

            self.transaction_observer(Filled(currentTime, opposite_order.price, opposite_order.qty, [order.request, opposite_order.request]))
            self.marketdata_observer(LastSalePrice(currentTime, order.symbol, opposite_order.price, opposite_order.qty, self.volume))
            self.__update_BBO()
            self.__process_new_order(order)

        else:
            opposite_book.delete_order(opposite_order)

            self.volume += order.qty

            self.transaction_observer(
                Filled(currentTime, order.price, order.qty, [order.request, opposite_order.request])
            )
            self.marketdata_observer(LastSalePrice(currentTime, order.symbol, order.price, order.qty, self.volume))
            self.__update_BBO()

    def __update_BBO(self):
        # self.marketdata_observer(BBOChange(time.time(), this.symbol, bidPrice, bidQty, offerPrice, offerQty))
        return True

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
                'order_n': self.lob.bids.get_order_n(),
                'qty': self.lob.bids.get_qty(),
                'lob': self.lob.bids.get_anonymize_lob()
            },
            'asks': {
                'best': self.lob.asks.get_best_price(),
                'worst': self.lob.asks.get_worst_price(),
                'order_n': self.lob.asks.get_order_n(),
                'qty': self.lob.asks.get_qty(),
                'lob': self.lob.asks.get_anonymize_lob()
            },
            'QID': self.lob.quote_id
            # 'tape': self.transactionObserver
        }

        return public_data
