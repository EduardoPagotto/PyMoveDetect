#!/usr/bin/env python3
'''
Created on 20171226
Update on 20171228
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

import time
import logging
import cv2

import numpy as np

from CanvasImg import CanvasImg

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

        self.prefix_texo = 'ID:'
        self.cor_texto = (255, 0, 0)
        self.size_texto = 0.25
        self.trick_texto = 1

        self.cor_retangulo = (0, 255, 0)
        self.trick_retangulo = 2

    def draw_rectangle(self, image):
        '''
        Desenha quadrado e info no mesmo
        '''
        cv2.rectangle(image, tuple(self.retangulo[0]), tuple(np.sum(self.retangulo, axis=0)), self.cor_retangulo, self.trick_retangulo)
        cv2.putText(image, self.prefix_texo + self.identificador, (self.retangulo[0][0], self.retangulo[0][1]-10), cv2.FONT_HERSHEY_SIMPLEX, self.size_texto, self.cor_texto, self.trick_texto)

class MoveDetect(object):
    '''
    Classe de deteccao de movimento
    '''
    def __init__(self, stream, width, height, config_settings):
        '''
        Inicializa dados
        stream: thread de leitura de camera/video
        width: resize width da geometria de tela usada para algoritmo de deteccao de movimento
        height: resize height da geometria de tela usada para algoritmo de deteccao de movimento
        config_settings: dict com dados do filtro
        '''
        self._min_area = config_settings['min_area']
        self._blur_size = config_settings['blur_size']
        self._threshold_sensitivity = config_settings['threshold_sensitivity']

        self._stream = stream
        self._width = width
        self._height = height

        self.image = None
        self.differenceimage = None
        self.thresholdimage = None
        self._gray_buffer = None
        self._last_frame_count = 0

    def start_frame(self):
        '''
        Primeiro frame a ser considerado
        '''
        #le primeiro frame e contador
        self._last_frame_count, img = self._stream.read()

        #redimenciona
        self.image = cv2.resize(img, (self._width, self._height))

        #inicializa buffer de cinza
        self._gray_buffer = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)


    def detect(self, move_time):
        '''
        Detecta lista de movimentos com identificador zerado,
        start_frame() deve ser chamado antes deste, fora do loop
        move_time: time que a ocorrencia do movimento foi registrada(o mesmo e usado em todo o bloco)
        '''

        #lista de retorno vazia
        detected_list = []

        #le frame atual
        last, img = self._stream.read()

        #se frame atual e o mesmo que o anterior ignora deteccao(ECONOMIA DE PROCESSADOR!!!!)
        if last > self._last_frame_count:

            #se novo frame atualiza dados e processar diferencas
            self._last_frame_count = last

            #le imagem colorida e redimenciona para tamanho mais facil de calcular
            self.image = cv2.resize(img, (self._width, self._height))

            #converte para GRAY
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

            # calcula a diferenca entre os 2 buffers em gray
            differenceimage = cv2.absdiff(self._gray_buffer, gray)

            #filtro em blur para gerar imagem mais cheia
            #self.differenceimage = cv2.blur(differenceimage, (self._blur_size, self._blur_size))

            # Calcula o threshold da diferenca das imagens baseado na variavel THRESHOLD_SENSITIVITY
            retval, thresholdimage = cv2.threshold(differenceimage, self._threshold_sensitivity, 255, cv2.THRESH_BINARY)

            thresholdimage = cv2.dilate(thresholdimage, None, iterations=2)

            try:
                thresholdimage, contours, hierarchy = cv2.findContours(thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            except:
                contours, hierarchy = cv2.findContours(thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            #buffer usado apenas para debug
            self.differenceimage = differenceimage
            self.thresholdimage = thresholdimage

            #acumula o buffer para ser comparado ao proximo frame que for valido (novo)
            self._gray_buffer = gray

            #Contabiliza os contornos e gera uma lista desnormalizada.
            if contours:
                for c in contours:

                    # aproveita apenas os maiores que self.min_area
                    if cv2.contourArea(c) > self._min_area:
                        (x, y, w, h) = cv2.boundingRect(c)
                        e = Entidade(str(0), x, y, w, h, move_time)
                        detected_list.append(e)

        return detected_list
