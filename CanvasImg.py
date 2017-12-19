#!/usr/bin/env python3
'''
Created on 20171217
Update on 20171218
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703


class Properties(object):
    def __init__(self, config_settings):
        self.bigger = config_settings['bigger']


class CanvasImg(object):
    '''
    Classe de tratamento de tela para acerto geometrico de linhas e planos
    '''
    def __init__(self, config_settings):
        '''
        Inicializa dados da possivel tela
        '''
        self.width = config_settings['defaults']['width']
        self.height = config_settings['defaults']['height']

        self.hflip = config_settings['defaults']['hflip']
        self.vflip = config_settings['defaults']['vflip']
        self.rotation = config_settings['defaults']['rotation']
        self.frame_rate = config_settings['defaults']['frame_rate']

        self.windows_on = config_settings['defaults']['windows_on']

        self.x_center = self.width / 2
        self.y_center = self.height / 2
        self.x_max = self.height
        self.y_max = self.width
        self.x_buf = self.width / 10
        self.y_buf = self.height / 10

        self.properties = Properties(config_settings['prop'])
        

    def crossed_x_centerline(self, enter, leave, movelist):
        '''
        Determina se cruza o meio em X
        '''
        #xbuf = 20  # buffer space on either side of x_center to avoid extra counts
        # Check if over center line then count
        if len(movelist) > 1:  # Are there two entries
            if movelist[0] <= self.x_center and  movelist[-1] > self.x_center + self.x_buf:
                leave += 1
                movelist = []
            elif movelist[0] > self.x_center and  movelist[-1] < self.x_center - self.x_buf:
                enter += 1
                movelist = []

        return enter, leave, movelist

    def crossed_y_centerline(self, enter, leave, movelist):
        '''
        Determina se cruza o meio em Y
        '''
        # Check if over center line then count
        if len(movelist) > 1:  # Are there two entries
            if movelist[0] <= self.y_center and  movelist[-1] > self.y_center + self.y_buf:
                leave += 1
                movelist = []
            elif movelist[0] > self.y_center and  movelist[-1] < self.y_center - self.y_buf:
                enter += 1
                movelist = []
        return enter, leave, movelist

    def get_bigger(self):

        big_w = int(self.width * self.properties.bigger)
        big_h = int(self.height * self.properties.bigger)

        return (big_w, big_h)
