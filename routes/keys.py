from xml.parsers.expat import errors

from flask import Blueprint, app, request, jsonify
from flask import Flask, jsonify
from models.api_key import APIKey


keysBlueprint = Blueprint('keys', __name__)



# IMPORT
import secrets
import string
from uuid import uuid4
from datetime import datetime
from app import session, APIKey



@keysBlueprint.route('/keys', methods=['POST'])
def generate_api_key():
    if request.method == "POST":
        data = request.get_json()
        name = data.get('name')
        rate_limit = data.get('rate_limit', 200)  

        errors=[]
        if not name:
            errors.append({"Field": "Name", "Message": "Name is required"})
        
        if rate_limit is None:
            rate_limit = 100
        elif not isinstance(rate_limit, int) or isinstance(rate_limit, bool):
            errors.append({"field": "rate_limit", "message": "Rate limit must be an integer"})
        elif rate_limit <= 0:
            errors.append({"field": "rate_limit", "message": "Rate limit must be a positive integer"})
        elif rate_limit > 10000:
                errors.append({"field": "rate_limit", "message": "Rate limit cannot exceed 10000"})
        generated_key = "KV_" + secrets.token_urlsafe(32)

        if errors:
            return jsonify({
                "success": False,
                "message": "Validation Failed",
                "errors": errors,
                "meta":{
                    "timestamp": datetime.now().isoformat(),
                    "request_id": str(uuid4())
                }
            })
        else:
            new_key = APIKey(key=generated_key, name=name, rate_limit=rate_limit)
            session.add(new_key)
            session.commit()

            return jsonify({
                "success": True,
                "message": "API Key generated successfully",
                "data": {
                    "api_key": generated_key,
                    "name": name,
                    "rate_limit": rate_limit
                },
                "meta":{
                    "timestamp": datetime.now().isoformat(),
                    "request_id": str(uuid4())
                }
            })


        
@keysBlueprint.route('/keys', methods=['GET'])
def get_keys():
    keys = session.query(APIKey).all()
    keys_data = []
    for key in keys:
        keys_data.append({
            "id": key.id,
            "key": key.key,
            "name": key.name,
            "is_active": key.is_active,
            "usage_count": key.usage_count,
            "rate_limit": key.rate_limit,
            "created_at": key.created_at.isoformat(),
            "request_this_hour": key.request_this_hour,
            "window_start": key.window_start.isoformat() if key.window_start else None,
            "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None
        })
    return jsonify({
        "success": True,
        "message": "API Keys retrieved successfully",
        "data": keys_data,
        "meta":{
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid4())
        }
    })


@keysBlueprint.route('/keys/<key_id>', methods=['GET'])
def get_key(key_id):
    key = session.query(APIKey).filter_by(id=key_id).first()
    if key:
        key_data = {
            "id": key.id,
            "key": key.key,
            "name": key.name,
            "is_active": key.is_active,
            "usage_count": key.usage_count,
            "rate_limit": key.rate_limit,
            "created_at": key.created_at.isoformat(),
            "request_this_hour": key.request_this_hour,
            "window_start": key.window_start.isoformat() if key.window_start else None,
            "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None
        }
        return jsonify({
            "success": True,
            "message": "API Key retrieved successfully",
            "data": key_data,
            "meta":{
                "timestamp": datetime.now().isoformat(),
                "request_id": str(uuid4())
            }
        })
    else:
        return jsonify({
            "success": False,
            "message": "API Key not found",
            "meta":{
                "timestamp": datetime.now().isoformat(),
                "request_id": str(uuid4())
            }
        }), 404