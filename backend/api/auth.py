from flask import Blueprint, request, jsonify, session
import bcrypt
import sqlite3
from testrfid import read_rfid
from rfid import await_scan

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
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        conn = sqlite3.connect('backend/db/vault.db')
        cur = conn.cursor()

        cur.execute('INSERT INTO users (username, password_hash, password_salt, rfid_uid) VALUES (?, ?, ?, ?)', (username, hashed, salt, rfid_uid))
        conn.commit()
        conn.close()

        return jsonify({ 'success': True })

    except Exception as e:
        print('Register error:', e)
        return jsonify({ 'success': False, 'message': 'Server error.' }), 500


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    print('Login attempt received')
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({ 'success': False, 'message': 'All fields are required.' }), 400

    try:
        conn = sqlite3.connect('backend/db/vault.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        user = cur.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()   

        conn.commit()
        conn.close()

        if not user:
            return jsonify({ 'success': False, 'message': 'Invalid credentials.' }), 401

        # check password, move on to polling for rfid
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            session['user_id'] = user['user_id']
            session['password_verified'] = True
            session['rfid_verified'] = False
            return jsonify({ 'success': True })
            
        # password is incorrect, fail
        return jsonify({ 'success': False, 'message': 'Invalid credentials.' }), 401

    except Exception as e:
        print('Login error:', e)
        return jsonify({ 'success': False, 'message': 'Server error.' }), 500


@auth_bp.route('/api/auth/rfid-scan', methods=['GET'])
def rfid_scan():
    try:
        result = await_scan()
        # old = result[0]
        # new = result[1]

        if result:
            return jsonify({ 'uid': result })
        else:
            return jsonify({ 'uid': None })

    except Exception as e:
        print('RFID scan error:', e)
        return jsonify({ 'uid': None }), 500


@auth_bp.route('/api/auth/rfid-verify', methods=['POST'])
def rfid_verify():
    data = request.get_json()

    user_id = session.get('user_id')
    rfid_uid = data.get('rfid_uid')

    if not user_id or not rfid_uid:
        return jsonify({ 'success': False, 'message': 'Missing fields.' }), 400

    try:
        conn = sqlite3.connect('backend/db/vault.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        user = cur.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()

        conn.commit()
        conn.close()

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


# TESTING
@auth_bp.route('/api/auth/rfid-test', methods=['GET'])
def rfid_test():
    return jsonify({ 'uid': '12345678' })