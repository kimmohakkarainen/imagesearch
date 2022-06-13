import os
import mariadb

def initDB():
    try:
        con = mariadb.connect(user='index', password='index', host='192.168.255.9', database='index')
        cur = con.cursor()
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS file (id integer PRIMARY KEY AUTO_INCREMENT, path char(255), name char(255), unique(path,name)) ''')
        # cur.execute('''CREATE TABLE IF NOT EXISTS file (id integer PRIMARY KEY, path text UNIQUE, name text) WITHOUT ROWID''')
        con.commit()
        return con
    except Exception as ex:
        print(ex)

def recurse(con, basepath):

    for file in os.scandir(basepath):
        if file.is_dir():
            recurse(con,file.path)
        else:
            try:
                cur = con.cursor()
                #cur.execute("INSERT IGNORE INTO file (path, name)  VALUES (?,?)",(file.path, file.name))
                cur.execute("INSERT IGNORE INTO file (path, name)  VALUES (?,?)",(basepath, file.name))
                con.commit()
                cur.close()
            except Exception as exp:
                #pass
                print(exp)



basepath='\\\\192.168.255.9\\tempimg'

con = initDB()

recurse(con, basepath)

con.close()