import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from dotenv import load_dotenv
from crypto_utils import generate_rsa_keys, encrypt_message, decrypt_message, generate_aes_key, encrypt_aes_key, decrypt_aes_key
from models import db, User, ChatRoom, Message
from datetime import datetime
import base64

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
socketio = SocketIO(app)

# Vintage color themes
VINTAGE_THEMES = {
    'sepia': {'bg': '#f4e9d8', 'text': '#5a4a3a', 'accent': '#8b6b4a'},
    'old_paper': {'bg': '#f0e6d2', 'text': '#4a3c29', 'accent': '#7d5c3e'},
    'classic_green': {'bg': '#e8f0e0', 'text': '#3a4a3a', 'accent': '#5a7d5a'},
    'vintage_blue': {'bg': '#e0e8f0', 'text': '#3a3a4a', 'accent': '#5a5a7d'},
    'antique_rose': {'bg': '#f0e0e8', 'text': '#4a3a3a', 'accent': '#7d5a5a'}
}

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('chat'))

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    rooms = ChatRoom.query.all()
    theme = session.get('theme', 'sepia')
    
    return render_template('chat.html', 
                         user=user, 
                         rooms=rooms,
                         themes=VINTAGE_THEMES,
                         current_theme=theme)

@app.route('/change_theme/<theme_name>')
def change_theme(theme_name):
    if theme_name in VINTAGE_THEMES:
        session['theme'] = theme_name
    return redirect(url_for('chat'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # In production, use proper password hashing
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # Simple check for demo
            session['user_id'] = user.id
            session['theme'] = user.theme_preference or 'sepia'
            return redirect(url_for('chat'))
        
        return render_template('auth/login.html', error="Invalid credentials")
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            return render_template('auth/register.html', error="Username already exists")
        
        # Generate RSA keys for the new user
        private_key, public_key = generate_rsa_keys()
        
        user = User(
            username=username,
            password=password,  # In production, hash this
            public_key=public_key,
            private_key=private_key,
            theme_preference='sepia'
        )
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        return redirect(url_for('chat'))
    
    return render_template('auth/register.html')

@socketio.on('connect')
def handle_connect():
    if 'user_id' not in session:
        return False
    user = User.query.get(session['user_id'])
    emit('user_connected', {'username': user.username})

@socketio.on('join_room')
def handle_join_room(data):
    room_id = data['room_id']
    join_room(room_id)
    room = ChatRoom.query.get(room_id)
    emit('room_message', {'msg': f"{session['username']} joined the room"}, room=room_id)

@socketio.on('send_message')
def handle_send_message(data):
    room_id = data['room_id']
    encrypted_message = data['message']
    aes_key_encrypted = data['aes_key']
    
    # In a real app, you'd decrypt the AES key with your private key first
    # Then decrypt the message with the AES key
    
    # For demo, we'll just pass through the encrypted message
    message = Message(
        room_id=room_id,
        user_id=session['user_id'],
        content=encrypted_message,
        encrypted=True,
        timestamp=datetime.utcnow()
    )
    db.session.add(message)
    db.session.commit()
    
    user = User.query.get(session['user_id'])
    
    emit('new_message', {
        'message': encrypted_message,
        'username': user.username,
        'timestamp': datetime.utcnow().isoformat(),
        'is_encrypted': True
    }, room=room_id)

if __name__ == '__main__':
    socketio.run(app, debug=True, ssl_context='adhoc')