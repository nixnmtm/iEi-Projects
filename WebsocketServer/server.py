from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect
import json

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route('/notifications/discover',  methods=['POST'])
def discovery():
    try:
        data = request.data
        data = json.loads(data)
        print(data)
        socketio.emit('my_response', data, namespace='/puzzle')
        return json.loads(data)
    except Exception as e:
        return ("Discovery Failed " + str(e))

@app.route('/notifications/interface_status',  methods=['POST'])
def connection():
    print("interface_status notifications")
    try:
        data = request.data
        data = json.loads(data)
        print(data)
        socketio.emit('interface', data, namespace='/puzzle')
        return json.loads(data)
    except Exception as e:
        return ("Connection Failed " + str(e))

# @app.route('/notifications/storage',  methods=['POST'])
# def storage():
#     print("notifications")
#     try:
#         data = read_json(request.data)
#         socketio.emit('storage', data, namespace='/puzzle')
#         print(data)
#         return data
#     except Exception as e:
#         return ("Storage Failed " + str(e))
#

# @app.route('/notifications/alarm',  methods=['POST'])
# def alarm():
#     print("notifications")
#     try:
#         data = read_json(request.data)
#         socketio.emit('alarm', data, namespace='/puzzle')
#         print(data)
#         return data
#     except Exception as e:
#         return ("Alarm Failed " + str(e))

@socketio.on('connect', namespace='/puzzle')
def connect():
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('disconnect', namespace='/puzzle')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=6555, host="0.0.0.0")
