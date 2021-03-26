import io
import sqlite3
import tensorflow as tf
import tensorflow.keras as keras
import numpy as np

# https://stackoverflow.com/questions/18621513/python-insert-numpy-array-into-sqlite3-database
def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


# Converts np.array to TEXT when inserting
sqlite3.register_adapter(np.ndarray, adapt_array)

# Converts TEXT to np.array when selecting
sqlite3.register_converter("array", convert_array)


con = sqlite3.connect('imagefiles.db', detect_types=sqlite3.PARSE_DECLTYPES)
cur = con.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS vgg19 (id INTEGER PRIMARY KEY, predict array, FOREIGN KEY(id) REFERENCES file(id)) WITHOUT ROWID')
#cur.execute('DROP TABLE vgg19')
#cur.execute('CREATE TABLE vgg19 (id INTEGER PRIMARY KEY, predict array, FOREIGN KEY(id) REFERENCES file(id)) WITHOUT ROWID')
con.commit()

conv_base = keras.applications.vgg19.VGG19(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3))
flat1 = tf.keras.layers.Flatten()(conv_base.output)
# define new model
model = tf.keras.Model(inputs=conv_base.inputs, outputs=flat1)

cur.execute('SELECT file.id,path FROM file LEFT JOIN vgg19 ON file.id = vgg19.id WHERE vgg19.id IS NULL ORDER BY name DESC')
list = cur.fetchall()
cur.close()

for id, path in list:
    print(path)
    try:
        image = tf.keras.preprocessing.image.load_img(path, target_size=(224,224))
        input_arr = keras.preprocessing.image.img_to_array(image)
        input_arr = np.array([input_arr])  # Convert single image to a batch.
        predictions = model.predict(input_arr)
        cur = con.cursor()
        cur.execute('INSERT INTO vgg19 VALUES(?, ?)',(id, predictions))
        con.commit()
        cur.close()
    except Exception as exp:
        print(exp)
