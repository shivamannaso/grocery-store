import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="@Shivamjadhav33",
        database="grocery_store"
    )