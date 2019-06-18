'''Create post and get expense endpoints'''
import re
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, request, jsonify, make_response
from app.api.models.expenses_model import ExpenseRecords, view_expenses
from app.api.models.database_connection import init_db

INIT_DB = init_db()

EXPENSES = Blueprint('expenses', __name__)

EXPENSE_RECORDS = ExpenseRecords()

@EXPENSES.route('/expenses', methods=['POST'])
def post_expense():
    '''post expenses endpoint'''
    try:
        data = request.get_json()

        date = data['date']
        amount = data['amount']
        account = date['account']
        description = ['description']

        name = account

        validate(name, amount, description, date)

        format_date = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
        
        cur = INIT_DB.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """  SELECT * FROM expenses WHERE (DATE(expense_date)) = '%s' """ % (format_date))
        data = cur.fetchall()

        if data is not None:
            for expense in data:
                db_amount=expense["amount"]
                int_amount = int(amount)
                print(int_amount)

                if ((db_amount == int_amount) and (expense["description"]==description) and (expense["account"]==account)):
                    return jsonify({"message":"Expense already created"})

        try:
            return EXPENSE_RECORDS.add_expense(format_date, account, amount, description)

        except (psycopg2.Error) as error:
            print(error)
            return jsonify({"error":"error posting to database"})
                    
    except KeyError:
        return jsonify({"error": "a key is missing"}), 400


@EXPENSES.route('/expenses', methods=['GET'])
def get_expenses():
    '''Allow users to get all question'''
    return EXPENSE_RECORDS.get_all_expenses()

@EXPENSES.route('/expenses/<int:expense_id>', methods=['GET'])
def get_one_expense(expense_id):
    '''Query an expense via date'''
    return EXPENSE_RECORDS.get_one_expense(expense_id)

@EXPENSES.route('expenses/query', methods=['POST'])
def query_by_date():
    '''Query via date'''
    return view_expenses()