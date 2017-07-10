import sqlite3
import datetime

CONN = sqlite3.connect('b.db')
C = CONN.cursor()

# # Create table
# c.execute("CREATE TABLE events (date text, desc text, created_by text)")

# # Insert a row of data
# c.execute("INSERT INTO events VALUES ('2017-04-25','This event will have pizza','Michael F')")

# # Save (commit) the changes
# conn.commit()
date = datetime.date.today()
sql_statement = "INSERT INTO events VALUES ('" + date.strftime('%Y/%m/%d') + "', 'This event will not have pizza', 'Michael F')"
C.execute(sql_statement)

for row in C.execute('SELECT * FROM events'):
        print row

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
CONN.commit()
CONN.close()