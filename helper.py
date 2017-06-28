from passlib.hash import pbkdf2_sha256
import pymysql,re,bs4,requests

connect=pymysql.connect(host='localhost',user='root',db='cs50')

def passHash(password):
    #Generate new salt and hash password
    hash=pbkdf2_sha256.hash(password)

    return hash

def stockPrice(symbol):
    res=requests.get("https://finance.yahoo.com/quote/{}".format(symbol))
    soup=bs4.BeautifulSoup(res.text,"html.parser")
    getRow=soup.select('.Ta(end)')



    try:
        bid=float(getRow[1].getText())
        ask=float(getRow[2].getText())
        final=bid+ask
        final=final/2
        return final
    except ValueError:
        print("Not valid symbol")
        return 1


def removePunc(cursor):
    results=cursor.fetchall()
    if type(results)!="list":
        results=list(results)
    for i in range(len(results)):
        results[i]=str(results[i])
        results[i]=results[i].replace("'","").replace(",","")
        results[i]=results[i].replace("(","").replace(")","")

    return(results)

def buyList(username,symbol,quantity):
    sql="SELECT quantity FROM {0}Portfolio WHERE symbol='{1}'".format(username,symbol)
    connect=pymysql.connect(host='localhost',user='root',db='cs50')
    connection=connect
    cursor=connection.cursor()
    cursor.execute(sql)
    temp=removePunc(cursor)
    length=len(temp)

    print("LENGTH IS {0}".format(length))
    print(type(length))
    if (length==0):
        sql="INSERT INTO {0}Portfolio(symbol,quantity) VALUES ('{1}',{2})".format(username,symbol,quantity)
        cursor.execute(sql)

    elif (length==1):
        stuff=int(temp[0])
        temp=stuff+quantity
        sql="UPDATE {0}Portfolio SET quantity={1} WHERE symbol='{2}'".format(username,temp,symbol)
        cursor.execute(sql)

    connection.commit()

    return 0

def sellList(username,symbol,quantity):
    sql="SELECT quantity FROM {0}Portfolio WHERE symbol='{1}'".format(username,symbol)
    connect=pymysql.connect(host='localhost',user='root',db='cs50')
    connection=connect
    cursor=connection.cursor()
    cursor.execute(sql)
    temp=removePunc(cursor)
    length=len(temp)

    if length==0:
        return -1
    elif length==1:
        stuff=int(temp[0])
        temp=stuff-quantity
        if temp<0:
            print("Not enough stock")
            return -1

        sql="UPDATE {0}Portfolio SET quantity={1} WHERE SYMBOL='{2}'".format(username,temp,symbol)
        cursor.execute(sql)

    connection.commit()
    return 0


def buildList(username):
    connect=pymysql.connect(host='localhost',user='root',db='cs50')
    cursor=connect.cursor()
    sql="SELECT symbol FROM {0}Portfolio WHERE quantity>0".format(username)
    cursor.execute(sql)
    stocks=removePunc(cursor)
    sql="SELECT quantity FROM {0}Portfolio WHERE quantity>0".format(username)
    cursor.execute(sql)
    amounts=removePunc(cursor)

    stockList=[]

    for i in range(len(stocks)):
        stockList.append([stocks[i],amounts[i]])

    return stockList


def getUsername():
    connection=connect
    cursor=connection.cursor()

    sql="SELECT username FROM register WHERE logged=1"
    cursor.execute(sql)
    username=removePunc(cursor)[0]
    return username
