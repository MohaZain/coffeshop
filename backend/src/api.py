import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from sqlalchemy.sql.sqltypes import String

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def drinks():
    try:
        drinks = Drink.query.all()
        drinks_formated = [drink.short() for drink in drinks]

    except BaseException:
        abort(500)
    return jsonify({
        'success': True,
        'drinks': drinks_formated
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    try:
        drinks = Drink.query.all()
        drinks_formated = [drink.long() for drink in drinks]
    except BaseException:
        abort(500)
    return jsonify({
        'success': True,
        'drinks': drinks_formated
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    body = request.get_json()

    try:
        recipe = str(body.get('recipe'))
        recipe = recipe.replace("\'", "\"")
        drink = Drink(
            title=body.get('title'),
            recipe=recipe
        )
        drink.insert()
        drink.recipe = recipe
    except BaseException:
        abort(422)
    return jsonify({
        'success': True,
        'drinks': body.get('recipe')
    })


@app.route('/drinks/<int:drinks_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, drinks_id):
    body = request.get_json()
    drink = Drink.query.filter(Drink.id == drinks_id).one_or_none()

    if drink is None:
        abort(404)

    try:
        recipe_data = str(body.get('recipe'))
        recipe_data = recipe_data.replace("\'", "\"")

        title_data = body.get('title')

        drink.title = title_data
        drink.recipe = recipe_data

        drink.update()
    except BaseException:
        abort(500)

    return jsonify({
        'success': True,
        'drinks': body.get('recipe'),
        'title': title_data
    })


@app.route('/drinks/<int:drinks_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drinks_id):

    drink = Drink.query.filter(Drink.id == drinks_id).one_or_none()

    if drink is None:
        abort(404)
    try:
        drink.delete()
    except BaseException:
        abort(500)
    return jsonify({
        'success': True,
        'delete': drinks_id,
    })

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def internal_server(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(401)
def Unuthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unuthorized"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403
