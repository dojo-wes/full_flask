from flask import Flask, render_template, session, redirect, flash, request
from mysqlconnector import MySQLConnector

import re
import md5
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'supersecret'

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

@app.route('/login', methods=['POST'])
def login():
  query = 'SELECT * FROM users WHERE email=:email'
  data = {
    "email": request.form['email']
  }
  users_list = mysql.query_db(query, data)
  
  # if we find a user with this email address, try to check the password
  if len(users_list) > 0:
    user = users_list[0]
    hashed_input = md5.new(request.form['password']).hexdigest()
    if hashed_input != user['pw_hash']:
      flash('invalid username or password')
      return redirect('/new')
    else:
      session['user_id'] = user['id']
      return redirect('/')
  
  flash('invalid username or password')
  return redirect('/new')

@app.route('/create', methods=['POST'])
def create():
  # print "*" * 80
  # print request.form
  # print "*" * 80

  # no fields blank
  # valid email
  # password is at least 8 char
  # password and confirm_password must match
  # make sure user doesn't already exist with email
  errors = False

  if len(request.form['first_name']) < 1:
    flash('First name must not be blank')
    errors = True
  if len(request.form['last_name']) < 1:
    flash('Last name must not be blank')
    errors = True
  if not EMAIL_REGEX.match(request.form['email']):
    flash('Please use a valid email address')
    errors = True
  if len(request.form['password']) < 8:
    flash('password must be more than 8 characters')
    errors = True
  if request.form['password'] != request.form['confirm_password']:
    flash('passwords must match')
    errors = True
  
  # check to see if email exists
  exists_query = 'SELECT * FROM users WHERE email = :email'
  data = {
    'email': request.form['email']
  }
  users_list = mysql.query_db(exists_query, data)
  # print "*" * 80
  # print users_list
  # print "*" * 80

  if len(users_list) > 0:
    flash('email already in use')
    errors = True

  if errors:
    return redirect('/new')
  else:
    hashed_pw = md5.new(request.form['password']).hexdigest()
    # print "*" * 80
    # print hashed_pw
    # print "*" * 80

    query = 'INSERT INTO users (first_name, last_name, email, pw_hash, created_at, updated_at) VALUES(:first_name, :last_name, :email, :pw_hash, NOW(), NOW())'
    data = {
      "first_name": request.form['first_name'],
      "last_name": request.form['last_name'],
      "email": request.form['email'],
      "pw_hash": hashed_pw
    }
    user_id = mysql.query_db(query, data)
    session['user_id'] = user_id
    return redirect('/')

@app.route('/logout')
def logout():
  session.clear()
  return redirect('/')

@app.route('/new')
def new():
  return render_template('new.html')

app.run(debug = True)