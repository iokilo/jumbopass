from flask import Blueprint, request, jsonify
import bcrypt
from database import get_db
from rfid import read_rfid

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    rfid_uid = data.get('rfid_uid')

    if not username or not password or not rfid_uid:
        return jsonify({ 'success': False, 'message': 'All fields are required.' }), 400

    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        db = get_db()
        db.execute(
            "INSERT INTO users (username, password_hash, rfid_uid) VALUES (?, ?, ?)",
            (username, hashed.decode('utf-8'), rfid_uid)
        )
        db.commit()

        return jsonify({ 'success': True })

    except db.IntegrityError:
        return jsonify({ 'success': False, 'message': 'Username or RFID already exists.' }), 409

    except Exception as e:
        print('Register error:', e)
        return jsonify({ 'success': False, 'message': 'Server error.' }), 500


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({ 'success': False, 'message': 'All fields are required.' }), 400

    try:
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if not user:
            return jsonify({ 'success': False, 'message': 'Invalid credentials.' }), 401

        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({ 'success': False, 'message': 'Invalid credentials.' }), 401

        # password is correct, frontend will now poll for RFID
        return jsonify({ 'success': True, 'user_id': user['id'] })

    except Exception as e:
        print('Login error:', e)
        return jsonify({ 'success': False, 'message': 'Server error.' }), 500


@auth_bp.route('/api/auth/rfid-scan', methods=['GET'])
def rfid_scan():
    try:
        uid = read_rfid()

        if uid:
            return jsonify({ 'uid': uid })
        else:
            return jsonify({ 'uid': None })

    except Exception as e:
        print('RFID scan error:', e)
        return jsonify({ 'uid': None }), 500


@auth_bp.route('/api/auth/rfid-verify', methods=['POST'])
def rfid_verify():
    data = request.get_json()

    user_id = data.get('user_id')
    rfid_uid = data.get('rfid_uid')

    if not user_id or not rfid_uid:
        return jsonify({ 'success': False, 'message': 'Missing fields.' }), 400

    try:
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()

        if not user or user['rfid_uid'] != rfid_uid:
            return jsonify({ 'success': False, 'message': 'RFID does not match.' }), 401

        # both password and RFID verified — grant access
        return jsonify({ 'success': True })

    except Exception as e:
        print('RFID verify error:', e)
        return jsonify({ 'success': False, 'message': 'Server error.' }), 500


@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({ 'success': True })