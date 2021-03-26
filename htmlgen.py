import io
import os
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

#index_to_search = 34119
index_to_search = 253341

images = dict()

with open('index.html','w') as output:
    output.writelines(['<html><body><table><thead><tr><td/><td/><td/></thead><tbody>'])
    cur = con.cursor()
    for row in cur.execute('SELECT s.similarity, f1.id, f2.id, f1.name, f2.name, f1.path, f2.path FROM similarity s JOIN file f1 on s.vid1 = f1.id JOIN file f2 ON s.vid2 = f2.id where (s.vid1 = ? or s.vid2 = ?) AND s.similarity > 0.3 ORDER BY s.similarity DESC',(index_to_search,index_to_search)):
        similarity, id1, id2, name1, name2, path1, path2 = row
        print(row)
        if id1 == index_to_search:
            filename = 'thumbnails/img-'+str(id2) + '.jpg'
            output.writelines(['<tr><th>' + str(similarity) + '</th>',
                               '<th><a href="' + path2 + '">' + name2 + '</a></th>',
                               '<th><img src="' + filename + '"></img></th></tr>'])
            images[id2] = (id2, path2, filename)
        else:
            filename = 'thumbnails/img-'+str(id1) + '.jpg'
            output.writelines(['<tr><th>' + str(similarity) + '</th>',
                               '<th><a href="' + path1 + '">' + name1 + '</a></th>',
                               '<th><img src="' + filename + '"></img></th></tr>'])
            images[id1] = (id1, path1, filename)
    con.commit()
    cur.close()
    output.writelines(['</tbody></table></body></html>'])

from PIL import Image

if not os.path.exists('thumbnails'):
    os.makedirs('thumbnails')

for id, path, filename in images.values():
    #filename = 'thumbnails/img-'+str(id) + '.jpg'
    if not os.path.exists(filename):
        im = Image.open(path)
        rgb_im = im.convert('RGB')
        rgb_im.thumbnail((128,128))
        rgb_im.save(filename, "JPEG")