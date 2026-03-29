from flask import Blueprint, request, jsonify
from models.api_key import APIKey
from models.event import Event
from models.rsvp import RSVP
from middleware.auth import require_api_key
from app import session
import datetime
import uuid


events_bp = Blueprint('events', __name__)


@events_bp.route('/events', methods=['POST'])
@require_api_key
def create_event():
    if request.method == 'POST':
        data = request.get_json()
        api_key = request.headers.get('X-API-KEY')
        api_key = session.query(APIKey).filter_by(key=api_key).first()

        # title = data.get('title')
        # description = data.get('description')
        # location = data.get('location')
        # start_time = data.get('start_time')
        # end_time = data.get('end_time')

        # start_time= str(start_time)
        # end_time= str(end_time)

        # error=[]
        # if not title:
        #     error.append("Title, start_time and end_time are required fields.")
        # elif isinstance(title, str) :
        #     error.append("Title must be a string")
        
        # if  start_time is None:
        #     error.append(" You must specify the start time.")
        # elif not isinstance(start_time, str):
        #     error.append("start_time must be a string in ISO 8601 format.")
        # elif start_time < datetime.datetime.now().isoformat():
        #     error.append("start_time must be in the future.")
        

        # if end_time is None:
        #     error.append(" You must specify the end time.")
        # elif not isinstance(end_time, str):
        #     error.append("end_time must be a string in ISO 8601 format.")
        # elif start_time and end_time <= start_time:
        #     error.append("end_time must be after start_time.")
        
        # start_time = datetime.datetime.fromisoformat(start_time)
        # end_time= datetime.datetime.fromisoformat(end_time)
        # if error:
        #     return jsonify({
        #         "success": False,
        #         "message": "Invalid input data.",
        #         "details": error,
        #         "meta": {
        #             "timestamp": datetime.now().isoformat(),
        #             "request_id": str(uuid.uuid4())
        #         }
        #     }), 422

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
        for e in event:
            if e.title == title and e.start_time == start_time and e.end_time == end_time:
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


# 130cf39e-5085-4248-b85a-3e8a85c3315b

