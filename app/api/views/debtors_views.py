'''Create post and get expense endpoints'''
import re
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, request, jsonify, make_response
from app.api.models.debtors_model import DebtRecords, view_debts_by_date, view_debts_by_name
from app.api.models.database_connection import init_db

INIT_DB = init_db()

DEBTORS = Blueprint('debtors', __name__)

DEBT_RECORDS = DebtRecords()

@DEBTORS.route('/debts', methods=['POST'])
def post_debt():
    '''post expenses endpoint'''
    try:
        data = request.get_json()

        date = data["date"]
        name = data["name"]
        amount = data["amount"]
        description = data["description"]

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

        format_date = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
        print(amount)
        
        cur = INIT_DB.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """  SELECT * FROM debtors WHERE (DATE(debt_date)) = '%s' """ % (format_date))
        data = cur.fetchall()

        if data is not None:
            for debt in data:
                db_amount = debt["amount"]
                int_amount = int(amount)

                if ((db_amount == int_amount) and debt["name"]==name and (debt["description"]==description)):
                    print(debt["name"])
                    return jsonify({"message":"Debt already posted"})

        try:
            return DEBT_RECORDS.add_debt(name, amount, description, date)

        except (psycopg2.Error) as error:
            return jsonify(error)
                    
    except KeyError:
        return jsonify({"error": "a key is missing"}), 400


@DEBTORS.route('/debts', methods=['GET'])
def get_all_debt():
    '''Get all debts'''
    return DEBT_RECORDS.get_all_debts()

@DEBTORS.route('/debts/<int:debtor_id>', methods=['GET'])
def get_one_debt(debtor_id):
    '''Query a debt via id'''
    return DEBT_RECORDS.get_one_debt(debtor_id)

@DEBTORS.route('debts/date', methods=['POST'])
def query_by_date():
    '''Query via date'''
    return view_debts_by_date()

@DEBTORS.route('debts/name', methods=['POST'])
def query_by_name():
    '''Query via date'''
    return view_debts_by_name()