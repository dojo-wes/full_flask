from flask import Flask, render_template, session, redirect, flash, request
from mysqlconnector import MySQLConnector

app = Flask(__name__)
mysql = MySQLConnector(app, 'py1_users')

@app.route('/')
def index():
  query = 'SELECT * FROM users'
  users_from_db = mysql.query_db(query)
  return render_template('index.html', users=users_from_db)

@app.route('/<user_id>/edit')
def edit(user_id):
  query = 'SELECT * FROM users WHERE id = :user_id'
  data = {
    'user_id': user_id
  }
  users_from_db = mysql.query_db(query, data)
  print users_from_db
  return render_template('edit.html', u_id = user_id, user = users_from_db[0])

app.run(debug = True)