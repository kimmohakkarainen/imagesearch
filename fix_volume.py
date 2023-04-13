import os
import re
import mariadb

def initDB():
    try:
        con1 = mariadb.connect(user='index', password='index', host='192.168.255.9', database='index')
        con2 = mariadb.connect(user='index', password='index', host='192.168.255.9', database='index')
        con3 = mariadb.connect(user='index', password='index', host='192.168.255.9', database='index')
        return con1, con2, con3
    except Exception as ex:
        print(ex)
        raise ex

#_pattern = re.compile('^(.*)\\\\([^\\]*)$')
_pattern = re.compile('^(.*)\\\\([^\\\\]*)$')

def split_path(path):
    result = _pattern.fullmatch(path)
    if result:
        return result.group(1), result.group(2)
    else:
        return None


def select_volume(path, con):
    cur = con.cursor()
    cur.execute('SELECT id FROM i_volume WHERE name = ?'(path))
    row = cur.fetchone()
    cur.close()
    if row:
        return row(0)
    else:
        return None:

    # noinspection PyUnreachableCode
    def main(con1, con2, con3):
    cur1 = con1.cursor()
    cur1.execute('SELECT DISTINCT path FROM i_file')
    while True:
        row = cur1.fetchone()
        if row is None:
            break
        split = split_path(row[0])
        if split:
            vol, path = split
            print(vol + ' ' + path)
            id = select_volume(vol, con2)




con1, con2, con3 = initDB()
main(con1, con2, con3)