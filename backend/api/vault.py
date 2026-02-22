from flask import Blueprint, request, jsonify, session
import sqlite3

vault_bp = Blueprint('vault', __name__)

@vault_bp.route('/api/vault', methods=['GET'])
def get_credentials():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({ 'success': False, 'message': 'Not logged in.' }), 401

    conn = sqlite3.connect('backend/db/vault.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    credentials = cur.execute(
        'SELECT * FROM vault_entries WHERE user_id = ?', (user_id,)
    ).fetchall()
    if credentials is None:
        print('No credentials found for user_id:', user_id)
        credentials = []

    conn.close()

    return jsonify({
        'success': True,
        'credentials': [dict(row) for row in credentials]
    })


@vault_bp.route('/api/vault', methods=['POST'])
def add_credential():
    return jsonify({ 'success': True })


@vault_bp.route('/api/vault/<int:id>', methods=['PUT'])
def update_credential(id):
    return jsonify({ 'success': True })


@vault_bp.route('/api/vault/<int:id>', methods=['DELETE'])
def delete_credential(id):
    return jsonify({ 'success': True })

# testing with seeding
@vault_bp.route('/api/test/seed', methods=['GET'])
def seed():
    conn = sqlite3.connect('backend/db/vault.db')
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO vault_entries (user_id, category, nonce, name, username, password, url, notes, last_updated, created_at)
        VALUES
        (1, 'gaming', 'hi', 'Roblox', 'enderscythe', 'skibma', 'https://www.roblox.com/', 'roblox account', 0, 0)
    ''')

    conn.commit()
    conn.close()
    return jsonify({ 'success': True, 'message': 'Seeded.' })

#t testing with hard coded user
@vault_bp.route('/api/test/set-session')
def set_session():
    session['user_id'] = 1  # hardcode a user_id that exists in your DB
    session['password_verified'] = True
    session['rfid_verified'] = True
    return jsonify({ 'success': True, 'message': 'Session set.' })