from flask import Flask, render_template,request, redirect,request,session
import csv, pymysql,re,math
from helper import stockPrice,passHash,removePunc, sellList, buyList,buildList
from helper import getUsername
from passlib.hash import pbkdf2_sha256


app=Flask(__name__)

class User():
    def __init__(self,username,password):
        self.username=username
        self.password=password
        self.cash=10000

connect=pymysql.connect(host='localhost',user='root',db='cs50')

@app.route("/")
def login():

    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/logout")
def logout():
    connection=connect
    cursor=connection.cursor()
    sql="SELECT username FROM register WHERE logged=1"
    cursor.execute(sql)
    username=removePunc(cursor)[0]
    print(username)
    sql="UPDATE register SET logged=0"

    cursor.execute(sql)
    connection.commit()

    return render_template("login.html")


@app.route("/registered",methods=["post"] )
def registered():
    connection=connect
    cursor=connection.cursor()
    sql="SELECT username FROM register"
    cursor.execute(sql)
    userList=removePunc(cursor)

    username=request.form['username']

    if username in userList:
        return render_template("failure.html")
    #Declare username and password
    if request.form['password']==request.form['password2']:
        password=request.form['password']
        password=passHash(password)


        sql="INSERT INTO register(username,password) VALUES('{0}','{1}')".format(username,password)

        cursor.execute(sql)
    else:
        return render_template("failure.html")

    username=request.form['username']
    columns="pid INT PRIMARY KEY NOT NULL AUTO_INCREMENT,username TEXT,symbol TEXT,quantity INT,price FLOAT,remaining INT"
    sql="CREATE TABLE {0}({1})".format(username,columns)
    cursor.execute(sql)
    sql="INSERT INTO {0}(remaining) VALUES (10000)".format(username)
    cursor.execute(sql)
    columns="sid INT PRIMARY KEY NOT NULL AUTO_INCREMENT,symbol TEXT, quantity INT"
    sql="CREATE TABLE {0}({1})".format(username+"Portfolio",columns)
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    connection.close()
    return render_template("login.html")

#LOGIN
@app.route("/verify",methods=["post"])
def verify():
    fail=0
    #CONNECT TO SERVER
    connection=pymysql.connect(host='localhost',user='root',db='cs50')
    uCursor=connection.cursor()
    pCursor=connection.cursor()


    #Grab variables from POST
    username=request.form["username"]
    password=request.form["password"]


    #Grab list of usernames and pwds from DB
    p="SELECT password FROM register"
    u="SELECT username FROM register"
    uCursor.execute(u)
    pCursor.execute(p)
    uResults=removePunc(uCursor)
    pResults=removePunc(pCursor)

    #Find username
    count=0
    for i in range(len(uResults)):
        if username==uResults[i]:
            count=i

    cursor=connection.cursor()
    sql="UPDATE register SET logged=1 WHERE username='{0}'".format(username)
    cursor.execute(sql)

    sql="SELECT remaining FROM {0}".format(username)
    mcursor=connection.cursor()
    mcursor.execute(sql)

    temp=removePunc(mcursor)
    #Set logged to 1
    connection.commit()
    funds=temp[-1]
    print(funds)

    #Make stock table
    sql="SELECT DISTINCT symbol FROM {0} WHERE quantity>0".format(username)
    cursor.execute(sql)
    stockList=buildList(username)
    if pbkdf2_sha256.verify(password,pResults[i]):
        return render_template("home.html",total=0,user=username,cash=funds,stockList=stockList)
    else:
        return render_template("login.html",fail=1)


@app.route("/purchase",methods=['post'])
def purchase():
    connection=connect
    symbol=request.form['symbol']
    if request.form['quantity']:
        quantity=request.form['quantity']
    else:
        quantity=0


    #Check for valid symbol
    if len(symbol)>4:
        return render_template("failure.html")
    if not symbol.isalpha():
        return render_template("failure.html")

    which=request.form['submit']

    cursor=connection.cursor()
    username=getUsername()

    stockList=buildList(username)


    #Buys Stock
    sql="SELECT remaining FROM {0}".format(username)

    cursor.execute(sql)
    remaining=removePunc(cursor)[-1]
    remaining=float(remaining)

    #Finds price of stock
    price=float(stockPrice(symbol))
    final=float(quantity)*price
    final=round(final,2)
    quantity=int(quantity)
    print("FINAL IS {0}".format(final))
    count=0


    #Logs Stock Purchase actionin SQL
    if which=="BUY":
        cols="username,symbol,quantity,price,remaining"
        remaining=remaining-final

        if remaining<0:
            count=-1
            remaining=remaining+final
            return render_template ("home.html",count=count,total=final,user=username,cash=remaining,stockList=stockList)

        sql="INSERT INTO {0}({6}) VALUES ('{1}','{2}','{3}','{4}','{5}')".format(username,username,symbol,quantity,price,remaining,cols)
        cursor.execute(sql)


        #Buids stocklist
        buyList(username,symbol,quantity)
        stockList=buildList(username)
        connection.commit()
        print("Building stocklist")
        return render_template ("home.html",count=count,total=final,user=username,cash=remaining,stockList=stockList)

    elif which=="QUOTE":

        return render_template("home.html",count=1,total=price,user=username,cash=remaining,stockList=stockList)

    elif which=="SELL":
        test=-1*quantity
        remaining=remaining+final
        cols="username,symbol,quantity,price,remaining"
        sql="INSERT INTO {0}({6}) VALUES ('{1}','{2}','{3}','{4}','{5}')".format(username,username,symbol,test,price,remaining,cols)
        cursor.execute(sql)
        sellList(username,symbol,quantity)
        stockList=buildList(username)
        connection.commit()


        return render_template("home.html",count=0,total=final,user=username,cash=remaining,stockList=stockList)


#@app.route("\quote",methods=['post'])





"""
@app.route("/settle",methods=["POST"])
def settle():
    name=request.form["name"]
    aapl=request.form["AAPL"]
    goog=request.form["GOOG"]
    fb=request.form["FB"]
    file=open("input.csv","a")
    writer=csv.writer(file)
    writer.writerow((name,aapl,goog,fb))

    file.close()
    print("done")
    return  render_template("success.html")
"""
if __name__=="__main__":
    app.run()
