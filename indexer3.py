import io
import os
import mariadb
import tensorflow as tf
import tensorflow.keras as keras
import numpy as np
import pickle

def initDB():
    try:
        con = mariadb.connect(user='index', password='index', host='192.168.255.9', database='index')
        con2 = mariadb.connect(user='index', password='index', host='192.168.255.9', database='index')
        cur = con.cursor()
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS file_distance (id integer PRIMARY KEY, distance1 FLOAT, distance2 FLOAT, distance3 FLOAT, FOREIGN KEY(id) REFERENCES file(id))''')
        con.commit()
        return con, con2
    except Exception as ex:
        print(ex)

def main(con, con2):
    cur = con.cursor()
    cur.execute('SELECT file.id, vgg19.predict, file_distance.id FROM file JOIN vgg19 ON file.id = vgg19.id LEFT JOIN file_distance ON file.id = file_distance.id WHERE file_distance.id IS NULL')

    d1 = np.ones((1,25088))
    d2 = np.arange(25088)
    d2 = d2 % 2
    d2 = np.reshape(d2,(1,25088))
    d3 = d1 - d2

    while True:
        row = cur.fetchone()
        if not row:
            break;
        (id, predict, fid) = row
        predict1 = pickle.loads(predict)
        dist1 = tf.keras.metrics.CosineSimilarity()(y_true=predict1, y_pred=d1)
        dist2 = tf.keras.metrics.CosineSimilarity()(y_true=predict1, y_pred=d2)
        dist3 = tf.keras.metrics.CosineSimilarity()(y_true=predict1, y_pred=d3)
        distance1 = float(dist1.numpy())
        distance2 = float(dist2.numpy())
        distance3 = float(dist3.numpy())
        cur2 = con2.cursor()
        cur2.execute('INSERT INTO file_distance(id, distance1, distance2, distance3) VALUES(?,?,?,?)',
                     (id, distance1, distance2, distance3))
        con2.commit()
        cur2.close()
    cur.close()

con, con2 = initDB()
main(con, con2)