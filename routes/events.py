from flask import Blueprint, request, jsonify, g
from models.api_key import APIKey
from models.event import Event
from models.rsvp import RSVP
from middleware.auth import require_api_key
from app import session
import datetime
import uuid
from utils.conflict import find_conflict



EventBlueprint = Blueprint('events', __name__)


@EventBlueprint.route('/events', methods=['POST'])
@require_api_key
def create_event():
    if request.method == 'POST':
        data = request.get_json()
        api_key = request.headers.get('X-API-KEY')
        api_key = session.query(APIKey).filter_by(key=api_key).first()

        

        title = data.get('title')
        description = data.get('description')
        location = data.get('location')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        errors = []
        if not title:
            errors.append("Title is required.")
        elif not isinstance(title, str):
            errors.append("Title must be a string.")

        if not start_time:
            errors.append("You must specify the start time.")
        elif not isinstance(start_time, str):
            errors.append("start_time must be a string in ISO 8601 format.")

        if not end_time:
            errors.append("You must specify the end time.")
        elif not isinstance(end_time, str):
            errors.append("end_time must be a string in ISO 8601 format.")

        if errors:
            return jsonify({
                "success": False,
                "message": "Invalid input data.",
                "details": errors,
                "meta": {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            }), 422

        try:
            start_time = datetime.datetime.fromisoformat(start_time)
        except ValueError:
            errors.append("start_time must be a valid ISO 8601 date-time string.")

        try:
            end_time = datetime.datetime.fromisoformat(end_time)
        except ValueError:
            errors.append("end_time must be a valid ISO 8601 date-time string.")

        if not errors:
            if start_time <= datetime.datetime.utcnow():
                errors.append("start_time must be in the future.")
            if end_time <= start_time:
                errors.append("end_time must be after start_time.")

        if errors:
            return jsonify({
                "success": False,
                "message": "Invalid input data.",
                "details": errors,
                "meta": {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            }), 422

        

        new_event = Event(
            api_key_id=api_key.id,
            title=title,
            description=description,
            location=location,
            start_time=start_time,
            end_time=end_time
        )
        event = session.query(Event).all()
        conflict = find_conflict(api_key.id, start_time, end_time)
        if conflict:
            return jsonify({
                    "success": False,
                    "message": "Event already exists.",
                    "details": "An event with the same title, start time, and end time already exists.",
                    "meta": {
                        "timestamp": datetime.datetime.now().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
            }), 409
            
        session.add(new_event)
        session.commit()
        return jsonify({
                        "success": True,
                        "message": "Event created successfully.",
                        "data": {
                            "id": new_event.id,
                            "title": new_event.title,
                            "description": new_event.description,
                            "location": new_event.location,
                            "start_time": new_event.start_time,
                            "end_time": new_event.end_time,
                            "created_at": new_event.created_at.isoformat(),
                            "updated_at": new_event.updated_at.isoformat()
                        },
                        "meta": {
                            "timestamp": datetime.datetime.now().isoformat(),
                            "request_id": str(uuid.uuid4())
                        }
        }), 201


@EventBlueprint.route('/events', methods=['GET'])
@require_api_key 
def get_events():
    api_Key= request.headers.get('X-API-KEY')
    query = session.query(Event).filter_by(api_key_id=session.query(APIKey).filter_by(key=api_Key).first().id)
    events = query.all()

    # filters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Event.start_time >= start_dt)
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid start_date format.",
                "details": "start_date must be a valid ISO 8601 date-time string.",
                "meta": {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            }), 422
        

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(Event.start_time <= end_dt)
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid end_date format.",
                "details": "end_date must be a valid ISO 8601 date-time string.",
                "meta": {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            }), 422


    events_data = []
    for event in events:
        events_data.append({
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "location": event.location,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "created_at": event.created_at.isoformat(),
            "updated_at": event.updated_at.isoformat()
        })
    return jsonify({
        "success": True,
        "message": "Events retrieved successfully.",
        "data": events_data,
        "meta": {
            "timestamp": datetime.datetime.now().isoformat(),
            "request_id": str(uuid.uuid4())
        }
    }), 200


@EventBlueprint.route('/events/<int:event_id>', methods=['GET'])
@require_api_key
def get_event(event_id):
    api_key = request.headers.get('X-API-KEY')
    event = session.query(Event).filter_by(id=event_id, api_key_id=session.query(APIKey).filter_by(key=api_key).first().id).first()
    if not event:
        return jsonify({
            "success": False,
            "message": "Event not found.",
            "details": f"No event found with id {event_id} for the provided API key.",
            "meta": {
                "timestamp": datetime.datetime.now().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        }), 404

    return jsonify({
        "success": True,
        "message": "Event retrieved successfully.",
        "data": {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "location": event.location,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "created_at": event.created_at.isoformat(),
            "updated_at": event.updated_at.isoformat()
        },
        "meta": {
            "timestamp": datetime.datetime.now().isoformat(),
            "request_id": str(uuid.uuid4())
        }
    }), 200


@EventBlueprint.route('/events/<int:event_id>', methods=['PUT'])
@require_api_key
def update_event(event_id):
    api_key = request.headers.get('X-API-KEY')
    api_key_obj = session.query(APIKey).filter_by(key=api_key).first()
    if not api_key_obj:
        return jsonify({
            "success": False,
            "message": "Invalid API key.",
            "details": "The provided API key is not valid.",
            "meta": {
                "timestamp": datetime.datetime.now().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        }), 401

    event = session.query(Event).filter_by(id=event_id, api_key_id=api_key_obj.id).first()
    if api_key_obj.id != event.api_key_id:
        return jsonify({
            "success": False,
            "message": "Unauthorized access.",
            "details": "You do not have permission to access this event.",
            "meta": {
                "timestamp": datetime.datetime.now().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        }), 403
    
    if not event:
        return jsonify({
            "success": False,
            "message": "Event not found.",
            "details": f"No event found with id {event_id} for the provided API key.",
            "meta": {
                "timestamp": datetime.datetime.now().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        }), 404

    data = request.get_json()
    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid JSON data.",
            "details": "The request body must contain valid JSON data.",
            "meta": {
                "timestamp": datetime.datetime.now().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        }), 400

    title = data.get('title')
    description = data.get('description')
    location = data.get('location')
    start_time = data.get('start_time')
    end_time = data.get('end_time')

    errors = []
    if title is not None and not isinstance(title, str):
        errors.append("Title must be a string.")

    if start_time is not None and not isinstance(start_time, str):
        errors.append("start_time must be a string in ISO 8601 format.")

    if end_time is not None and not isinstance(end_time, str):
        errors.append("end_time must be a string in ISO 8601 format.")

    if errors:
        return jsonify({
            "success": False,
            "message": "Invalid input data.",
            "details": errors,
            "meta": {
                "timestamp": datetime.datetime.now().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        }), 422

    title = title if title is not None else event.title
    description = description if description is not None else event.description
    location = location if location is not None else event.location

    if start_time is not None:
        try:
            start_time = datetime.datetime.fromisoformat(start_time)
        except ValueError:
            errors.append("start_time must be a valid ISO 8601 date-time string.")
    else:
        start_time = event.start_time

    if end_time is not None:
        try:
            end_time = datetime.datetime.fromisoformat(end_time)
        except ValueError:
            errors.append("end_time must be a valid ISO 8601 date-time string.")
    else:
        end_time = event.end_time

    if not errors:
        if start_time != event.start_time and start_time <= datetime.datetime.utcnow():
            errors.append("start_time must be in the future.")
        if end_time <= start_time:
            errors.append("end_time must be after start_time.")

    if errors:
        return jsonify({
            "success": False,
            "message": "Invalid input data.",
            "details": errors,
            "meta": {
                "timestamp": datetime.datetime.now().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        }), 422

    conflict = find_conflict(api_key_obj.id, start_time, end_time)
    if conflict:
        return jsonify({
            "success": False,
            "message": "Event already exists.",
            "details": "An event with the same title, start time, and end time already exists.",
            "meta": {
                "timestamp": datetime.datetime.now().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        }), 409
    

    event.title = title
    event.description = description
    event.location = location
    event.start_time = start_time
    event.end_time = end_time

    session.commit()

    return jsonify({
        "success": True,
        "message": "Event updated successfully.",
        "data": {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "location": event.location,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "created_at": event.created_at.isoformat(),
            "updated_at": event.updated_at.isoformat()
        },
        "meta": {
            "timestamp": datetime.datetime.now().isoformat(),
            "request_id": str(uuid.uuid4())
        }
    }), 200

@EventBlueprint.route('/events/<int:event_id>', methods=['DELETE'])
@require_api_key
def delete_event(event_id):
    api_key = request.headers.get('X-API-KEY')
    api_key_obj = session.query(APIKey).filter_by(key=api_key).first()
    if not api_key_obj:
        return jsonify({
            "success": False,
            "message": "Invalid API key.",
            "details": "The provided API key is not valid.",
            "meta": {
                "timestamp": datetime.datetime.now().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        }), 401
    
    event = session.query(Event).filter_by(id=event_id, api_key_id=api_key_obj.id).first()
    if not event:
        return jsonify({
            "success": False,
            "message": "Event not found.",
            "details": f"No event found with id {event_id} for the provided API key.",
            "meta": {
                "timestamp": datetime.datetime.now().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        }), 404
    if api_key_obj.id != event.api_key_id:
        return jsonify({
            "success": False,
            "message": "Unauthorized access.",
            "details": "You do not have permission to access this event.",
            "meta": {
                "timestamp": datetime.datetime.now().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        }), 403
    session.delete(event)
    session.commit()
    return jsonify({
        "success": True,
        "message": "Event deleted successfully.",
        "meta": {
            "timestamp": datetime.datetime.now().isoformat(),
            "request_id": str(uuid.uuid4())
        }
    }), 200

