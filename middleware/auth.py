from functools import wraps
from flask import request, jsonify, g
import datetime
import uuid
import logging
from models.api_key import APIKey
from app import session
from datetime import datetime




def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            return jsonify({
                "success": False,
                "message": "API key is missing.",
                "details": "You must provide an API key in the 'X-API-KEY' header to access this resource.",
                "meta":{
                    "timestamp": datetime.now().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            }), 401
        
        api_key = session.query(APIKey).filter_by(key=api_key).first()
        if not api_key:
            return jsonify({
                "success": False,
                "message": "Invalid API key.",
                "details": "The provided API key is not valid.",
                "meta":{
                    "timestamp": datetime.now().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            }), 401
        if api_key.is_active==False:
            return jsonify({
                "success": False,
                "message": "API Key is already revoked",
                "meta":{
                    "timestamp": datetime.now().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            }), 401
        
        if api_key.window_start is None or api_key.window_start + datetime.timedelta(hours=1) < datetime.datetime.utcnow():
            api_key.window_start = datetime.datetime.utcnow()
            api_key.request_this_hour = 0
        
        if api_key.request_this_hour >= api_key.rate_limit:
            return jsonify({
                "success": False,
                "message": "Rate limit exceeded.",
                "details": f"You have exceeded the rate limit of {api_key.rate_limit} requests per hour.",
                "meta":{
                    "timestamp": datetime.now().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            }), 429
        else:
            api_key.request_this_hour += 1
            api_key.last_used_at = datetime.datetime.utcnow()
            api_key.usage_count += 1
            session.commit()

        g.api_key = api_key

        return f(*args, **kwargs)
    return decorated


