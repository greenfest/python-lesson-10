import sqlite3, os

DATABASE=os.path.join('database.db')      

def connect_db():
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv

def sql_add(con, cortege):
    db = connect_db()
    cur = db.execute(
        """INSERT INTO Questions (ChatID, DateTime, Questions, Seen, Id) VALUES(?, ?, ?, ?, ?)""", cortege)
    db.commit()

def sql_out():
    db = connect_db()
    cur = db.execute("""SELECT ChatID, Id FROM Questions WHERE Seen = 0""")
    rows = cur.fetchall()
    return rows
    
def sql_search(Id):
    db = connect_db()
    cur = db.execute("""SELECT ChatID, DateTime, Questions, Id FROM Questions WHERE Id = ? AND Seen = 0""", (Id,))
    rows = cur.fetchall()
    return rows  

def sql_setRead(Id):
    db = connect_db()
    cur = db.execute(
        """UPDATE Questions SET Seen = 1 WHERE id = ?""", (Id,))
    db.commit() 