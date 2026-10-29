from flask_socketio import join_room, leave_room
from . import socketio


@socketio.on("join_event")
def on_join(data):
    join_room(f"event_{data['event_id']}")


@socketio.on("leave_event")
def on_leave(data):
    leave_room(f"event_{data['event_id']}")