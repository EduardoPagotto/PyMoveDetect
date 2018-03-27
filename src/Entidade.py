#!/usr/bin/env python3
'''
Created on 20180326
Update on 20180326
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

import cv2
import numpy as np

class Entidade(object):
    '''
    Entidade de ocorrencia de movimento
    '''
    def __init__(self, identificador, x, y, w, h, t):#left, up, right, botom
        '''
        Inicializa retangulo com Ocorrencia de movimento
        id: identificador da ocorrenica, na criacao sera inicializado com 0
        x: posicao X
        y: posicao Y
        w: tamanho X
        h: tamanho Y
        t: time da ocorrencia(criacao)
        '''
        self.identificador = identificador
        self.retangulo = np.array(([[x, y], [w, h]]), dtype=int) #array configuracao x, y, size_x, size_y
        self.time = t

        self.center = np.sum(self.retangulo, axis=0) / 2 #np.array([x + w / 2, y + h / 2]), dtype=int)
        self.center = self.center.astype(int)

        self.prefix_texo = 'ID:'
        self.cor_texto = (255, 0, 0)
        self.size_texto = 0.25
        self.trick_texto = 1

        self.cor_retangulo = (0, 255, 0)
        self.trick_retangulo = 2
        self.dead = False

    def draw_rectangle(self, image):
        '''
        Desenha quadrado e info no mesmo
        '''
        cv2.rectangle(image, tuple(self.retangulo[0]), tuple(np.sum(self.retangulo, axis=0)), self.cor_retangulo, self.trick_retangulo)
        cv2.putText(image, self.prefix_texo + self.identificador, (self.retangulo[0][0], self.retangulo[0][1]-10), cv2.FONT_HERSHEY_SIMPLEX, self.size_texto, self.cor_texto, self.trick_texto)

    def distancia(self, outro):
        '''
        calcula a distancia do outro ponto
        '''
        #distancia entre 2 pontos de centro de retangulo
        return (np.dot(self.center - outro.center, self.center - outro.center))**.5

    def is_collide(self, outro, distance_far, limit_w, limit_h):
        '''
        verifica se colide com distancia 
        '''
        x_1 = self.retangulo[0][0] - distance_far
        if x_1 < 0:
            x_1 = 0

        y_1 = self.retangulo[0][1] - distance_far
        if y_1 < 0:
            y_1 = 0

        width_1 = self.retangulo[1][0] + distance_far
        if width_1 > limit_w:
            width_1 = limit_w

        height_1 = self.retangulo[1][1] + distance_far
        if height_1 > limit_h:
            height_1 = limit_h

        x_2 = outro.retangulo[0][0] - distance_far
        if x_2 < 0:
            x_2 = 0

        y_2 = outro.retangulo[0][1] - distance_far
        if y_2 < 0:
            y_2 = 0

        width_2 = outro.retangulo[1][0] + distance_far
        if width_2 > limit_w:
            width_2 = limit_w

        height_2 = outro.retangulo[1][1] + distance_far
        if height_2 > limit_h:
            height_2 = limit_h

        return not (x_1 > (x_2 + width_2) or (x_1 + width_1) < x_2 or y_1 > (y_2 + height_2) or (y_1 + height_1) < y_2)
