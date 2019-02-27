import sys, time
from .Orderbook import Orderbook
from .Order import Order


# Exchange's internal orderbook
class Exchange(Orderbook):

    def __init__(self, debug):
        super().__init__()
        self.verbose = debug

    # add a quote/order to the exchange and update all internal records; return unique i.d.
    def add_order(self, order):
        order.qid = self.quote_id
        self.quote_id = order.qid + 1
        # if verbose : print('QUID: order.quid=%d self.quote.id=%d' % (order.qid, self.quote_id))

        if order.otype == Order.BID:
            response = self.bids.book_add(order)
        elif order.otype == Order.ASK:
            response = self.asks.book_add(order)
        else:
            sys.exit('add_order() given neither Bid nor Ask')

        return response

    # receive an order and either add it to the relevant LOB (ie treat as limit order)
    # or if it crosses the best counterparty offer, execute it (treat as a market order)
    def process_order(self, order):
        counter_party, price = None, None

        response = self.add_order(order)  # add it to the order lists -- overwriting any previous order

        if self.verbose:
            print('QUID: order.quid=%d' % order.qid)
            print('RESPONSE: %s' % response)

        best_ask = self.asks.get_best_price()
        best_ask_tid = self.asks.get_best_tid()
        best_bid = self.bids.get_best_price()
        best_bid_tid = self.bids.get_best_tid()

        if order.otype == Order.BID:
            if self.asks.get_qty() > 0 and best_bid >= best_ask:
                # bid lifts the best ask
                if self.verbose:
                    print("Bid $%s lifts best ask" % order.price)

                counter_party = best_ask_tid
                price = best_ask  # bid crossed ask, so use ask price

                if self.verbose:
                    print('counterparty, price', counter_party, price)

                # delete the ask just crossed
                self.asks.delete_best()
                # delete the bid that was the latest order
                self.bids.delete_best()
        elif order.otype == Order.ASK:
            if self.bids.get_qty() > 0 and best_ask <= best_bid:
                # ask hits the best bid
                if self.verbose:
                    print("Ask $%s hits best bid" % order.price)

                # remove the best bid
                counter_party = best_bid_tid
                price = best_bid  # ask crossed bid, so use bid price

                if self.verbose:
                    print('counterparty, price', counter_party, price)

                # delete the bid just crossed, from the exchange's records
                self.bids.delete_best()
                # delete the ask that was the latest order, from the exchange's records
                self.asks.delete_best()
        else:
            # we should never get here
            sys.exit('process_order() given neither Bid nor Ask')

        # NB at this point we have deleted the order from the exchange's records
        # but the two traders concerned still have to be notified
        if self.verbose:
            print('counterparty %s' % counter_party)

        if counter_party is not None and price is not None:
            # process the trade

            transaction_time = time.time()
            if self.verbose:
                print('>>>>>>>>>>>>>>>>>TRADE t=%5.2f $%d %s %s' % (transaction_time, price, counter_party, order.tid))

            transaction_record = {
                'type': 'Trade',
                'time': transaction_time,
                'price': price,
                'party1': counter_party,
                'party2': order.tid,
                'qty': order.qty
            }
            self.tape.append(transaction_record)
            return transaction_record
        else:
            return "No transaction occurred"

    # delete a trader's quot/order from the exchange, update all internal records
    def del_order(self, order):
        if order.otype == Order.BID:
            self.bids.book_del(order)
            if self.bids.get_qty() > 0:
                best_price = self.bids.lob_anon[-1][0]
                self.bids.best_price = best_price
                self.bids.best_tid = self.bids.lob[best_price][1][0][2]
            else:  # this side of book is empty
                self.bids.best_price = None
                self.bids.best_tid = None
            cancel_record = {'type': 'Cancel', 'time': time.time(), 'order': order}
            self.tape.append(cancel_record)

        elif order.otype == Order.ASK:
            self.asks.book_del(order)
            if self.asks.get_qty() > 0:
                best_price = self.asks.lob_anon[0][0]
                self.asks.best_price = best_price
                self.asks.best_tid = self.asks.lob[best_price][1][0][2]
            else:  # this side of book is empty
                self.asks.best_price = None
                self.asks.best_tid = None
            cancel_record = {'type': 'Cancel', 'time': time.time(), 'order': order}
            self.tape.append(cancel_record)
        else:
            # neither bid nor ask?
            sys.exit('bad order type in del_quote()')

    def tape_dump(self, fname, fmode, tmode):
        dumpfile = open(fname, fmode)
        for tapeitem in self.tape:
            if tapeitem['type'] == 'Trade':
                dumpfile.write('%s, %s\n' % (tapeitem['time'], tapeitem['price']))
        dumpfile.close()
        if tmode == 'wipe':
            self.tape = []

    # this returns the LOB data "published" by the exchange,
    # i.e., what is accessible to the traders
    def publish_lob(self):
        public_data = {
            'time': time.time(),
            'bids': {
                'best': self.bids.get_best_price(),
                'worst': self.bids.get_worst_price(),
                'qty': self.bids.get_qty(),
                'lob': self.bids.get_anonymize_lob()
            },
            'asks': {
                'best': self.asks.get_best_price(),
                'worst': self.asks.get_worst_price(),
                'qty': self.asks.get_qty(),
                'lob': self.asks.get_anonymize_lob()
            },
            'QID': self.quote_id, 'tape': self.tape
        }

        if self.verbose:
            print('publish_lob: t=%d' % public_data['time'])
            print('BID_lob=%s' % public_data['bids']['lob'])
            # print('best=%s; worst=%s; n=%s ' % (self.bids.best_price, self.bids.worst_price, self.bids.n_orders))
            print('ASK_lob=%s' % public_data['asks']['lob'])
            # print('qid=%d' % self.quote_id)

        return public_data
