from flask import Blueprint, request, jsonify, session
import bcrypt
import sqlite3
from testrfid import read_rfid
from rfid import await_scan, write_to_arduino
import os
import hmac
import hashlib
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

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
        # hash password for login verification (bcrypt)
        bsalt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), bsalt)

        # generate vault key
        vault_key = os.urandom(32)  # 256-bit key

        # derive encryption key from password using scrypt KDF
        kdf = Scrypt(salt=bsalt, length=32, n=2**14, r=8, p=1)
        derived_key = kdf.derive(password.encode('utf-8'))

        # encrypt vault key using derived key
        aesgcm = AESGCM(derived_key)
        vault_key_nonce = os.urandom(12)
        encrypted_vault_key = aesgcm.encrypt(vault_key_nonce, vault_key, None)

        conn = sqlite3.connect('backend/db/vault.db')
        cur = conn.cursor()

        cur.execute(
            '''INSERT INTO users 
               (username, password_hash, password_salt, rfid_uid, encrypted_vault_key, vault_key_nonce) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (username, hashed, bsalt, rfid_uid,
             encrypted_vault_key, vault_key_nonce)
        )

        conn.commit()
        conn.close()

        session['user_id'] = cur.lastrowid

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

        # check password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            return jsonify({ 'success': False, 'message': 'Invalid credentials.' }), 401

        # re-derive the encryption key from plaintext password + stored salt
        kdf = Scrypt(salt=user['password_salt'], length=32, n=2**14, r=8, p=1)
        derived_key = kdf.derive(password.encode('utf-8'))

        # decrypt vault key using derived key + stored nonce
        aesgcm = AESGCM(derived_key)
        vault_key = aesgcm.decrypt(user['vault_key_nonce'], user['encrypted_vault_key'], None)

        # store decrypted vault key in session
        session['user_id'] = user['user_id']
        session['vault_key'] = vault_key.hex()  # store as hex string since sessions are JSON
        session['password_verified'] = True
        session['rfid_verified'] = False

        return jsonify({ 'success': True })

    except Exception as e:
        print('Login error:', e)
        return jsonify({ 'success': False, 'message': 'Server error.' }), 500


@auth_bp.route('/api/auth/initialize-rfid', methods=['GET'])
def initialize_rfid():
    secret = os.urandom(64)

    write_to_arduino(secret)

    conn = sqlite3.connect('backend/db/vault.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    user = cur.execute(
        'INSERT INTO user_tokens (user_id, secret, counter) VALUES (?, ?, ?)', (session['user_id'], secret, 0,)
    )  
    conn.commit()
    conn.close()

    return jsonify({ 'success': True })

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

        if user['rfid_uid'] == rfid_uid:
            session['rfid_verified'] = True
            return jsonify({ 'success': True })

        # both password and RFID verified — grant access
        return jsonify({ 'success': False, 'message': 'RFID does not match.' }), 401

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