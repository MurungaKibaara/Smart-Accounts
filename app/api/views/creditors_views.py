'''Create post and get expense endpoints'''
import re
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, request, jsonify, make_response
from app.api.models.creditors_model import CreditorsRecords
from app.api.models.database_connection import init_db
from app.api.utils.validation import validate

INIT_DB = init_db()

CREDITORS = Blueprint('creditors', __name__)

CREDITORS_RECORDS = CreditorsRecords()

@CREDITORS.route('/creditor', methods=['POST'])
def post_credit():
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
            """  SELECT * FROM creditors WHERE (DATE(credit_date)) = '%s' """ % (format_date))
        data = cur.fetchall()

        if data is not None:
            for debt in data:
                db_amount = debt["amount"]
                int_amount = int(amount)

                if ((db_amount == int_amount) and debt["name"]==name and (debt["description"]==description)):
                    print(debt["name"])
                    return jsonify({"message":"creditor already posted"})

        try:
            return CREDITORS_RECORDS.add_creditor(name, amount, description, date)

        except (psycopg2.Error) as error:
            return jsonify(error)
                    
    except KeyError:
        return jsonify({"error": "a key is missing"}), 400


@CREDITORS.route('/creditor', methods=['GET'])
def get_creditors():
    '''Get all creditors'''
    return CREDITORS_RECORDS.get_all_creditors()

@CREDITORS.route('/creditor/<int:creditor_id>', methods=['GET'])
def get_creditor(creditor_id):
    '''Query a debt via id'''
    return CREDITORS_RECORDS.get_one_creditor(creditor_id)

@CREDITORS.route('/creditor/date', methods=['POST'])
def query_by_date():
    '''Query via date'''
    return CREDITORS_RECORDS.view_creditors_by_date()

@CREDITORS.route('creditor/name', methods=['POST'])
def query_by_name():
    '''Query via date'''
    return CREDITORS_RECORDS.view_creditors_by_name()

@CREDITORS.route('creditor/repay', methods=['POST'])
def update_repayments():
    '''Update records'''
    return CREDITORS_RECORDS.credit_repayment_records()