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

        date = data["date"]
        amount = data["amount"]
        account = data["account"]
        description = data["description"]

        if not description.strip():
            return jsonify({"error": "Description cannot be empty"}), 400

        if not date.strip():
            return jsonify({"error": "Date cannot be empty"}), 400
        
        if not re.match(r"^((0|1|2)[0-9]{1}|(3)[0-1]{1})-((0)[0-9]{1}|(1)[0-2]{1})-((19)[0-9]{2}|(20)[0-9]{2})$",date):
            return jsonify({"error":"input correct date format"}), 400

        if not amount.strip():
            return jsonify({"error": "Amount cannot be empty"}), 400

        if not account.strip():
            return jsonify({"error": "Account cannot be empty"}), 400
        
        if not re.match(r"^[0-9]", amount):
            return jsonify({"error": "Enter a valid amount"}), 400

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
            return EXPENSE_RECORDS.add_expense(date, account, amount, description)

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