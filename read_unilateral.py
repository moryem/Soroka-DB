# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 17:34:21 2019

@author: Mor
"""

import os
import pandas as pd
import pydicom
import numpy as np
from keras.utils import to_categorical
from utils import read_dcm
from pre_process import pre_process

class read_data():
    
    def __init__(self, exl_name = 'Mammo_Out.xlsx', path = '.'):
# =============================================================================
#         initialize parameters
# =============================================================================
        
        self.exl_name = exl_name                # excel file for interpretations
        self.path = path                        # root directory
        self.rd = read_dcm(mode='unilateral')   # read dicom object

    def create_data(self):
# =============================================================================
#         read all images and their labels
# =============================================================================
        
        # create data
        if os.path.isfile('./x_train.npy'):
            self.X = np.load('./x_train.npy')
        else:
            # read dcm_names
            self.rd.read_dicom()
            data = list(map(self.read_img, self.rd.dcm_paths))
            self.X = np.asarray(data)
            np.save('x_train', self.X, allow_pickle=True, fix_imports=True)
        
        # create labels
        if os.path.isfile('./y_train.npy'):
            self.y = np.load('./y_train.npy')
            self.birads = np.load('./birads.npy')
        else:
            self.create_labels()
            np.save('y_train', self.y, allow_pickle=True, fix_imports=True)
            np.save('birads', self.birads, allow_pickle=True, fix_imports=True)
                                
    def read_img(self, dcm_file):
# =============================================================================
#         read and process the image in the dicom file       
# =============================================================================
        
        # read dicom file
        ds = pydicom.dcmread(dcm_file)
        # get img 
        img = ds.pixel_array
        # pre-process the image
        pp = pre_process(min_size=10000)       
        # crop the breast part in the image
        cropped = pp.crop_image(img[:,:,np.newaxis])
        # resize
        img2 = pp.resize(cropped)[:,:,np.newaxis]
        
        return img2
    
    def create_labels(self):
# =============================================================================
#         create labels according to birads level (above 4 means positive)
# =============================================================================
        
        try:
            # read excel file
            exl_file = pd.read_excel(os.path.join(self.path, self.exl_name))
        except:
            print('Excel file does not exist')
            return

        self.birads = np.asarray(exl_file['Bi-Rads'].values)
        # convert 4X to 4
        self.birads[np.where(self.birads=='4a')] = 4
        self.birads[np.where(self.birads=='4b')] = 4
        self.birads[np.where(self.birads=='4c')] = 4
        # create binary labels
        self.y = np.zeros((len(self.birads),1),int)
        self.y[self.birads>4] = 1
        self.y = to_categorical(self.y)            
  