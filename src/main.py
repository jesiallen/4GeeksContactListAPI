"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Contact
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/contact/all', methods=['GET'])
def get_contacts():
    contact_query = Contact.query.all()
    all_people = list(map(lambda x: x.serialize(), contact_query))
    return jsonify(all_people)

@app.route('/contact', methods=['POST'])
def add_contact():
    body= request.get_json()
    contact=Contact(name= body['full_name'], email=body['email'], address=body['address'], phone= body['phone'])
    db.session.add(contact)
    db.session.commit()
    if body is None:
        return "The request body is null", 400
    elif body['full_name'] is None:
        return "The request has no name", 400
    else:
        contact_query = Contact.query.all()
        all_people = list(map(lambda x: x.serialize(), contact_query))
        return jsonify(all_people)

@app.route('/contact/<contact_id>', methods=['GET'])
def get_contact(contact_id):
    user1 = Contact.query.get(contact_id)
    return jsonify(user1.serialize())

@app.route('/contact/<contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    user1 = Contact.query.get(contact_id)
    if user1 is None:
        raise APIException('User not found', status_code=404)
    db.session.delete(user1)
    db.session.commit()
    contact_query = Contact.query.all()
    all_people = list(map(lambda x: x.serialize(), contact_query))
    return jsonify(all_people)


@app.route('/contact/<contact_id>', methods=['PUT'])
def edit_contact(contact_id):
    body= request.get_json()
    user1 = Contact.query.get(contact_id)
    if user1 is None:
        raise APIException('User not found', status_code=404)
    if "full_name" in body:
        user1.full_name = body["full_name"]
    if "email" in body:
        user1.email = body["email"]
    if "phone" in body:
        user1.phone = body["phone"]
    if "address" in body:
        user1.address = body["address"]
    db.session.commit()
    contact_query = Contact.query.all()
    all_people = list(map(lambda x: x.serialize(), contact_query))
    return jsonify(all_people)






# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
