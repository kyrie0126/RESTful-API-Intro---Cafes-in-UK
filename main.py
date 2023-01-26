from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(app)

class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            #Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

db.create_all()

msg = {
        "response": {
            "success": "Successfully added the new cafe",
            "failure": "Cafe was not added"
        }
    }

@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())

@app.route('/all')
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    return jsonify(all_cafes=[cafe.to_dict() for cafe in cafes])

@app.route('/search')
def search_cafe_location():
    query_location = request.args.get("loc")
    cafes = db.session.query(Cafe).filter_by(location=query_location).all()
    if cafes:
        return jsonify(all_cafes=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location"})


## HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add_cafe():
    name = request.args.get('name')
    map_url = request.args.get('map')
    img_url = request.args.get('img')
    location = request.args.get('loc')
    seats = request.args.get('seats')
    has_toilet = bool(request.args.get('toilet'))
    has_wifi = bool(request.args.get('wifi'))
    has_sockets = bool(request.args.get('sockets'))
    can_take_calls = bool(request.args.get('calls'))
    coffee_price = request.args.get('price')

    new_cafe = Cafe(name=name, map_url=map_url, img_url=img_url, location=location, seats=seats, has_toilet=has_toilet, has_wifi=has_wifi, has_sockets=has_sockets, can_take_calls=can_take_calls, coffee_price=coffee_price)
    db.session.add(new_cafe)
    db.session.commit()
    if new_cafe:
        return jsonify(response={"Success": "Cafe added!"})
    else:
        return jsonify(response=msg["Error": "Cafe NOT added!"])


## HTTP PUT/PATCH - Update Record
@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    new_price = request.args.get('new_price')
    cafe_to_update = db.session.query(Cafe).get(cafe_id)
    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"Success": "Coffee price updated!"})
    else:
        return jsonify(response={"Error": "cafe_id not found"})


## HTTP DELETE - Delete Record
@app.route('/report-closed/<int:cafe_id>', methods=['DELETE'])
def del_cafe(cafe_id):
    api_key = request.args.get('api-key')
    cafe_to_delete = db.session.query(Cafe).get(cafe_id)
    if cafe_to_delete and api_key == "TopSecretAPIKey":
        db.session.delete(cafe_to_delete)
        db.session.commit()
        return jsonify(response={"Success": "Cafe deleted, thanks!"})
    elif cafe_to_delete:
        return jsonify(response={"Error": "Incorrect API Key"})
    elif api_key == "TopSecretAPIKey":
        return jsonify(response={"Erorr": "cafe_id not found"})
    else:
        return jsonify(repsonse={"Error": "It's all wrong, sorry!"})



if __name__ == '__main__':
    app.run(debug=True)
