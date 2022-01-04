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
            '''CREATE TABLE IF NOT EXISTS vgg19 (id integer PRIMARY KEY, predict TEXT, FOREIGN KEY(id) REFERENCES file(id))''')
        con.commit()
        return con, con2
    except Exception as ex:
        print(ex)

def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return out.read()

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


def main(con, con2):
    conv_base = keras.applications.vgg19.VGG19(
        weights='imagenet',
        include_top=False,
        input_shape=(224, 224, 3))
    flat1 = tf.keras.layers.Flatten()(conv_base.output)
    # define new model
    model = tf.keras.Model(inputs=conv_base.inputs, outputs=flat1)

    cur = con.cursor()
    cur.execute('SELECT file.id, file.path FROM file LEFT JOIN vgg19 ON file.id = vgg19.id WHERE vgg19.id IS NULL ORDER BY name DESC')
    #list = cur.fetchall()
    #cur.close()

    #for id, path in list:
    while True:
        row = cur.fetchone()
        if not row:
            break
        (id, path) = row
        print(id)
        print(path)
        try:
            image = tf.keras.preprocessing.image.load_img(path, target_size=(224,224))
            input_arr = keras.preprocessing.image.img_to_array(image)
            input_arr = np.array([input_arr])  # Convert single image to a batch.
            predictions = model.predict(input_arr)
            cur2 = con2.cursor()
            cur2.execute('INSERT INTO vgg19(id, predict) VALUES(?, ?)',(id, adapt_array(predictions)))
            con2.commit()
            cur2.close()
        except Exception as exp:
            print(exp)

    cur.close()


con, con2 = initDB()
main(con, con2)