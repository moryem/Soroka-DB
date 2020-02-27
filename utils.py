# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 12:20:45 2020

@author: Mor
"""

import os
import pandas as pd
import pydicom
from collections import OrderedDict
import json

class read_dcm():

    def __init__(self, mammo_dir = 'all_mammograms', path = '.', mode = None):
# =============================================================================
#         initialize parameters
# =============================================================================
        
        self.mammo_dir = mammo_dir          # mammograms directory name
        self.path = path                    # root directory
        self.mode = mode                    # unilateral or bilateral
        self.codes = set()                  # set of names to prevent duplicates
        self.dcm_paths = []                 # list off dcm files paths
        
    def get_all_dcm_names(self):
# =============================================================================
#         get dicom files names
# =============================================================================

        # get the tree of directories
        self.mammo_path = os.path.join(self.path, self.mammo_dir)
        self.dcm_dirs = list(os.walk(self.mammo_path))
        
        # get the dicom files names inside each directory as a list
        self.dcm_tpl = [self.dcm_dirs[i] for i in range(len(self.dcm_dirs)) if self.dcm_dirs[i][1] == []]
        self.all_dcm_names = [os.path.join(self.dcm_tpl[i][0],self.dcm_tpl[i][2][0]) for i in range(len(self.dcm_tpl))]

    def read_dicom(self):
# =============================================================================
#         create a dataframe with each dicom file detailes
# =============================================================================
        
        if os.path.exists(os.path.join('.','df_' + self.mode + '.pkl')) and os.path.exists(os.path.join('.','dcm_paths_' + self.mode + '.json')):
            self.dicom_df = pd.read_pickle('df_' + self.mode + '.pkl')
            with open('dcm_paths_' + self.mode + '.json') as json_file:
                self.dcm_paths = json.load(json_file)
        else:
            self.get_all_dcm_names()
            # read files
            self.dicom_df = list(map(self.read_dicom_file, self.all_dcm_names, range(len(self.all_dcm_names))))
            self.dicom_df = pd.concat(self.dicom_df)  
            # reindex
            self.dicom_df.index = range(len(self.dicom_df))
            if (self.mode == 'bilateral'):
                self.remove_mastectomy()
                # save df into pickle file
                self.dicom_df.to_pickle('df_bilateral.pkl')
                # save dicom paths into json file
                self.save_dcm_paths(name='dcm_paths_bilateral.json')
            else:
                # save df into pickle file
                self.dicom_df.to_pickle('df_unilateral.pkl')
                # save dicom paths into json file
                self.save_dcm_paths(name='dcm_paths_unilateral.json')
                

    def read_dicom_file(self, dcm_file, i):
# =============================================================================
#         returns the wanted details of each dicom file in a dataframe format
# =============================================================================

        # read dicom file
        ds = pydicom.dcmread(dcm_file)
        
        # create the encoded name
        second_dash = dcm_file.find('\\',2)
        third_dash = dcm_file.find('\\',second_dash+1)
        name = dcm_file[second_dash+1:third_dash]
        
        # get laterality from two types of dicom files
        try:
            laterality = ds[0x20,0x62].value
        except:
            try:
                laterality = ds[0x20,0x60].value
            except: # raise error if dcm file is unreadable
                print (dcm_file + 'is unreadable')
        
        # Create DataFrame
        data = [OrderedDict({'Name': name, 'Birth Date': ds[0x10,0x30].value, 'Study Date':ds[0x08,0x20].value,
         'Age': ds[0x10,0x1010].value, 'Laterality': laterality, 'View':ds[0x18, 0x5101].value,
         'Orientation':ds[0x20, 0x20].value})]
        df = pd.DataFrame(data, index=[i])
        
        # check if this dicom is not a duplicate
        code = name + '_' + laterality + '_' + ds[0x18, 0x5101].value
        if code in self.codes:
            return
        else:
            self.codes.add(code)
            self.dcm_paths.append(dcm_file)
            return df

    def save_dcm_paths(self, name):
# =============================================================================
#       save dcm names so we won't need to build it each time 
# =============================================================================
        
        with open(name, 'w') as file:
            json.dump(self.dcm_paths, file)

    def remove_mastectomy(self):
# =============================================================================
#       remove all images of only one breast for the bilateral model     
# =============================================================================
        
        new_df = pd.DataFrame()
        patients = set(self.dicom_df['Name'])
        for patient in patients: # run over patients
            patient_df = self.dicom_df[self.dicom_df['Name']==patient]
            # Check for CC view R and L
            patient_cc_df = patient_df[patient_df['View']=='CC']  
            cc_lateralities = set(patient_cc_df['Laterality'])
            if ('L' in cc_lateralities) and ('R' in cc_lateralities): 
                new_df = pd.concat([new_df,patient_cc_df])
            # Check for MLO view R and L
            patient_mlo_df = patient_df[patient_df['View']=='MLO']  
            mlo_lateralities = set(patient_mlo_df['Laterality'])
            if ('L' in mlo_lateralities) and ('R' in mlo_lateralities):
                new_df = pd.concat([new_df,patient_mlo_df])                
        
        # sort by original indexes and update dicom_df
        self.dicom_df = new_df.sort_index()
        # take the matching dicom paths
        idx = self.dicom_df.index.values
        self.dcm_paths = [self.dcm_paths[i] for i in idx]
        # reindex
        self.dicom_df.index = range(len(self.dicom_df))
    
      
