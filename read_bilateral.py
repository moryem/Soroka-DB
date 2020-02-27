# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 17:34:21 2019

@author: Mor
"""

import os
import pandas as pd
import pydicom
import numpy as np
import cv2
from utils import read_dcm
from pre_process import pre_process
from keras.utils import to_categorical
from sklearn.utils import shuffle 


class read_data():
    
    def __init__(self, exl_name = 'Mammo_Out.xlsx', path = '.'):
# =============================================================================
#         initialize parameters
# =============================================================================
        
        self.exl_name = exl_name                # excel file for interpretations
        self.path = path                        # root directory
        self.rd = read_dcm(mode='bilateral')    # read dicom object

    def create_data(self):
# =============================================================================
#       read all images pairs and their labels    
# =============================================================================
    
        # create data         
        if os.path.isfile('./right.npy') and os.path.isfile('./left.npy'):
            self.right = np.load('./right.npy')
            self.left = np.load('./left.npy')
        else:
            self.read_right_left()
            np.save('right.npy',self.right)
            np.save('left.npy',self.left)
                    
        # create labels
        if os.path.isfile('./y.npy'):
            self.y = np.load('./y.npy')
        else:            
            self.create_labels()
            np.save('y.npy',self.y)
            
        # shuffle and devide to train and test sets
        self.right, self.left, self.y = shuffle(self.right, self.left, self.y, random_state=52)
        
        self.right_train = self.right[:round(0.8*self.right.shape[0]),:,:,:]
        self.left_train = self.left[:round(0.8*self.left.shape[0]),:,:,:]
        
        self.right_test = self.right[round(0.8*self.right.shape[0]):,:,:,:]
        self.left_test = self.left[round(0.8*self.left.shape[0]):,:,:,:]
        
        self.y_train = self.y[:round(0.8*self.y.shape[0]),:]
        self.y_test = self.y[round(0.8*self.y.shape[0]):,:]
        
        # save to npy
        np.save('right_train.npy',self.right_train)
        np.save('left_train.npy',self.left_train)
        np.save('right_test.npy',self.right_test)
        np.save('left_test.npy',self.left_test)
        np.save('y_train.npy',self.y_train)
        np.save('y_test.npy',self.y_test)
        
           
    def read_right_left(self):
# =============================================================================
#          Create bi-lateral pairs for similarity model        
# =============================================================================
   
        # read orifinal dicom_df    
        self.rd.read_dicom()

        # right side images
        self.right_df, self.right_dcm = self.create_side_df_dcm('R')
        
        # left side images        
        self.left_df, self.left_dcm = self.create_side_df_dcm('L')
        
        # read each right file
        right_data = [self.read_img(self.right_dcm[i], self.right_df.iloc[i]) for i in range(len(self.right_dcm))]
        self.right = np.asarray(right_data)

        # read each left file
        left_data = [self.read_img(self.left_dcm[i], self.left_df.iloc[i]) for i in range(len(self.left_dcm))]
        self.left = np.asarray(left_data)

    def create_side_df_dcm(self, laterality):
# =============================================================================
#       create a dataframe with the wanted information and a list of dcm files 
#       of inly one laterality        
# =============================================================================
         
        # find indexes of all CC views of the laterality and extract the matching dcm paths
        cc_ind = np.where((self.rd.dicom_df['Laterality']==laterality) & (self.rd.dicom_df['View']=='CC'))
        cc_dcm = [self.rd.dcm_paths[i] for i in cc_ind[0]]   
        # find indexes of all MLO views of the laterality
        mlo_ind = np.where((self.rd.dicom_df['Laterality']==laterality) & (self.rd.dicom_df['View']=='MLO'))
        mlo_dcm = [self.rd.dcm_paths[i] for i in mlo_ind[0]]
        # create list of dcm names and dataframe of all right side images
        dcm = cc_dcm + mlo_dcm
        new_df = pd.concat((self.rd.dicom_df.iloc[cc_ind],self.rd.dicom_df.iloc[mlo_ind]))
        # reindex
        new_df.index = range(len(new_df))
        
        return new_df, dcm
        
    def read_img(self, dcm_file, df_row):
# =============================================================================
#         read and process the image in the dicom file       
# =============================================================================
                
        # read dicom file
        ds = pydicom.dcmread(dcm_file)
        # get img 
        img = ds.pixel_array        
        # if it's Left side - flip to match the right side
        if (df_row['Laterality']=='L'):
            if ('A' in df_row['Orientation']):
                # flip along y axis
                img = cv2.flip(img, 1)
            elif (('FR' in df_row['Orientation']) or 
                  ('F' in df_row['Orientation']) or 
                  ('R' in df_row['Orientation']) or
                  (df_row['Name']=='SAA1521')): # this one case is exceptional
                img = img
            else:
                # flip along x axis
                img = cv2.flip(img, 0)
        # pre-process the image
        pp = pre_process(min_size=20000, height=100, width=100)
        # crop the breast part in the image
        cropped = pp.crop_image(img[:,:,np.newaxis])
        # resize
        img2 = pp.resize(cropped)[:,:,np.newaxis]
        
        return img2
    
    def  create_labels(self):
# =============================================================================
#       create labels according to birads level (4 and above in either side 
#        means positive)        
# =============================================================================
        
        try:
            # read excel file
            exl_file = pd.read_excel(os.path.join(self.path, self.exl_name))
        except:
            print('Excel file does not exist')
            return
        
        # organise bi-rads levels
        self.birads = np.asarray(exl_file['Bi-Rads'].values)
        # convert 4X to 4
        self.birads[np.where(self.birads=='4a')] = 4
        self.birads[np.where(self.birads=='4b')] = 4
        self.birads[np.where(self.birads=='4c')] = 4
        
        y = []
        self.right_df, junk = self.create_side_df_dcm('R')
        for i in range(len(self.right_df)): # run over all cases
            birads = self.birads[exl_file['Name'] == self.right_df['Name'][i]]
            if (any(birads>=4)):
                y.append(1)
            else:
                y.append(0)
        
        self.y = to_categorical(np.asarray(y))

    
#%%
        
rd = read_data()
rd.create_data()        
        