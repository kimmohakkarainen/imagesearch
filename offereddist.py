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
        return con, con2
    except Exception as ex:
        print(ex)


def convert_array(text):
    out = io.BytesIO(text.encode('utf-8'))
    out.seek(0)
    return np.load(out,allow_pickle=False, encoding='bytes')


def main(con, con2):

    cur = con.cursor()
    cur.execute('SELECT file.id, file.path, file.name, vgg19.predict FROM file JOIN vgg19 ON file.id = vgg19.id ORDER BY name DESC')

    while True:
        row = cur.fetchone()
        if not row:
            break
        (id, path, name, pred) = row
        predict1 = pickle.loads(pred)
        #predict1 = convert_array(pred)

        cur2 = con2.cursor()
        cur2.execute('SELECT id, path, name, predict FROM file_offered')

        while True:
            row2 = cur2.fetchone()
            if not row2:
                break
            (id2, path2, name2, pred2) = row2
            #predict2 = convert_array(pred2)
            predict2 = pickle.loads(pred2)

            similarity = tf.keras.metrics.CosineSimilarity()(y_true=predict1,y_pred=predict2)
            sim = similarity.
            print(name + ' <=> ' + name2 + ' ' + str(sim))
        cur2.close()

    cur.close()


con, con2 = initDB()
main(con, con2)