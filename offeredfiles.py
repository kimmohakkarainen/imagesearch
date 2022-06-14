import io
import os
import mariadb
import tensorflow as tf
import tensorflow.keras as keras
import numpy as np

def initDB():
    try:
        con = mariadb.connect(user='index', password='index', host='192.168.255.9', database='index')
        cur = con.cursor()
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS file_offered (id integer PRIMARY KEY AUTO_INCREMENT, path char(255), name char(255), error TEXT, predict MEDIUMBLOB, unique(path,name)) ''')
        con.commit()
        return con
    except Exception as ex:
        print(ex)

'''
def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return out.read()
'''

def recurse(con, basepath):

    conv_base = keras.applications.vgg19.VGG19(
        weights='imagenet',
        include_top=False,
        input_shape=(224, 224, 3))
    flat1 = tf.keras.layers.Flatten()(conv_base.output)
    model = tf.keras.Model(inputs=conv_base.inputs, outputs=flat1)

    for file in os.scandir(basepath):
        if file.is_dir():
            recurse(con,file.path)
        else:
            cur = con.cursor()
            cur.execute('SELECT path, name FROM file_offered WHERE path = ? AND name = ?', (basepath, file.name))
            if cur.fetchone():
                pass
                #print(basepath + '\\' + file.name + ' EXISTS')
            else:
                try:
                    #image = tf.keras.preprocessing.image.load_img(file.path, target_size=(224,224))
                    image = tf.keras.preprocessing.image.load_img(file.path)
                    try:
                        image = image.resize((224,224))
                    except:
                        image = image.resize((224,224), box=(0, 0, image.width, image.height))
                    input_arr = keras.preprocessing.image.img_to_array(image)
                    input_arr = np.array([input_arr])  # Convert single image to a batch.
                    predictions = model.predict(input_arr)
                    cur.execute('INSERT INTO file_offered(path, name, predict) VALUES(?, ?, ?)',(basepath, file.name, predictions.dumps()))
                except Exception as exp:
                    #print(exp)
                    cur.execute('INSERT INTO file_offered(path, name, error) VALUES(?, ?, ?)', (basepath, file.name, str(exp)))
                con.commit()
            cur.close()


#basepath='\\\\192.168.255.9\\incoming\\kimmo\\OpenShare\\60dparhaat'

con = initDB()

#recurse(con, '\\\\192.168.255.9\\incoming\\kimmo\\OpenShare\\canon60d\\20130331')
#recurse(con, '\\\\192.168.255.9\\incoming\\kimmo\\OpenShare\\canon60d\\20160228-dubai')
recurse(con, '\\Users\\KimmoHakkarainen\\OneDrive - Exadeci Oy\\DCIM')

con.close()