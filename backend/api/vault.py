from flask import Blueprint, request, jsonify

vault_bp = Blueprint('vault', __name__)


@vault_bp.route('/api/vault', methods=['GET'])
def get_credentials():
    return jsonify({ 'success': True, 'credentials': [] })


@vault_bp.route('/api/vault', methods=['POST'])
def add_credential():
    return jsonify({ 'success': True })


@vault_bp.route('/api/vault/<int:id>', methods=['PUT'])
def update_credential(id):
    return jsonify({ 'success': True })


@vault_bp.route('/api/vault/<int:id>', methods=['DELETE'])
def delete_credential(id):
    return jsonify({ 'success': True })