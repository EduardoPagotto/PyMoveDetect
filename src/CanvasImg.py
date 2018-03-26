#!/usr/bin/env python3
'''
Created on 20171217
Update on 20171218
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

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

    def set_flipper(self):
        '''
        Define o valor usado no openCV para o Flip se h ou v forem true
        '''
        if (self.hflip or self.vflip) is False:
            return None
        elif self.hflip is True:
            return 1
        elif self.vflip is True:
            return 0
        else:
            return -1
