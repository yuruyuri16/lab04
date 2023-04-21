from flask import Flask
from flask import request, jsonify
import urllib.request
import json
import redis

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


@app.route('/summary', methods=['POST'])
def total_orders():
    data = request.get_json()
    if not data:
        return jsonify(error="request body cannot be empty"), 400
    total = 0
    for order in data:
        country = order['country']
        amount = int(order['amount'])
        tax = get_tax_from_api(country)
        total += amount * tax
    return jsonify(total_due=total), 200


def get_tax_from_api(country) -> int:
    tax = r.get(country)
    if tax is not None:
        return int(tax)
    url = "http://127.0.0.1:5000/tax?country={}".format(country)
    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)
    tax = int(dict["Tax"])
    r.set(country, tax)
    return tax


if __name__ == "__main__":
    app.run(debug=True, port=3000)


# TODO: Handle errors properly.
