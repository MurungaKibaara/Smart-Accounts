import os
import psycopg2
from flask import jsonify

DB_URL = os.getenv('DATABASE')

def init_db():
    '''Connecting to the DB'''
    conn = psycopg2.connect(DB_URL)
    return conn

def create_tables():
    '''Function for creating tables in database'''
    conn = init_db()
    cur = conn.cursor()
    queries = tables()

    for query in queries:
        cur.execute(query)
        conn.commit()

def tables():
    '''Function to define the tables'''
    expenses_db = """CREATE TABLE IF NOT EXISTS expenses(
            expense_id serial PRIMARY KEY NOT NULL,
            account character varying(1000) NOT NULL,
            amount INT NOT NULL,
            description character varying(1000) NOT NULL,
            expense_date DATE DEFAULT CURRENT_DATE);
            """

    debtors_db = """CREATE TABLE IF NOT EXISTS debtors (
            name character varying(1000) NOT NULL,
            phonenumber serial PRIMARY KEY NOT NULL,
            amount INTEGER NOT NULL,
            description character varying(1000) NOT NULL,
            debt_date DATE NOT NULL DEFAULT CURRENT_DATE);
            """

    creditors_db = """CREATE TABLE IF NOT EXISTS questions (
            name character varying(1000) NOT NULL,
            phonenumber serial PRIMARY KEY NOT NULL,
            amount INTEGER NOT NULL,
            description character varying(1000) NOT NULL,
            credit_date DATE NOT NULL DEFAULT CURRENT_DATE);
            """

    queries = [expenses_db, debtors_db, creditors_db]

    return queries
