from flask import Flask
from flask import request, jsonify
from flask_mongoengine import MongoEngine
import redis

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'taxes',
    'host': 'localhost',
    'port': 27017
}

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

db = MongoEngine()
db.init_app(app)


@app.route('/tax')
def tax_by_country():
    country_arg = request.args.get('country')

    tax = r.get(country_arg)
    if tax is not None:
        return jsonify({
            "Tax": tax
        })
    db_tax = Tax.objects(country=country_arg).first()
    r.set(country_arg, db_tax.value)
    if not db_tax:
        return jsonify({'error': 'data not found'})
    else:
        return jsonify(db_tax.to_json())


class Tax(db.Document):
    country = db.StringField()
    value = db.StringField()

    def to_json(self):
        return {"Country": self.country,
                "Tax": self.value}


if __name__ == "__main__":
    app.run(debug=True, port=5000)
