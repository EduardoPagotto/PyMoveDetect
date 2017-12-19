#!/usr/bin/env python3
'''
Created on 20171012
Update on 20171216
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

import cv2
import time
import threading

import logging

class VideoStreamDev(object):
    '''Classe de stream do arquivo/device'''

    FRAME_COUNTER = 1000

    def __init__(self, device_cam, canvas, debug):
        '''Inicializacao thread de video'''

        self._thead = threading.Thread(target=self.update, args=())
        self._thead.daemon = True
        self._stopped = False

        self._ao_vivo = isinstance(device_cam, int)

        self.canvas = canvas

        self._stream = cv2.VideoCapture(device_cam)
        self._stream.set(3, canvas.width)
        self._stream.set(4, canvas.height)

        self.debug = debug

        (self._grabbed, self._frame) = self._stream.read()

    def start(self):
        '''Ativa a Thread'''
        # start the thread to read frames from the video stream
        self._thead.start()
        return self

    def update(self):
        '''Atualiza status do video'''
        while True:
            if self._stopped:
                return

            if self._ao_vivo is False:
                time.sleep(0.037)#delay devido ao video continuo 1/27 (27FPS)

            #Le o proximo frame
            (self._grabbed, self._frame) = self._stream.read()

    def read(self):
        '''retorna o frame mais recente'''
        return self._frame

    def stop(self):
        '''Sinaliza parada da thread'''
        # indicate that the thread should be stopped
        self._stopped = True

    def show_FPS(self, start_time, frame_count):
        '''
        contabiliza FPS
        '''
        if self.debug:
            if frame_count >= self.FRAME_COUNTER:
                duration = float(time.time() - start_time)
                FPS = float(frame_count / duration)
                logging.info("Processing at %.2f fps last %i frames", FPS, frame_count)
                frame_count = 0
                start_time = time.time()
            else:
                frame_count += 1

        return start_time, frame_count

    def get_gray_image(self):
        try:
            return cv2.cvtColor(self.read(), cv2.COLOR_BGR2GRAY)
        except Exception as exp:
            self.stop()
            logging.error('Nao foi possivel capturar image GRAY, Erro:%s', str(exp))
            raise exp
            