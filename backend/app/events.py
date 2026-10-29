from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from sqlalchemy import func
from . import db, socketio
from .models import Event, Participant, Score

events_bp = Blueprint("events", __name__, url_prefix="/api/events")


def is_staff():
    return get_jwt().get("role") in ("organizer", "admin")


def leaderboard(event_id):
    total = func.coalesce(func.sum(Score.points), 0)
    rows = (
        db.session.query(Participant.id, Participant.name, Participant.college, total)
        .outerjoin(Score, Score.participant_id == Participant.id)
        .filter(Participant.event_id == event_id)
        .group_by(Participant.id)
        .order_by(total.desc())
        .all()
    )
    return [
        {"rank": i + 1, "participant_id": r[0], "name": r[1], "college": r[2], "total": int(r[3])}
        for i, r in enumerate(rows)
    ]


@events_bp.post("")
@jwt_required()
def create_event():
    if not is_staff():
        return jsonify(error="Organizer only"), 403
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify(error="name required"), 400
    ev = Event(
        name=data["name"],
        description=data.get("description"),
        organizer_id=int(get_jwt_identity()),
    )
    db.session.add(ev)
    db.session.commit()
    return jsonify(id=ev.id, name=ev.name, status=ev.status), 201


@events_bp.get("")
def list_events():
    return jsonify([
        {"id": e.id, "name": e.name, "description": e.description, "status": e.status}
        for e in Event.query.order_by(Event.created_at.desc()).all()
    ])


@events_bp.post("/<int:event_id>/participants")
@jwt_required()
def add_participant(event_id):
    if not db.session.get(Event, event_id):
        return jsonify(error="Event not found"), 404
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify(error="name required"), 400
    p = Participant(
        event_id=event_id,
        user_id=int(get_jwt_identity()),
        name=data["name"],
        college=data.get("college"),
    )
    db.session.add(p)
    db.session.commit()
    socketio.emit("leaderboard_update", leaderboard(event_id), to=f"event_{event_id}")
    return jsonify(id=p.id, name=p.name), 201


@events_bp.post("/<int:event_id>/scores")
@jwt_required()
def add_score(event_id):
    if not is_staff():
        return jsonify(error="Organizer only"), 403
    data = request.get_json() or {}
    p = db.session.get(Participant, data.get("participant_id"))
    if not p or p.event_id != event_id:
        return jsonify(error="Participant not in this event"), 404

    db.session.add(Score(
        event_id=event_id,
        participant_id=p.id,
        round_no=data.get("round_no", 1),
        points=int(data.get("points", 0)),
    ))
    db.session.commit()

    board = leaderboard(event_id)
    socketio.emit("leaderboard_update", board, to=f"event_{event_id}")
    return jsonify(board)


@events_bp.get("/<int:event_id>/leaderboard")
def get_leaderboard(event_id):
    return jsonify(leaderboard(event_id))