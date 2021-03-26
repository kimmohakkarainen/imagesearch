import os
import io
import sqlite3

def initDB():
    con = sqlite3.connect('imagefiles.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS file (id integer PRIMARY KEY AUTOINCREMENT, path text UNIQUE, name text)''')
    #cur.execute('''CREATE TABLE IF NOT EXISTS file (id integer PRIMARY KEY, path text UNIQUE, name text) WITHOUT ROWID''')
    con.commit()
    return con

def recurse(con, basepath):

    for file in os.scandir(basepath):
        if file.is_dir():
            recurse(con,file.path)
        else:
            try:
                cur = con.cursor()
                cur.execute("INSERT OR IGNORE INTO file VALUES (?,?,?)",(None, file.path, file.name))
                con.commit()
                cur.close()
            except Exception as exp:
                pass
                #print(exp)



basepath='\\\\192.168.255.11\\material'

con = initDB()

recurse(con, basepath)

con.close()