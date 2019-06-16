'''model to handle debt'''
import re
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor, RealDictCursor
from flask import jsonify, request
from app.api.models.database_connection import init_db
from app.api.utils.validation import validate

INIT_DB = init_db()

class DebtRecords():
    """ Create a model that handles debt data"""

    def __init__(self):
        """initialize the database and argument variables"""
        self.database = INIT_DB

    def add_debt(self, name, amount, description, date):
        '''Add the debt data to database'''
        try: 
            payload = {
                "name":name,
                "amount": int(amount),
                "description": description,
                "date": date
            }
            print(payload)

            query = """INSERT INTO debtors (name, amount, description,
            debt_date) VALUES (%(name)s, %(amount)s, %(description)s, %(date)s)"""

            cur = self.database.cursor()
            cur.execute(query, payload)
            self.database.commit()

            return jsonify({"message":"successfully posted"})

        except (psycopg2.Error) as error:
            print(error)
            return jsonify({"error":"postgres error"})

    def get_all_debts(self):
        '''Get all debts'''
        try:
            cur = INIT_DB.cursor(cursor_factory=RealDictCursor)
            cur.execute("""SELECT * FROM debtors""")
            data = cur.fetchall()

            if data is None:
                return jsonify({"Message":"No debt/debtor found"}), 404

            debt_data = {
                "status": 200,
                "debts": data
                }, 200

            return jsonify(debt_data)

        except psycopg2.Error:
            return jsonify({"Error":"Could not get any debt"}), 400

        return jsonify({"Message":"No debt found"}), 400

    def get_one_debt(self, debtor_id):
        '''get one debt'''
        try:
            cur = INIT_DB.cursor(cursor_factory=RealDictCursor)
            cur.execute(""" SELECT * FROM debtors WHERE debtor_id = '%d' """ %(debtor_id))
            data = cur.fetchone()

            if data is None:
                return jsonify({"message":"No debt/debtor by that id"}), 404

            return jsonify(
                {"status": 200},
                data), 200

        except psycopg2.Error:
            return jsonify({
                "status": 400,
                "error":"error retrieving data from database"}), 400

    def debt_repayment_record(self):
        '''Update debt record'''
        try:
            data = request.get_json()

            name = data["name"]
            amount = data["amount"]
            description = "Repayment"
            date = data["date"]

            validate(name, amount, description, date)
            
            amount = -(int(amount))

            DebtRecords.add_debt(self, name, amount, description, date)

            cur = self.database.cursor()
            cur.execute("""  SELECT SUM(amount) FROM debtors WHERE name = '%s' """ % (name))
            data = cur.fetchall()

            total_amount= data[0]

            if data is None:
                return jsonify({
                    "status": 400,
                    "message": "No debt by that name"}), 404
            try:
                debt_remaining = total_amount

                return jsonify({
                    "status": 200,
                    "remaining debt": debt_remaining,
                    "message": "successfully update debt record"
                }), 200

            except psycopg2.Error:
                return jsonify({
                    "status": 400,
                    "error":"not updated"}), 400

        except KeyError:
            return jsonify({"error":"a key is missing"})


    def view_debts_by_date(self):
        '''Search for an expense using date'''
        try:
            date = request.get_json()["date"]

            if not date.strip():
                return jsonify({"error": "Date cannot be empty"}), 400

            if not re.match(r"^((0|1|2)[0-9]{1}|(3)[0-1]{1})-((0)[0-9]{1}|(1)[0-2]{1})-((19)[0-9]{2}|(20)[0-9]{2})$",date):
                return jsonify({"error":"input correct date format"}), 400
            
            format_date = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')

            cur = self.database.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """  SELECT * FROM debtors WHERE DATE(debt_date) = '%s' """ % (format_date))
            data = cur.fetchall()

            if data is None:
                return jsonify({"message":"No data for that date"})

            return jsonify({
                "status":200,
                "expense":data}), 200

        except (psycopg2.Error) as error:
            return jsonify(error)
        except KeyError:
            return jsonify({"error":"a key is missing"})

    def view_debts_by_name(self):
        '''Search for an expense using date'''
        try:
            name = request.get_json()["name"]

            if not name.strip():
                return jsonify({"error": "name cannot be empty"}), 400

            if not re.match(r"^[A-Za-z][a-zA-Z]", name):
                return jsonify({"error":"input valid name"}), 400

            cur = self.database.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """  SELECT * FROM debtors WHERE name = '%s' """ % (name))
            data = cur.fetchall()

            if data is None:
                return jsonify({"message":"name user does not exist"})

            return jsonify({
                "status":200,
                "expense":data}), 200

        except (psycopg2.Error) as error:
            return jsonify(error)

        except KeyError:
            return jsonify({"error":"a key is missing"})
