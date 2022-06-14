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
        cur = con.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS similar (id integer PRIMARY KEY AUTO_INCREMENT, distance FLOAT, fileid integer, offeredid integer, FOREIGN KEY(fileid) REFERENCES file(id), FOREIGN KEY(offeredid) REFERENCES file_offered(id))'
        )
        con.commit()
        con2 = mariadb.connect(user='index', password='index', host='192.168.255.9', database='index')
        con3 = mariadb.connect(user='index', password='index', host='192.168.255.9', database='index')
        return con, con2, con3
    except Exception as ex:
        print(ex)


d1 = np.ones((1,25088))
d2 = np.arange(25088)
d2 = d2 % 2
d2 = np.reshape(d2,(1,25088))
d3 = d1 - d2

def distance_triplet(predict):
    dist1 = tf.keras.metrics.CosineSimilarity()(y_true=predict, y_pred=d1)
    dist2 = tf.keras.metrics.CosineSimilarity()(y_true=predict, y_pred=d2)
    dist3 = tf.keras.metrics.CosineSimilarity()(y_true=predict, y_pred=d3)
    distance1 = float(dist1.numpy())
    distance2 = float(dist2.numpy())
    distance3 = float(dist3.numpy())
    return distance1 - 0.001, distance1 + 0.001, \
           distance2 - 0.001, distance2 + 0.001, \
           distance3 - 0.001, distance3 + 0.001


def main(con, con2, con3):

    cur = con.cursor()
    cur.execute('SELECT f.id, f.path, f.name, f.predict, s.offeredid FROM file_offered f LEFT JOIN similar s ON f.id = s.offeredid WHERE predict IS NOT NULL AND s.offeredid IS NULL ORDER BY path, name')

    while True:
        row = cur.fetchone()
        if not row:
            break
        (id, path, name, pred, offeredid) = row
        #print(name + ' ' + path + ' ' + str(offeredid))
        predict = pickle.loads(pred)
        d1l, d1h, d2l, d2h, d3l, d3h = distance_triplet(predict)

        cur2 = con2.cursor()
        #cur2.execute('SELECT id, path, name, predict FROM file_offered WHERE predict IS NOT NULL ORDER BY path, name')
        #cur2.execute('SELECT file.id, file.path, file.name, vgg19.predict FROM file JOIN vgg19 ON file.id = vgg19.id JOIN file_distance d ON file.id = d.id WHERE (d.distance1 BETWEEN ? AND ?) AND (d.distance2 BETWEEN ? AND ?) AND (d.distance3 BETWEEN ? AND ?)',(d1l, d1h, d2l, d2h, d3l, d3h))
        cur2.execute('SELECT file.id, file.path, file.name, vgg19.predict, d.distance1, d.distance2, d.distance3 FROM file JOIN vgg19 ON file.id = vgg19.id JOIN file_distance d ON file.id = d.id WHERE (d.distance1 BETWEEN ? AND ?) AND (d.distance2 BETWEEN ? AND ?) AND (d.distance3 BETWEEN ? AND ?)',(d1l, d1h, d2l, d2h, d3l, d3h))

        while True:
            row2 = cur2.fetchone()
            if not row2:
                break
            (id2, path2, name2, pred2, dd1, dd2, dd3) = row2
            predict2 = pickle.loads(pred2)

            similarity = tf.keras.metrics.CosineSimilarity()(y_true=predict,y_pred=predict2)
            sim = similarity.numpy()
            if sim > 0.5:
                print(str(id) + ' ' + name + ' <=> ' + str(id2) + ' ' + name2 + ' ' + str(sim))
                cur3 = con3.cursor()
                cur3.execute('INSERT IGNORE INTO similar(fileid, offeredid, distance) VALUES(?, ?, ?)',(id2, id, float(sim)))
                con3.commit()
                cur3.close()
        cur2.close()

    cur.close()


con, con2, con3 = initDB()
main(con, con2, con3)