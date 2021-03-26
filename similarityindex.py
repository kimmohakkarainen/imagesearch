import io
import sqlite3
import numpy as np
import random

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
#cur.execute('DROP TABLE similarity')
cur.execute('CREATE TABLE IF NOT EXISTS similarity (id INTEGER PRIMARY KEY AUTOINCREMENT, vid1 INTEGER, vid2 INTEGER, similarity, FOREIGN KEY(vid1) REFERENCES file(id), FOREIGN KEY(vid2) REFERENCES file(id), UNIQUE(vid1, vid2))')

cur.execute('SELECT MIN(id), MAX(id) FROM vgg19')
min, max = cur.fetchone()
cur.close()
print((min,max))

import tensorflow as tf

random.seed()

cur = con.cursor()
cur.execute('SELECT id, predict FROM vgg19')
fulllist = cur.fetchall()
cur.close()

for i in range(100000):
    index1 = random.randrange(len(fulllist))
    index2 = random.randrange(len(fulllist))
    id1, predict1 = fulllist[index1]
    id2, predict2 = fulllist[index2]

    vid1 = id1 if id1 < id2 else id2
    vid2 = id2 if id1 < id2 else id1

    cur = con.cursor()
    cur.execute('SELECT id, vid1, vid2 FROM similarity WHERE vid1 = ? AND vid2 = ?', (vid1, vid2))
    if cur.fetchone():
        print(str(vid1) + '  ' + str(vid2) + ' EXISTS')
        cur.close()
    else:
        similarity = tf.keras.metrics.CosineSimilarity()(y_true=predict1,y_pred=predict2)
        #print(str(vid1) + '  ' + str(vid2) + '  ' + str(similarity))
        cur.execute('INSERT INTO similarity VALUES(?,?,?,?)', (None, vid1, vid2, float(similarity)))
        con.commit()
        cur.close()



'''
for i in range(10000):

    index1 = random.randrange(min,max)
    cur = con.cursor()
    cur.execute('SELECT file.id, path, name, predict FROM vgg19 JOIN FILE ON vgg19.id = file.id WHERE vgg19.id <= ? ORDER BY vgg19.id DESC', (index1,))
    id1, path1, name1, predict1 = cur.fetchone()
    #print((index1, id1, path1, name1))

    index2 = random.randrange(min,max)
    cur.execute('SELECT file.id, path, name, predict FROM vgg19 JOIN FILE ON vgg19.id = file.id  WHERE vgg19.id >= ? ORDER BY vgg19.id ASC', (index2,))
    id2, path2, name2, predict2 = cur.fetchone()
    #print((index2, id2, path2, name2))

    vid1 = id1 if id1 < id2 else id2
    vid2 = id2 if id1 < id2 else id1

    cur.execute('SELECT id, vid1, vid2 FROM similarity WHERE vid1 = ? AND vid2 = ?', (vid1, vid2))
    if cur.fetchone():
        print(str(vid1) + '  ' + str(vid2) + ' EXISTS')
        cur.close()
    else:
        similarity = tf.keras.metrics.CosineSimilarity()(y_true=predict1,y_pred=predict2)
        print(str(vid1) + '  ' + str(vid2) + '  ' + str(similarity))
        cur.execute('INSERT INTO similarity VALUES(?,?,?,?)', (None, vid1, vid2, float(similarity)))
        con.commit()
        cur.close()
'''