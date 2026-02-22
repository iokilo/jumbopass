from flask import Blueprint, request, jsonify, session
import sqlite3
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

vault_bp = Blueprint('vault', __name__)

DB = 'backend/db/vault.db'

def get_vault_key():
    vault_key_hex = session.get('vault_key')
    if not vault_key_hex:
        return None
    return bytes.fromhex(vault_key_hex)


@vault_bp.route('/api/vault', methods=['GET'])
def get_credentials():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({ 'success': False, 'message': 'Not logged in.' }), 401

    vault_key = get_vault_key()
    if not vault_key:
        return jsonify({ 'success': False, 'message': 'No vault key in session.' }), 401

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    rows = cur.execute(
        'SELECT * FROM vault_entries WHERE user_id = ?', (user_id,)
    ).fetchall()
    conn.close()

    credentials = []
    aesgcm = AESGCM(vault_key)

    for row in rows:
        try:
            decrypted_password = aesgcm.decrypt(
                bytes.fromhex(row['nonce']),
                bytes.fromhex(row['password']),
                None
            ).decode('utf-8')
        except Exception as e:
            print('Decryption error:', e)
            decrypted_password = '[decryption failed]'

        credentials.append({
            'id': row['entry_id'],
            'name': row['name'],
            'username': row['username'],
            'password': decrypted_password,
            'url': row['url'],
            'notes': row['notes']
        })

    return jsonify({ 'success': True, 'credentials': credentials })


@vault_bp.route('/api/vault', methods=['POST'])
def add_credential():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({ 'success': False, 'message': 'Not logged in.' }), 401

    vault_key = get_vault_key()
    if not vault_key:
        return jsonify({ 'success': False, 'message': 'No vault key in session.' }), 401

    data = request.get_json()
    name = data.get('name')
    username = data.get('username', '')
    password = data.get('password')
    url = data.get('url', '')
    notes = data.get('notes', '')

    if not name or not password:
        return jsonify({ 'success': False, 'message': 'Name and password are required.' }), 400

    # encrypt the password
    aesgcm = AESGCM(vault_key)
    nonce = os.urandom(12)
    encrypted_password = aesgcm.encrypt(nonce, password.encode('utf-8'), None)

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        '''INSERT INTO vault_entries (user_id, name, username, password, nonce, url, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (user_id, name, username,
         encrypted_password.hex(),  # store as hex string since schema uses TEXT
         nonce.hex(),
         url, notes)
    )
    conn.commit()
    conn.close()

    return jsonify({ 'success': True })


@vault_bp.route('/api/vault/<int:id>', methods=['DELETE'])
def delete_credential(id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({ 'success': False, 'message': 'Not logged in.' }), 401

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        'DELETE FROM vault_entries WHERE entry_id = ? AND user_id = ?', (id, user_id)
    )
    conn.commit()
    conn.close()

    return jsonify({ 'success': True })