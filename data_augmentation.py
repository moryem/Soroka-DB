# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 13:08:16 2019

@author: Mor
"""

from keras.preprocessing.image import ImageDataGenerator
import numpy as np

# read the existing data and labels
x_train = np.load('mammos.npy')
y_train = np.load('labels.npy')

# create the data generator
datagen = ImageDataGenerator(
    rotation_range = 90,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip = True,
    vertical_flip = True)

# fit it to the data
datagen.fit(x_train, augment=True)

# concatenate 
counter, flag = 1, 1

for x_batch, y_batch in datagen.flow(x_train, y_train, batch_size = x_train.shape[0]):
    x_train = np.concatenate((x_train,x_batch),axis=0)
    y_train = np.concatenate((y_train,y_batch),axis=0)
    counter += 1
    if (counter == 5): # end after 5 variations
        break

np.save('x_train',np.squeeze(x_train))
np.save('y_train',np.squeeze(y_train))
