import re
from flask import jsonify

def validate(name, amount, description, date):
    '''Validate data'''
    if not description.strip():
            return jsonify({"error": "Description cannot be empty"}), 400

    if not name.strip():
        return jsonify({"error": "name cannot be empty"}), 400

    if not re.match(r"^[A-Za-z][a-zA-Z]", name):
        return jsonify({"error":"input valid name"}), 400

    if not date.strip():
        return jsonify({"error": "Date cannot be empty"}), 400
    
    if not re.match(r"^((0|1|2)[0-9]{1}|(3)[0-1]{1})-((0)[0-9]{1}|(1)[0-2]{1})-((19)[0-9]{2}|(20)[0-9]{2})$",date):
        return jsonify({"error":"input correct date format"}), 400

    if not amount.strip():
        return jsonify({"error": "Amount cannot be empty"}), 400
    
    if not re.match(r"^[0-9]", amount):
        return jsonify({"error": "Enter a valid amount"}), 400