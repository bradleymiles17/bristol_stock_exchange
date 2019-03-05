from flask import request
from flask_api import FlaskAPI

from exchange.Exchange import Exchange
from model.OrderBookRequest import NewOrder


# EB looks for an 'application' callable by default.

exchange = Exchange(True)

application = FlaskAPI(__name__)


@application.route("/api/orders")
def publish_orders():
    return exchange.publish_orders()


@application.route("/api/anon_lob")
def publish_lob():
    return exchange.publish_lob()


@application.route("/api/order", methods=["POST"])
def create_order():
    body = request.get_json()

    order_request = NewOrder(body["trader_id"], body["symbol"], body["qty"], body["is_buy"], body["price"])
    exchange.process_order_book_request(order_request)

    return "Success"


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.run(debug=True)
