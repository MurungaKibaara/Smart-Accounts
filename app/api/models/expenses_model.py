'''model to handle expense'''
import re
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor, RealDictCursor
from flask import jsonify, request
from app.api.models.database_connection import init_db

INIT_DB = init_db()

class ExpenseRecords():
    """ Create a model that handles expense data"""

    def __init__(self):
        """initialize the database and argument variables"""
        self.database = INIT_DB

    def add_expense(self, date, account, amount, description):
        '''Add the expense data to database'''
        try: 
            payload = {
                "date": date,
                "account": account,
                "amount": int(amount),
                "description": description
            }

            query = """INSERT INTO expenses (account, amount, description,
            expense_date) VALUES (%(account)s, %(amount)s, %(description)s,%(date)s)"""

            cur = self.database.cursor()
            cur.execute(query, payload)
            self.database.commit()

            return jsonify({"message":"successfully posted"})

        except (psycopg2.Error) as error:
            cur = self.database.cursor()
            cur.execute("ROLLBACK")
            self.database.commit()
            print(error)

            return jsonify({"error":"error posting to database"})

    def get_all_expenses(self):
        '''Get all questions'''
        try:
            cur = INIT_DB.cursor(cursor_factory=RealDictCursor)
            cur.execute("""SELECT * FROM expenses""")
            data = cur.fetchall()

            if data is None:
                return jsonify({"message":"expenses not found"}), 404

            return jsonify(data)

        except psycopg2.Error:
            return jsonify({"error":"Could not get any expenses"}), 400

        return jsonify({"message":"expenses not found"}), 400

    def get_one_expense(self, expense_id):
        '''get one question'''
        try:
            cur = INIT_DB.cursor(cursor_factory=RealDictCursor)
            cur.execute(""" SELECT * FROM expenses WHERE expense_id = '%d' """ %(expense_id))
            data = cur.fetchone()

            if data is None:
                return jsonify({"message":"No expense by that date"}), 404

            return jsonify(data)

        except psycopg2.Error:
            return jsonify({"error":"error retrieving data from database"}), 400

    def reporting(self):
        '''Generate Reports'''
        try:
            cur = self.database.cursor()
            cur.execute("""  SELECT SUM(amount) FROM expenses """)
            data = cur.fetchall()

            total_amount= data[0]

            return jsonify({'total': total_amount})

        except psycopg2.Error as error:
            return jsonify({"error":"encountered problem while retrieving data from database"}), 400

    def view_expenses_by_account(self):
        '''Search for an expense using date'''
        try:
            account = request.get_json()["account"]

            if not account.strip():
                return jsonify({"error": "account cannot be empty"}), 400

            if not re.match(r"^[A-Za-z][a-zA-Z]", account):
                return jsonify({"error":"input valid account"}), 400

            cur = self.database.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """  SELECT * FROM expenses WHERE account = '%s' """ % (account))
            data = cur.fetchall()

            if data is None:
                return jsonify({"message":"name user does not exist"})

            return jsonify(data), 200

        except (psycopg2.Error) as error:
            return jsonify(error)

        except KeyError:
            return jsonify({"error":"a key is missing"})

def view_expenses():
    '''Search for an expense using date'''
    try:
        date = request.get_json()["date"]

        if not date.strip():
            return jsonify({"error": "date cannot be empty"}), 400

        if not re.match(r"^((0|1|2)[0-9]{1}|(3)[0-1]{1})-((0)[0-9]{1}|(1)[0-2]{1})-((19)[0-9]{2}|(20)[0-9]{2})$",date):
            return jsonify({"error":"input correct date format"}), 400
        
        format_date = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')

        cur = INIT_DB.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """  SELECT * FROM expenses WHERE DATE(expense_date) = '%s' """ % (format_date))
        data = cur.fetchall()

        if data is None:
            return jsonify({"message":"no data for that date"})

        return jsonify(data)

    except (psycopg2.Error) as error:
        return jsonify(error)
    except KeyError:
        return jsonify({"error":"a key is missing"})

    


   
