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
import cv2

import numpy as np

from src.CanvasImg import CanvasImg

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

def aglutinador(lista):
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

def classificador(lista, distance_far, limit_w, limit_h):

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

            if len(lista_aglutinada) > 0:
                lista_aglutinada.append(e1)
                e1 = aglutinador(lista_aglutinada)
            else:
                repete = False

        if e1.dead is False:
            lista_final.append(e1)

    return lista_final
