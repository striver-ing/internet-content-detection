import sqlite3

conn = sqlite3.connect('test.db')
c = conn.cursor()
c.execute('''CREATE TABLE TAB_IOPM_MAX_ID
       (ID INT PRIMARY KEY     NOT NULL,
       NAME CHAR(50)    NOT NULL,
       max_id INT     NOT NULL
       ''')
print ("Table created successfully")
conn.commit()
conn.close()