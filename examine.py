import io
import os
import mariadb
import tensorflow as tf
import tensorflow.keras as keras
import numpy as np

imgpathL = '\\\\192.168.255.9\\incoming\\kimmo\\OpenShare\\canon60d\\20130331\\IMG_1542.CR2'
imgpathP = '\\\\192.168.255.9\\incoming\\kimmo\\OpenShare\\canon60d\\20130331\\IMG_1543.CR2'

conv_base = keras.applications.vgg19.VGG19(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3))
flat1 = tf.keras.layers.Flatten()(conv_base.output)
model = tf.keras.Model(inputs=conv_base.inputs, outputs=flat1)

#image = tf.keras.preprocessing.image.load_img(imgpath, target_size=(224,224))
imageL = tf.keras.preprocessing.image.load_img(imgpathL)
imageP = tf.keras.preprocessing.image.load_img(imgpathP)
#image = tf.keras.utils.load_img(imgpath, target_size=(224,224), keep_aspect_ratio=True)
try:
    imageL.resize((240,240))
    imageP.resize((240,240))
except:
    imageL.resize((240,240), box=(0,0, imageL.width, imageL.height))
    imageP.resize((240,240), box=(0,0, imageP.width, imageP.height))
input_arr = keras.preprocessing.image.img_to_array(image)
input_arr = np.array([input_arr])  # Convert single image to a batch.
predictions = model.predict(input_arr)
