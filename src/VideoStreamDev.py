#!/usr/bin/env python3
'''
Created on 20171012
Update on 20180326
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

import time
import logging
import datetime
import threading
import cv2

class VideoStreamDev(object):
    '''Classe de stream do arquivo/device'''

    def __init__(self, device_cam, width, height):
        '''Inicializacao thread de video'''

        self._thead = threading.Thread(target=self.update, args=())
        self._thead.daemon = True
        self._stopped = False

        self._ao_vivo = isinstance(device_cam, int)

        self._stream = cv2.VideoCapture(device_cam)
        self._stream.set(3, width)
        self._stream.set(4, height)
        self._frame_count = 0
        (self._grabbed, self._frame) = self._stream.read()
        self.fps = 0

        self.log = logging.getLogger(__name__)
        if self._ao_vivo is True:
            self.log.info('Video (%d x %d) definido na WebCam:%d', width, height, device_cam)
        else:
            self.log.info('Video (%d x %d) em arquivo: %s', width, height, device_cam)


    def start(self):
        '''Ativa a Thread'''
        # start the thread to read frames from the video stream
        self._thead.start()
        self.log.info('Thread de Video Stream em execucao')
        return self

    def update(self):
        '''Atualiza status do video'''

        inicio = datetime.datetime.now()
        frames_por_ciclo = 0

        while True:
            if self._stopped:
                return

            if self._ao_vivo is False:
                time.sleep(0.037)#delay devido ao video continuo 1/27 (27FPS)

            #Le o proximo frame
            (self._grabbed, self._frame) = self._stream.read()

            self._frame_count += 1

            frames_por_ciclo += 1
            atual = datetime.datetime.now()
            elapsed = atual - inicio
            if elapsed.seconds >= 1: # 1 segundo
                self.fps = int(frames_por_ciclo)
                frames_por_ciclo = 0
                inicio = atual

    def read(self):
        '''retorna o frame mais recente'''
        return (self._frame_count, self._frame)

    def stop(self):
        '''Sinaliza parada da thread'''
        # indicate that the thread should be stopped
        self._stopped = True
        self.log.info('Thread de Video Stream sinalizada a encerrar')
