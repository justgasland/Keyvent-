from flask import Blueprint, request, jsonify
from models.api_key import APIKey
from models.event import Event
from models.rsvp import RSVP
from middleware.auth import require_api_key
from app import session
import datetime
import uuid


RSVPBlueprint = Blueprint('rsvp', __name__)


def build_meta():
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "request_id": str(uuid.uuid4())
    }

@RSVPBlueprint.route('/events/<event_id>/rsvps', methods=['POST'])
@require_api_key
def create_rsvp(event_id):
    data = request.get_json()
    api_key = request.headers.get('X-API-KEY')
    api_key_obj = session.query(APIKey).filter_by(key=api_key).first()

    event = session.query(Event).filter_by(id=event_id, api_key_id=api_key_obj.id).first()
    if not event:
        return jsonify({
            "success": False,
            "message": "Event not found.",
            "details": f"No event found with id {event_id} for the provided API key.",
            "meta": build_meta()
        }), 404

    name = data.get('name')
    email = data.get('email')
    response_value = data.get('response')

    errors = []
    if not name or not isinstance(name, str):
        errors.append("Name is required and must be a string.")
    if not email or not isinstance(email, str):
        errors.append("Email is required and must be a string.")
    if not response_value or not isinstance(response_value, str):
        errors.append("Response is required and must be a string.")
    else:
        response_value = response_value.strip().lower()
        if response_value not in ('accepted', 'declined'):
            errors.append("Response must be either 'accepted' or 'declined'.")

    if errors:
        return jsonify({
            "success": False,
            "message": "Invalid RSVP data.",
            "details": errors,
            "meta": build_meta()
        }), 422

    email = email.strip().lower()

    existing_rsvp = session.query(RSVP).filter_by(event_id=event_id, email=email).first()
    if existing_rsvp:
        existing_rsvp.name = name.strip()
        existing_rsvp.response = response_value
        existing_rsvp.updated_at = datetime.datetime.utcnow()
        session.commit()

        return jsonify({
            "success": True,
            "message": "RSVP updated successfully.",
            "data": {
                "id": existing_rsvp.id,
                "event_id": existing_rsvp.event_id,
                "name": existing_rsvp.name,
                "email": existing_rsvp.email,
                "response": existing_rsvp.response,
                "created_at": existing_rsvp.created_at.isoformat() if existing_rsvp.created_at else None,
                "updated_at": existing_rsvp.updated_at.isoformat() if existing_rsvp.updated_at else None
            },
            "meta": build_meta()
        }), 200

    new_rsvp = RSVP(
        event_id=event_id,
        name=name.strip(),
        email=email,
        response=response_value
    )
    session.add(new_rsvp)
    session.commit()

    return jsonify({
        "success": True,
        "message": "RSVP submitted successfully.",
        "data": {
            "id": new_rsvp.id,
            "event_id": new_rsvp.event_id,
            "name": new_rsvp.name,
            "email": new_rsvp.email,
            "response": new_rsvp.response,
            "created_at": new_rsvp.created_at.isoformat() if new_rsvp.created_at else None,
            "updated_at": new_rsvp.updated_at.isoformat() if new_rsvp.updated_at else None
        },
        "meta": build_meta()
    }), 201


@RSVPBlueprint.route('/events/<event_id>/rsvps', methods=['GET'])
@require_api_key
def list_rsvps(event_id):
    api_key = request.headers.get('X-API-KEY')
    api_key_obj = session.query(APIKey).filter_by(key=api_key).first()

    event = session.query(Event).filter_by(id=event_id, api_key_id=api_key_obj.id).first()
    if not event:
        return jsonify({
            "success": False,
            "message": "Event not found.",
            "details": f"No event found with id {event_id} for the provided API key.",
            "meta": build_meta()
        }), 404

    query = session.query(RSVP).filter_by(event_id=event_id)
    response_filter = request.args.get('response')
    if response_filter:
        response_filter = response_filter.strip().lower()
        if response_filter not in ('accepted', 'declined'):
            return jsonify({
                "success": False,
                "message": "Invalid response filter.",
                "details": "The response filter must be either 'accepted' or 'declined'.",
                "meta": build_meta()
            }), 422
        query = query.filter_by(response=response_filter)

    rsvps = query.all()
    data = [
        {
            "id": rsvp.id,
            "event_id": rsvp.event_id,
            "name": rsvp.name,
            "email": rsvp.email,
            "response": rsvp.response,
            "created_at": rsvp.created_at.isoformat() if rsvp.created_at else None,
            "updated_at": rsvp.updated_at.isoformat() if rsvp.updated_at else None
        }
        for rsvp in rsvps
    ]

    return jsonify({
        "success": True,
        "message": "RSVPs retrieved successfully.",
        "data": data,
        "meta": build_meta()
    }), 200


@RSVPBlueprint.route('/rsvps/<rsvp_id>', methods=['DELETE'])
@require_api_key
def delete_rsvp(rsvp_id):
    api_key = request.headers.get('X-API-KEY')
    api_key_obj = session.query(APIKey).filter_by(key=api_key).first()

    rsvp = session.query(RSVP).filter_by(id=rsvp_id).first()
    if not rsvp:
        return jsonify({
            "success": False,
            "message": "RSVP not found.",
            "details": f"No RSVP found with id {rsvp_id}.",
            "meta": build_meta()
        }), 404

    event = session.query(Event).filter_by(id=rsvp.event_id, api_key_id=api_key_obj.id).first()
    if not event:
        return jsonify({
            "success": False,
            "message": "Unauthorized access.",
            "details": "You do not have permission to delete this RSVP.",
            "meta": build_meta()
        }), 403

    session.delete(rsvp)
    session.commit()

    return jsonify({
        "success": True,
        "message": "RSVP deleted successfully.",
        "meta": build_meta()
    }), 200

    