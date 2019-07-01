'''Create post and get expense endpoints'''
import re
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, request, jsonify, make_response
from app.api.models.debtors_model import DebtRecords
from app.api.models.database_connection import init_db
from app.api.utils.validation import validate

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

        validate(name, amount, description, date)

        format_date = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
        
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
                    return jsonify({"message":"debt already posted"})

        try:
            return DEBT_RECORDS.add_debt(name, amount, description, format_date)

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
    return DEBT_RECORDS.view_debts_by_date()

@DEBTORS.route('debts/name', methods=['POST'])
def query_by_name():
    '''Query via date'''
    return DEBT_RECORDS.view_debts_by_name()

@DEBTORS.route('debts/repay', methods=['POST'])
def update_repayments():
    '''Update records'''
    return DEBT_RECORDS.debt_repayment_record()

@DEBTORS.route('debts/reporting', methods=['GET'])
def totals():
    '''Total debt'''
    return DEBT_RECORDS.reporting()