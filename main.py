import os
import tensorflow as tf
import tensorflow.keras as keras
import numpy as np


#conv_base = keras.applications.vgg16.VGG16(
conv_base = keras.applications.vgg19.VGG19(
    weights='imagenet',
    include_top=False,
    #pooling='max',
    input_shape=(224, 224, 3))


flat1 = tf.keras.layers.Flatten()(conv_base.output)
# define new model
model = tf.keras.Model(inputs=conv_base.inputs, outputs=flat1)

#conv_base.add(tf.keras.layers.Flatten())
print(conv_base.summary())
print(model.summary())

dataset = tf.keras.preprocessing.image_dataset_from_directory('images', label_mode=None, image_size=(224,224))
features = conv_base.predict(dataset)
print(features.shape)

for i in range(len(features)):
    for p in range(i+1,len(features)):
        print(str(i) + ' vs ' + str(p))
        print(tf.keras.metrics.CosineSimilarity()(y_true=features[i],y_pred=features[p]))

#predictions = tf.keras.applications.vgg16.decode_predictions(features, top=1)
#print(predictions)