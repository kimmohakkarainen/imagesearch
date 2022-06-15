import os
import mariadb
import tensorflow as tf
import tensorflow.keras as keras
import numpy as np

def initDB():
    try:
        con1 = mariadb.connect(user='index', password='index', host='192.168.255.9', database='index')
        con2 = mariadb.connect(user='index', password='index', host='192.168.255.9', database='index')
        con3 = mariadb.connect(user='index', password='index', host='192.168.255.9', database='index')
        cur = con1.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS i_volume(id integer PRIMARY KEY AUTO_INCREMENT, name char(255), comment text, UNIQUE(name))')
        cur.execute(
            'CREATE TABLE IF NOT EXISTS '
            'i_vgg19('
            'id integer PRIMARY KEY AUTO_INCREMENT, '
            'predict MEDIUMBLOB,'
            'distance1 FLOAT,'
            'distance2 FLOAT,'
            'distance3 FLOAT)')

        cur.execute(
            'CREATE TABLE IF NOT EXISTS '
            'i_file('
            'id integer PRIMARY KEY AUTO_INCREMENT, '
            'path char(255), '
            'name char(255), '
            'vol_id integer, '
            'vgg_id integer, '
            'FOREIGN KEY(vol_id) REFERENCES i_volume(id), '
            'FOREIGN KEY(vgg_id) REFERENCES i_vgg19(id), '
            'UNIQUE(path, name))')
        cur.execute(
            'CREATE TABLE IF NOT EXISTS '
            'i_error('
            'id integer PRIMARY KEY,'
            'error TEXT,'
            'FOREIGN KEY(id) REFERENCES i_file(id))'
        )
        con1.commit()
        cur.close

        return con1, con2, con3
    except Exception as ex:
        print(ex)
        raise ex


def insert_file(path, name, con):
    cur = con.cursor()
    cur.execute('INSERT IGNORE INTO i_file(path,name) VALUES(?,?)', (path,name))
    con.commit()
    cur.close


def select_files_without_vgg19(con):
    cur = con.cursor()
    cur.execute('SELECT f.id, f.path, f.name FROM i_file f LEFT JOIN i_error e ON f.id = e.id WHERE f.vgg_id IS NULL AND e.id IS NULL')
    return cur


def select_errors_for_migration(con):
    cur = con.cursor()
    cur.execute('SELECT f.id, f.path, f.name FROM file f JOIN error e ON f.id = e.id')
    return cur


def select_vgg19s_for_migration(con):
    cur = con.cursor()
    cur.execute('SELECT f.id, f.path, f.name FROM file f JOIN error e ON f.id = e.id')
    return cur



def select_close_vgg(d1, d2, d3, con):
    d1l = d1 - 0.001
    d2l = d2 - 0.001
    d3l = d3 - 0.001
    d1h = d1 + 0.001
    d2h = d2 + 0.001
    d3h = d3 + 0.001
    cur = con.cursor()
    cur.execute('SELECT v.id FROM i_vgg19 v '
                'WHERE '
                '(v.distance1 BETWEEN ? AND ?) AND'
                '(v.distance2 BETWEEN ? AND ?) AND'
                '(v.distance3 BETWEEN ? AND ?)',
                (d1l, d1h, d2l, d2h, d3l, d3h))
    row = cur.fetchone()
    cur.close()
    if row is None:
        return row
    else:
        return (row,)


def insert_vgg19(vgg19, d1, d2, d3, con):
    cur = con.cursor()
    cur.execute('INSERT INTO i_vgg19(predict, distance1, distance2, distance3) VALUES(?,?,?,?)',(vgg19.dumps(), d1, d2, d3))
    con.commit()
    id = cur.lastrowid
    cur.close()
    return id


def update_file_vggid(id, vggid,con):
    cur = con.cursor()
    cur.execute('UPDATE i_file SET vgg_id = ? WHERE id = ?', (vggid, id))
    con.commit()
    cur.close()


def insert_error(id, error, con):
    cur = con.cursor()
    cur.execute('INSERT INTO i_error(id, error) VALUES(?, ?)',(id,str(error)))
    con.commit()
    cur.close()

'''
GLOBAL
'''
conv_base = keras.applications.vgg19.VGG19(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3))
flat1 = tf.keras.layers.Flatten()(conv_base.output)
# define new model
model = tf.keras.Model(inputs=conv_base.inputs, outputs=flat1)

d1 = np.ones((1,25088))
d2 = np.arange(25088)
d2 = d2 % 2
d2 = np.reshape(d2,(1,25088))
d3 = d1 - d2


def calc_distance3(predict):
    dist1 = tf.keras.metrics.CosineSimilarity()(y_true=predict, y_pred=d1)
    dist2 = tf.keras.metrics.CosineSimilarity()(y_true=predict, y_pred=d2)
    dist3 = tf.keras.metrics.CosineSimilarity()(y_true=predict, y_pred=d3)
    distance1 = float(dist1.numpy())
    distance2 = float(dist2.numpy())
    distance3 = float(dist3.numpy())
    return predict, distance1, distance2, distance3


def vgg19_distance(filepath):
    image = tf.keras.preprocessing.image.load_img(filepath)
    try:
        image = image.resize((224,224))
    except:
        image = image.resize((224,224), box=(0, 0, image.width, image.height))
    input_arr = keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])  # Convert single image to a batch.
    predict = model.predict(input_arr)
    return calc_distance3(predict)



def import_file_names(path, con1, con2, con3):
    for file in os.scandir(path):
        if file.is_dir():
            import_file_names(file.path, con1, con2, con3)
        else:
            insert_file(path,file.name,con1)


def calculate_vgg19(con1, con2, con3):
    cur1 = select_files_without_vgg19(con1)
    while True:
        row1 = cur1.fetchone()
        if not row1:
            break
        (id, path, name) = row1
        filepath = path + '\\' + name
        try:
            vgg19, d1, d2, d3 = vgg19_distance(filepath)
            vgg_id = select_close_vgg(d1, d2, d3,con2)
            if vgg_id is None:
                vgg_id = insert_vgg19(vgg19, d1, d2, d3, con2)
            update_file_vggid(id,vgg_id, con2)
        except Exception as exp:
            insert_error(id, exp, con2)

    cur1.close()


def migrate_errors(con1, con2, con3):
    cur1 = select_errors_for_migration(con1)
    pass


def migrate_vgg19(con1, con2, con3):
    pass



'''
    main routine
'''

def main(path, con1, con2, con3):
    import_file_names(path, con1, con2, con3)
    calculate_vgg19(con1, con2, con3)


def migrate(con1, con2, con3):
    migrate_errors(con1, con2, con3)
    migrate_vgg19(con1, con2, con3)



con1, con2, con3 = initDB()
#main('\\\\192.168.255.9\\tempimg\\DCIM', con1, con2, con3)
migrate(con1, con2, con3)


