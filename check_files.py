from os import scandir
import tensorflow as tf
import keras
import numpy as np
from mariadbcon import initDB, select_close_vgg, select_close_files
from util import isImageFile


con1, con2, con3 = initDB()
conv_base = tf.keras.applications.vgg19.VGG19(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3))
flat1 = tf.keras.layers.Flatten()(conv_base.output)
# define new model
model = tf.keras.Model(inputs=conv_base.inputs, outputs=flat1)

d1 = np.ones((1, 25088))
d2 = np.arange(25088)
d2 = d2 % 2
d2 = np.reshape(d2, (1, 25088))
d3 = d1 - d2






def main(path, con1, con2, con3):
    for file in scandir(path):
        if file.is_dir():
            main(file.path, con1, con2, con3)
        elif isImageFile(file.name):
            try:
                predict, dist1, dist2, dist3 = vgg19_distance(file.path)
                close_files = select_close_files(dist1, dist2, dist3, con1)
                #if len(close_files) == 0:
                #    print(' '.join(['No similar image exists for ', str(file.path)]))
                #else:
                maxsim = 0
                found = False
                for row in close_files:
                    id2, pred2, path2, name2 = row
                    similarity = tf.keras.metrics.CosineSimilarity()(y_true=predict, y_pred=pred2)
                    sim = similarity.numpy()
                    maxsim = sim if sim > maxsim else maxsim
                    if sim >= 0.99:
                        found = True
                        #print(' '.join([file.path,' == ', path2, name2]))
                if not found:
                    print(' '.join(['!!!', 'max similarity', str(maxsim), str(file.path)]))
            except Exception as exp:
                print(str(file.path), str(exp))


def calc_distance3(predict):
    dist1 = tf.keras.metrics.CosineSimilarity()(y_true=predict, y_pred=d1)
    dist2 = tf.keras.metrics.CosineSimilarity()(y_true=predict, y_pred=d2)
    dist3 = tf.keras.metrics.CosineSimilarity()(y_true=predict, y_pred=d3)
    distance1 = float(dist1.numpy())
    distance2 = float(dist2.numpy())
    distance3 = float(dist3.numpy())
    return predict, distance1, distance2, distance3


def vgg19_distance(filepath):
    image = tf.keras.utils.load_img(filepath)
    try:
        image = image.resize((224, 224))
    except:
        image = image.resize((224, 224), box=(0, 0, image.width, image.height))
    input_arr = keras.utils.img_to_array(image)
    input_arr = np.array([input_arr])  # Convert single image to a batch.
    predict = model.predict(input_arr)
    return calc_distance3(predict)


#main('\\\\192.168.255.9\\tempimg', con1, con2, con3)
#main('C:\\Users\\KimmoHakkarainen\\OneDrive - Exadeci Oy\\DCIM', con1, con2, con3)
main('C:\\temp', con1, con2, con3)

