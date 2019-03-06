from typing import List
from model.OrderBookRequest import OrderBookRequest, NewOrder


class OrderBookResponse:
    timestamp = None


class Filled(OrderBookResponse):
    def __init__(self, timestamp, price, qty, requests: List[NewOrder]):
        self.timestamp = timestamp
        self.price = price
        self.qty = qty
        self.requests = requests

    def __str__(self):
        return 'FILLED (%5.2f): [P=%.2f Q=%s]' % \
               (self.timestamp, self.price, self.qty)


class Acknowledged(OrderBookResponse):
    def __init__(self, timestamp, request: OrderBookRequest):
        self.timestamp = timestamp
        self.request = request

    def __str__(self):
        return 'ACKNOWLEDGED (T=%5.2f): [%s]' % \
               (self.timestamp, self.request)


class Rejected(OrderBookResponse):
    def __init__(self, timestamp, error, request: OrderBookRequest):
        self.timestamp = timestamp
        self.error = error
        self.request = request

    def __str__(self):
        return 'REJECTED (T=%5.2f) %s: [%s]' % \
               (self.timestamp, self.error, self.request)


class Canceled(OrderBookResponse):
    def __init__(self, timestamp, reason, request: OrderBookRequest):
        self.timestamp = timestamp
        self.reason = reason
        self.request = request

    def __str__(self):
        return 'CANCELED (T=%5.2f) %s: [%s]' % \
               (self.timestamp, self.reason, self.request)

