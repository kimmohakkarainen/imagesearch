import mariadb
import pickle


def initDB():
    try:
        con1 = mariadb.connect(user='kuvadb', password='kuvadb', host='192.168.255.9', database='kuvadb')
        con2 = mariadb.connect(user='kuvadb', password='kuvadb', host='192.168.255.9', database='kuvadb')
        con3 = mariadb.connect(user='kuvadb', password='kuvadb', host='192.168.255.9', database='kuvadb')
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
        cur.close()

        return con1, con2, con3
    except Exception as ex:
        print(ex)
        raise ex


def select_close_vgg(d1, d2, d3, con):
    d1l = d1 - 0.001
    d2l = d2 - 0.001
    d3l = d3 - 0.001
    d1h = d1 + 0.001
    d2h = d2 + 0.001
    d3h = d3 + 0.001
    cur = con.cursor()
    cur.execute('SELECT v.id, v.predict FROM i_vgg19 v '
                'WHERE '
                '(v.distance1 BETWEEN ? AND ?) AND'
                '(v.distance2 BETWEEN ? AND ?) AND'
                '(v.distance3 BETWEEN ? AND ?)',
                (d1l, d1h, d2l, d2h, d3l, d3h))
    row = cur.fetchone()
    cur.close()
    if row is None:
        return None
    else:
        vgg_id, pred = row
        return vgg_id, pickle.loads(pred)


def select_close_files(d1, d2, d3, con):
    d1l = d1 - 0.001
    d2l = d2 - 0.001
    d3l = d3 - 0.001
    d1h = d1 + 0.001
    d2h = d2 + 0.001
    d3h = d3 + 0.001
    cur = con.cursor()
    cur.execute('SELECT v.id, v.predict, f.path, f.name FROM i_vgg19 v JOIN i_file f '
                'ON v.id = f.vgg_id '
                'WHERE '
                '(v.distance1 BETWEEN ? AND ?) AND'
                '(v.distance2 BETWEEN ? AND ?) AND'
                '(v.distance3 BETWEEN ? AND ?)',
                (d1l, d1h, d2l, d2h, d3l, d3h))
    retval = []
    for row in cur.fetchall():
        idp, predict, path, name = row
        predict = pickle.loads(predict)
        retval.append((idp, predict, path, name))
    cur.close()
    return retval