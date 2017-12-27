#!/usr/bin/env python3
'''
Created on 20171226
Update on 20171226
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

import time
import logging
import cv2

from CanvasImg import CanvasImg

class Entidade(object):
    def __init__(self, id, x, y, w, h, t):
        self.id = id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.time = t
        self.cx = int(x + w/2)   # put circle in middle of width
        self.cy = int(y + h/2)   # put circle in middle of height
        self.cw, self.ch = w, h

    def draw_rectangle(self, image):
        cv2.rectangle(image,(self.cx, self.cy), (self.x + self.cw, self.y + self.ch), (0,255,0), 3)

class MoveDetect(object):
    '''
    Classe de deteccao de movimento
    '''
    def __init__(self, config_settings):
        #self.bigger = config_settings['bigger']
        self.min_area = config_settings['min_area']
        self.blur_size = config_settings['blur_size']
        self.threshold_sensitivity = config_settings['threshold_sensitivity']
        #self.movelist_timeout = config_settings['movelist_timeout']
        #self.inout_reverse = config_settings['inout_reverse']
        #self.canvas = canvas

    def detect(self, grayimage1, grayimage2, move_time):
        '''
        Detecta lista de movimentos com identificador zerado
        '''

        #lista de retorno
        detected_list = []

        # Get differences between the two greyed images
        differenceimage = cv2.absdiff(grayimage1, grayimage2)
        differenceimage = cv2.blur(differenceimage, (self.blur_size, self.blur_size))

        # Get threshold of difference image based on THRESHOLD_SENSITIVITY variable
        retval, thresholdimage = cv2.threshold(differenceimage, self.threshold_sensitivity, 255, cv2.THRESH_BINARY)
        try:
            thresholdimage, contours, hierarchy = cv2.findContours( thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
        except:
            contours, hierarchy = cv2.findContours( thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )

        if contours:
            total_contours = len(contours)  # Get total number of contours
            for c in contours:              # find contour with biggest area
                found_area = cv2.contourArea(c)  # get area of next contour
                # find the middle of largest bounding rectangle
                if found_area > self.min_area:
                    (x, y, w, h) = cv2.boundingRect(c)
                    e = Entidade(0, x, y, w, h, move_time)
                    detected_list.append(e)

        return detected_list
