import io
import sqlite3
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
#cur = con.cursor()

queries = [
    'SELECT MIN(id), MAX(id), COUNT(*) FROM file',
    'SELECT MIN(id), MAX(id), COUNT(*) FROM vgg19',
    'SELECT MIN(vid1), MAX(vid1), MIN(vid2), MAX(vid2), MIN(similarity), MAX(similarity), COUNT(*) FROM similarity',
    'SELECT COUNT(*) FROM similarity WHERE similarity < 0.01',
    #'SELECT s.similarity, f1.id, f2.id, f1.name, f2.name, f1.path, f2.path FROM similarity s JOIN file f1 on s.vid1 = f1.id JOIN file f2 ON s.vid2 = f2.id where s.similarity < 0.01 AND s.similarity > 0',
    'SELECT s.similarity, f1.id, f2.id, f1.name, f2.name, f1.path, f2.path FROM similarity s JOIN file f1 on s.vid1 = f1.id JOIN file f2 ON s.vid2 = f2.id where (s.vid1 = 34119 or s.vid2 = 34119) AND s.similarity > 0.5'
    #'SELECT * FROM vgg19 JOIN file on vgg19.id = file.id',
    #'SELECT count(*) FROM vgg19 JOIN file on vgg19.id = file.id',
    #'SELECT path,name FROM file WHERE name like "IMG%" ORDER BY name',
    #'SELECT count(*) FROM file WHERE name like "IMG%" ORDER BY name',
    #'SELECT count(*) FROM file'

    # remove unnecessary lines
    #"DELETE FROM similarity WHERE vid2 IN (SELECT id FROM file WHERE path LIKE '%material\\recycle%')",
    #"DELETE FROM vgg19 WHERE id IN (SELECT id FROM file WHERE path LIKE '%material\\recycle%')",
    #"SELECT * FROM file f JOIN vgg19 on f.id = vgg19.id JOIN similarity s ON f.id = s.vid1 WHERE path LIKE '%material\\recycle%'",
    #"SELECT * FROM file f JOIN vgg19 on f.id = vgg19.id JOIN similarity s ON f.id = s.vid2 WHERE path LIKE '%material\\recycle%'",
    #"SELECT * FROM file f JOIN vgg19 on f.id = vgg19.id WHERE path LIKE '%material\\recycle%'",
]

for query in queries:
    cur = con.cursor()
    for row in cur.execute(query):
        print(row)
    con.commit()
    cur.close()
