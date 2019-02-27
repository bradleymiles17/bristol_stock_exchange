from flask import request
from flask_api import FlaskAPI

from model.Exchange import Exchange
from model.Order import Order


# EB looks for an 'application' callable by default.

exchange = Exchange(True)

application = FlaskAPI(__name__)


@application.route("/api/lob")
def index():
    return exchange.publish_lob()


@application.route("/api/order/<uuid>", methods=["GET"])
def get_order(uuid):
    return uuid


@application.route("/api/order", methods=["POST"])
def create_order():
    lob = exchange.publish_lob()

    body = request.get_json()

    order = Order(lob['QID'], body["trader_id"], body["otype"], body["price"], body["qty"])
    transaction_record = exchange.process_order(order)
    return transaction_record


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.run(debug=True)
