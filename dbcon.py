import sqlite3

def initDB():
    con = sqlite3.connect('imagefiles.db')
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS file (id integer PRIMARY KEY AUTOINCREMENT, path text UNIQUE, name text)')
    cur.execute('CREATE TABLE IF NOT EXISTS vgg19 (id INTEGER PRIMARY KEY, predict array, FOREIGN KEY(id) REFERENCES file(id)) WITHOUT ROWID')
    cur.execute('CREATE TABLE IF NOT EXISTS similarity (id INTEGER PRIMARY KEY AUTOINCREMENT, vid1 INTEGER, vid2 INTEGER, similarity, FOREIGN KEY(vid1) REFERENCES file(id), FOREIGN KEY(vid2) REFERENCES file(id), UNIQUE(vid1, vid2))')
    con.commit()
    return con
