from flask import request
from flask_api import FlaskAPI

from model.Exchange import Exchange
from model.Order import Order


# EB looks for an 'application' callable by default.

exchange = Exchange()

application = FlaskAPI(__name__)


@application.route("/")
def index():
    return exchange.publish_lob(True)


@application.route("/order", methods=["GET"])
def orders_index(self):
    return True


@application.route("/order", methods=["POST"])
def create_bid(self):
    lob = self.exchange.publish_lob(True)

    body = request.get_json()

    order = Order(
        body["trader_id"],
        body["otype"],
        body["price"],
        body["qty"],
        lob['QID']
    )
    [order.qid, response] = self.exchange.add_order(order, True)
    return response


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.run(debug=True)
