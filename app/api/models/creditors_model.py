'''model to handle creditors'''
import re
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor, RealDictCursor
from flask import jsonify, request
from app.api.models.database_connection import init_db
from app.api.utils.validation import validate

INIT_DB = init_db()

class CreditorsRecords():
    """ Create a model that handles debt data"""

    def __init__(self):
        """initialize the database and argument variables"""
        self.database = INIT_DB

    def add_creditor(self, name, amount, description, date):
        '''Add the credit data to database'''
        try: 
            payload = {
                "name":name,
                "amount": int(amount),
                "description": description,
                "date": date
            }

            query = """INSERT INTO creditors (name, amount, description,
            credit_date) VALUES (%(name)s, %(amount)s, %(description)s, %(date)s)"""

            cur = self.database.cursor()
            cur.execute(query, payload)
            self.database.commit()

            return jsonify({"message":"successfully posted"})

        except (psycopg2.Error) as error:
            cur = conn.cursor()
            cur.execute("ROLLBACK")
            self.database.commit()

            print(error)

            return jsonify({"error":"error posting to database"})

    def get_all_creditors(self):
        '''Get all creditors'''
        try:
            cur = INIT_DB.cursor(cursor_factory=RealDictCursor)
            cur.execute("""SELECT * FROM creditors""")
            data = cur.fetchall()

            if data is None:
                return jsonify({"message":"No creditor found"}), 404

            return jsonify(data)

        except psycopg2.Error:
            return jsonify({"error":"Could not get any creditor"}), 400

        return jsonify({"message":"No debt found"}), 400

    def get_one_creditor(self, credit_id):
        '''get one creditor'''
        try:
            cur = INIT_DB.cursor(cursor_factory=RealDictCursor)
            cur.execute(""" SELECT * FROM creditors WHERE creditor_id = '%d' """ %(credit_id))
            data = cur.fetchone()

            if data is None:
                return jsonify({"message":"No creditor by that id"}), 404

            return jsonify(data)

        except psycopg2.Error:
            return jsonify({
                "status": 400,
                "error":"error retrieving data from database"}), 400

    def credit_repayment_records(self):
        '''Update creditor's records'''
        try:
            data = request.get_json()

            name = data["name"]
            amount = data["amount"]
            description = "Repayment"
            date = data["date"]

            validate(name, amount, description, date)
            
            amount = -(int(amount))

            CreditorsRecords.add_creditor(self, name, amount, description, date)

            cur = self.database.cursor()
            cur.execute("""  SELECT SUM(amount) FROM creditors WHERE name = '%s' """ % (name))
            data = cur.fetchall()

            total_amount= data[0]

            if data is None:
                return jsonify({
                    "status": 400,
                    "message": "No creditor by that name"}), 404
            try:
                debt_remaining = total_amount

                return jsonify(debt_remaining),

            except psycopg2.Error:
                return jsonify({"error":"not updated"}), 400

        except KeyError:
            return jsonify({"error":"a key is missing"}), 400


    def view_creditors_by_date(self):
        '''Search for a creditor by date'''
        try:
            date = request.get_json()["date"]

            if not date.strip():
                return jsonify({"error": "Date cannot be empty"}), 400

            if not re.match(r"^((0|1|2)[0-9]{1}|(3)[0-1]{1})-((0)[0-9]{1}|(1)[0-2]{1})-((19)[0-9]{2}|(20)[0-9]{2})$",date):
                return jsonify({"error":"input correct date format"}), 400
            
            format_date = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')

            cur = self.database.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """  SELECT * FROM creditors WHERE DATE(debt_date) = '%s' """ % (format_date))
            data = cur.fetchall()

            if data is None:
                return jsonify({"message":"No data for that date"}), 404

            return jsonify(data)

        except (psycopg2.Error) as error:
            return jsonify(error)
        except KeyError:
            return jsonify({"error":"a key is missing"})

    def view_creditors_by_name(self):
        '''Search for a creditor using name'''
        try:
            name = request.get_json()["name"]

            if not name.strip():
                return jsonify({"error": "name cannot be empty"}), 400

            if not re.match(r"^[A-Za-z][a-zA-Z]", name):
                return jsonify({"error":"input valid name"}), 400

            cur = self.database.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """  SELECT * FROM creditors WHERE name = '%s' """ % (name))
            data = cur.fetchall()

            if data is None:
                return jsonify({"message":"name user does not exist"})

            return jsonify(data)

        except (psycopg2.Error) as error:
            return jsonify(error)

        except KeyError:
            return jsonify({"error":"a key is missing"})
    
    def reporting(self):
        '''Generate Reports'''

        cur = self.database.cursor()
        cur.execute("""  SELECT SUM(amount) FROM creditors """)
        data = cur.fetchall()

        total_amount= data[0]

        return jsonify({'total': total_amount})


