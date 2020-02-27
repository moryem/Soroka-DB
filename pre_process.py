# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 15:19:33 2020

@author: Mor
"""

import cv2
import numpy as np

class pre_process():
    
    def __init__(self, min_size = 1000, height = 200, width = 200):
# =============================================================================
#         initialize parameters
# =============================================================================
        
        self.height = height                    # target height for the image
        self.width = width                      # target width for the image           
        self.min_size = min_size                # minimum size of blobs (number of pixels)

    def resize(self,img):
# =============================================================================
#         resize to get uniformity
# =============================================================================
        resized_image = cv2.resize(img,(self.height, self.width)) 
        
        return resized_image

    def crop_image(self, img):
# =============================================================================
#         crop black areas and leave only breast parts
# =============================================================================

        # convert img into uint8 and make it binary for threshold value of 1.    
        _,thresh = cv2.threshold(img.astype('uint8'),1,255,cv2.THRESH_BINARY)
        
        #find all the connected components (white blobs in the image)
        nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(thresh, connectivity=8)
        # take out the background (found also as a blob)
        sizes = stats[1:, -1]; nb_components = nb_components - 1

        # get rid of small blobs
        img2 = np.zeros((output.shape))
        #for every component in the image, we keep it only if it's above min_size
        for i in range(0, nb_components):
            if sizes[i] >= self.min_size:
                img2[output == i + 1] = 255
                
        # find contours and bounding rectangle
        contours = cv2.findContours(img2.astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnt = contours[0]
        x,y,w,h = cv2.boundingRect(cnt)
        
        # crop the original image
        crop = img[y:y+h,x:x+w] 
    
        return crop
