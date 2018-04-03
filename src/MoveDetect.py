#!/usr/bin/env python3
'''
Created on 20171226
Update on 20180403
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703
#pylint: disable=W0702

import logging
import cv2
import numpy as np
from src.Entidade import Entidade

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

        self.log = logging.getLogger(__name__)
        self.log.info('Detector de movimento configurado')

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

        self.log.info('Primeiro Frame Capturado')

    def detect(self, move_time):
        '''
        Detecta lista de movimentos com identificador zerado,
        start_frame() deve ser chamado antes deste, fora do loop
        move_time: time que a ocorrencia do movimento foi registrada(o mesmo e usado em todo o bloco)
        '''

        #le frame atual
        last, img = self._stream.read()

        #se frame atual e o mesmo que o anterior ignora deteccao(ECONOMIA DE PROCESSADOR!!!!)
        if last > self._last_frame_count:

            #lista de retorno vazia
            detected_list = []

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
            _, thresholdimage = cv2.threshold(differenceimage, self._threshold_sensitivity, 255, cv2.THRESH_BINARY)

            thresholdimage = cv2.dilate(thresholdimage, None, iterations=2)

            try:
                thresholdimage, contours, _ = cv2.findContours(thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            except:
                contours, _ = cv2.findContours(thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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

        return None

def compositor(lista):
    '''
    converte uma lista de entidades em 1 entidade composta
    '''
    x_final = 9999999
    y_final = 9999999
    x1_final = 0
    y1_final = 0

    for r in lista:

        x, y = tuple(r.retangulo[0])
        x1, y1 = tuple(np.sum(r.retangulo, axis=0))

        if x < x_final:
            x_final = x

        if y < y_final:
            y_final = y

        if x1 > x1_final:
            x1_final = x1

        if y1 > y1_final:
            y1_final = y1

        r.dead = True

    e = Entidade(0, x_final, y_final, x1_final - x_final, y1_final - y_final, lista[0].time)
    e.identificador = lista[0].identificador
    e.prefix_texo = lista[0].prefix_texo
    e.cor_texto = lista[0].cor_texto
    e.size_texto = lista[0].size_texto
    e.trick_texto = lista[0].trick_texto
    e.cor_retangulo = lista[0].cor_retangulo
    e.trick_retangulo = lista[0].trick_retangulo

    return e

def aglutinador(lista, distance_far, limit_w, limit_h):
    '''
    Concatena retangulos que colidem em um unico retangulo
    '''
    lista_final = []

    tot = len(lista)

    for indice in range(0, tot):

        repete = True
        e1 = lista[indice]
        while repete:
            lista_aglutinada = []

            for sub in range(indice, tot):

                if indice == sub:
                    continue

                e2 = lista[sub]
                if e2.dead is True:
                    continue

                if e1.is_collide(e2, distance_far, limit_w, limit_h) is True:
                    lista_aglutinada.append(e2)

            #if len(lista_aglutinada) > 0:
            if lista_aglutinada:
                lista_aglutinada.append(e1)
                e1 = compositor(lista_aglutinada)
            else:
                repete = False

        if e1.dead is False:
            lista_final.append(e1)

    return lista_final
