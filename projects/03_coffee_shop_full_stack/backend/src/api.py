from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def get_drinks():
    drinks = [d.short() for d in Drink.query.all()]
    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    drinks = [d.long() for d in Drink.query.all()]
    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    try:
        data = request.get_json()
        title = data['title']
        recipe = json.dumps(data['recipe'])
        new_drink = Drink(title=title, recipe=recipe)
        new_drink.insert()
        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        })
    except KeyError:
        return abort(422)
    except exc.IntegrityError:
        return abort(422, 'A drink with the same title exists')


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, drink_id):
    drink = Drink.query.get(drink_id)
    if drink is None:
        return abort(404)
    data = request.get_json()
    if 'title' in data:
        drink.title = data['title']
    if 'recipe' in data:
        drink.recipe = data['recipe']
    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    drink = Drink.query.get(drink_id)
    if drink is None:
        return abort(404)
    drink.delete()
    return jsonify({
        'success': True,
        'delete': drink_id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": str(error)
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Forbidden"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden"
    }), 403
