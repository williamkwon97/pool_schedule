import os
import time
import operator

from flask import request
from flask import Flask, render_template
from flask import make_response
import mysql.connector
from mysql.connector import errorcode
import requests
from operator import itemgetter
import json

application = Flask(__name__)
app = application




def get_db_creds():
    db = os.environ.get("DB", None) or os.environ.get("database", None)
    username = os.environ.get("USER", None) or os.environ.get("username", None)
    password = os.environ.get("PASSWORD", None) or os.environ.get("password", None)
    hostname = os.environ.get("HOST", None) or os.environ.get("dbhost", None)
    return db, username, password, hostname


def create_table():

    db, username, password, hostname = get_db_creds()
    table_ddl = 'CREATE TABLE pools(pool_name VARCHAR(100), '
    'status TEXT NOT NULL, phone TEXT, '
    'pool_type TEXT, PRIMARY KEY (pool_name))'


    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname,
                                      database=db)


    except Exception as exp:
        print(exp)


    cur = cnx.cursor()

    try:
        cur.execute(table_ddl)
        cnx.commit()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)









@app.route('/pools', methods=['POST'])
def add_pool():
    print("request receieved")
    print(request.json)


    pool_name = request.json['pool_name']
    status = request.json['status']
    phone= request.json['phone']
    pool_type = request.json['pool_type']
    if (status == 'Closed') or (status == 'Open') or (status== 'in Renovation'):
        statusTF=True
    else:
        return 'Message: status field has invalid value', 400
    if (pool_type == 'Neighborhood') or (pool_type == 'University') or (pool_type== 'Community'):
       pool_typeTF=True
    else:
        return 'Message: pool_type field has invalid value', 400
    
    if len(phone) != 12:
        return 'phone field not in valid format',400
    for i in range(12):
        if i in [3,7]:
            if phone[i] != '-':
                return 'phone field not in valid format',400
        elif not phone[i].isalnum():
            return 'phone field not in valid format',400
    phoneTF=True

    db, username, password, hostname = get_db_creds()
    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password, host=hostname, database=db)
    except Exception as e:
        print(e)

    pools = ("INSERT INTO pools (pool_name, status, phone,pool_type ) VALUES ('%s', '%s', '%s', '%s')"
                % (pool_name, status, phone,pool_type, ))
    check = ("SELECT pool_name FROM pools")

    cur = cnx.cursor()
    cur.execute(check)
    pool_names = [dict(pool_name=row[0]) for row in cur.fetchall()]



 
    if query_data(pool_name) == True:

        return 'Pool with name %s already exists' % pool_name, 400
            
    else:
        cur.execute(pools)
        cnx.commit()
        return "created",201

   


@app.route('/pools/<pool_name>', methods=['GET'])
def search_pool(pool_name):
    #pool_name_parm = request.json('pool_name')
                         

    db, username, password, hostname = get_db_creds()
    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password, host=hostname, database=db)
    except Exception as e:
        print(e)

    action = ("SELECT pool_name, status, phone, pool_type FROM pools WHERE pool_name ='%s'" % pool_name)


    results = None
    cur = cnx.cursor()
    cur.execute(action)
    
    
    
    pool_names = [dict(pool_name=row[0], status=[1], phone=[2], pool_type=[3]) for row in cur.fetchall()] 

    if query_data(pool_name) == True:
          
        cnx.commit()
        return  json.dumps(pool_names),200 #need to fix
            
    else:
        return 'Pool with name %s does not exist' % pool_name,404
    



@app.route('/pools/<pool_name>', methods=['PUT'])
def update_pool(pool_name):
   
    bodypool_name = request.json['pool_name']
    status = request.json['status']
    phone= request.json['phone']
    pool_type = request.json['pool_type']
    if bodypool_name = pool_name:
        return 'Update to pool_name field not allowed', 400
    if (status == 'Closed') or (status == 'Open') or (status== 'in Renovation'):
        statusTF=True
    else:
        return 'Message: status field has invalid value', 400
    if (pool_type == 'Neighborhood') or (pool_type == 'University') or (pool_type== 'Community'):
       pool_typeTF=True
    else:
        return 'Message: pool_type field has invalid value', 400
    
    if len(phone) != 12:
        return 'phone field not in valid format',400
    for i in range(12):
        if i in [3,7]:
            if phone[i] != '-':
                return 'phone field not in valid format',400
        elif not phone[i].isalnum():
            return 'phone field not in valid format',400

    db, username, password, hostname = get_db_creds()
    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password, host=hostname, database=db)
    except Exception as e:
        print(e)
    

    action = ("UPDATE pools SET status='%s', phone='%s', pool_type='%s' WHERE pool_name='%s'"
            % ( status, phone,pool_type,pool_name))
    message = 'pool %s could not be updated' % pool_name

    check = ("SELECT pool_name FROM pools")
    cur = cnx.cursor()
    cur.execute(check)
    pool_names = [dict(pool_name=row[0]) for row in cur.fetchall()]
    cnx.commit()
    if query_data(pool_name) == True:
        cur.execute(action)
        cnx.commit()
        return "Ok", 200 
            
    else:
        return "Pool with name <pool_name> does not exist" % pool_name,404

    

@app.route('/pools/<pool_name>', methods=['DELETE'])
def delete_pool(pool_name):
    
    bodypool_name = request.json['pool_name']
    

    db, username, password, hostname = get_db_creds()
    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password, host=hostname, database=db)
    except Exception as e:
        print(e)

    action = ("DELETE FROM pools WHERE pool_name='%s'" % pool_name)
    message = 'pool %s could not be deleted' % pool_name

    check = ("SELECT pool_name FROM pools")
    cur = cnx.cursor()
    cur.execute(check)
    pool_names = [dict(pool_name=row[0]) for row in cur.fetchall()]

    
    if query_data(pool_name) == True:
        cur.execute(action)
        cnx.commit()
        return "OK",200
            
    else:
        return "pool with pool_name '%s' doesn't exist" % pool_name,404
     
def query_data(pool_name):
    
    
    
    db, username, password, hostname = get_db_creds()
    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password, host=hostname, database=db)
    except Exception as e:
        print(e)

    action = ("SELECT pool_name, status, phone, pool_type FROM pools WHERE pool_name ='%s'" % pool_name)



    results = None
    cur = cnx.cursor()
    cur.execute(action)
    
    
    
   
    pool_names = [dict(pool_name=row[0]) for row in cur.fetchall()]
   


    
    cnx.commit()
    for t in pool_names:
        if t['pool_name'] == pool_name:
            return True
            
        else:
            return False

def hello():
    entries = query_data()

    return entries


if __name__ == "__main__":
    app.debug = True
    create_table()
    app.run(host='0.0.0.0')
