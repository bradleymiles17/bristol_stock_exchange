from flask import request
from flask_api import FlaskAPI

from exchange.Exchange import Exchange
from exchange.model.OrderBookRequest import NewOrder, Cancel

# EB looks for an 'application' callable by default.

application = FlaskAPI(__name__)
application.config["DEBUG"] = True
application.config['SECRET_KEY'] = 'secret!'

exchange = Exchange(application.config["DEBUG"])


@application.route("/")
def index():
    return exchange.publish_lob()


@application.route("/api/lob")
def publish_lob():
    return exchange.publish_lob()


@application.route("/api/orders", methods=["GET"])
def view_orders():
    return exchange.publish_orders()


@application.route("/api/orders/<int:order_id>", methods=["GET"])
def get_order(order_id: int):
    order = exchange.lob.get_order_by_id(order_id)

    if order is not None:
        return str(order)
    else:
        return "Order id does not exist"


@application.route("/api/orders/<int:order_id>/cancel", methods=["POST"])
def cancel_order(order_id: int):
    cancel_request = Cancel(order_id)
    exchange.process_order_book_request(cancel_request)

    return "Cancelled"


@application.route("/api/orders", methods=["POST"])
def place_order():
    body = request.get_json()

    order_request = NewOrder(body["trader_id"], body["symbol"], body["is_buy"], body["qty"], body["price"])
    exchange.process_order_book_request(order_request)

    return "Acknowledged"


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.run()
