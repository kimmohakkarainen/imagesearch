import io
import os
import mariadb
import tensorflow as tf
import tensorflow.keras as keras
import numpy as np

def initDB():
    try:
        con = mariadb.connect(user='index', password='index', host='192.168.255.9', database='index')
        con2 = mariadb.connect(user='index', password='index', host='192.168.255.9', database='index')
        cur = con.cursor()
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS similarity (id integer PRIMARY KEY, predict TEXT, FOREIGN KEY(id) REFERENCES file(id))''')
        con.commit()
        return con, con2
    except Exception as ex:
        print(ex)

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)
