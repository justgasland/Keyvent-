import jwt
from functools import wraps
from flask import Blueprint, config, request, jsonify, g
from app import session
from models.api_key import APIKey
from datetime import datetime, timedelta
import flask


auth_bp = Blueprint('auth', __name__)
SECRET_KEY= config("SECRET_KEY")


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    key_value = data.get('key')

    if not key_value:
        return jsonify({
            "success": False,
            "message": "API key is required",
            "error": { "code": "INVALID_API_KEY" }
        }), 401
    api_key = session.query(APIKey).filter_by(key=key_value).first()