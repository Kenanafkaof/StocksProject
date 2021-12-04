import sqlite3


# Database structure - 'id' INTEGER | 'name' VARCHAR(255) | 'email' VARCHAR(255)
connection = sqlite3.connect('database.db', check_same_thread=False)
#connection.execute("DROP TABLE stocks;");
try:
    connection.execute('CREATE TABLE stocks (Col1 TEXT, Col2 TEXT, Col3 TEXT, Col4 TEXT)')
except:
    pass
