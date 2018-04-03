#!/usr/bin/env python3
'''
Created on 20180326
Update on 20180326
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

import time
import cv2
from src.CanvasImg import CanvasImg
from src.VideoStreamDev import VideoStreamDev
from src.MoveDetect import MoveDetect, Entidade, aglutinador
from src.Recorder import Recorder, get_recorder

class MoveWrapper(object):
    '''
    Classe de regra de negocio
    '''
    def __init__(self, config_global):
        '''
        Inicializa todos os objetos
        '''
        cf = config_global['move']
        self.canvas_img = CanvasImg(cf['canvas'])
        self.stream = VideoStreamDev(cf['video_device'], self.canvas_img.width, self.canvas_img.height)
        self.move = MoveDetect(self.stream, self.canvas_img.width, self.canvas_img.height, cf['move_entity'])
        self.rec = get_recorder(config_global)

    def start(self):
        '''
        Dispara processor de stream e deteccao
        '''
        self.stream.start()
        self.move.start_frame()

    def stop(self):
        '''
        encerra processos
        '''
        self.stream.stop()
        time.sleep(1)

        if self.rec is not None:
            self.rec.close()

    def capture(self):
        '''
        Captura novo frame e o retorna
        '''
        lista_crua = self.move.detect(time.time())

        lista = aglutinador(lista_crua, 0, self.canvas_img.width, self.canvas_img.height)

        tot_mov = len(lista)

        image = self.move.image

        cv2.putText(image, "FPS : " + str(int(self.stream.fps)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)

        #alert1 = Entidade(str(1), 80, 180, 150, 100, None)
        #alert1.prefix_texo = 'Detect Area'

        #alert2 = Entidade(str(2), 575, 300, 150, 150, None)
        #alert2.prefix_texo = 'Detect Area'

        #se há movimento desenhe retangulos e ajuste o FPS na Tela
        if tot_mov > 0:
            cv2.putText(image, "Entidades : " + str(int(tot_mov)), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            for entidade in lista:
                entidade.draw_rectangle(image)

                # if alert1.is_collide(entidade, 0, self.canvas_img.width, self.canvas_img.height) is True:
                #     alert1.cor_retangulo = (0, 0, 255)
                #     break

                # if alert2.is_collide(entidade, 0, self.canvas_img.width, self.canvas_img.height) is True:
                #     alert2.cor_retangulo = (0, 0, 255)
                #     break

        #alert1.draw_rectangle(image)
        #alert2.draw_rectangle(image)

        if self.rec is not None:
            self.rec.write_frame(image, self.stream._frame_count)

        return image