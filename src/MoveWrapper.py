#!/usr/bin/env python3
'''
Created on 20180326
Update on 20200214
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

import json
import os
import requests

import time
import cv2
from src.CanvasImg import CanvasImg
from src.VideoStreamDev import VideoStreamDev
from src.MoveDetect import MoveDetect, Entidade, aglutinador
from src.Recorder import Recorder, get_recorder

import subprocess

import datetime as dt 

def execute_comando(comando):
    separado = comando.split(' ')
    proc = subprocess.Popen(separado,
                            #shell=True,
                            #preexec_fn=os.setsid,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    proc.wait()
    #logging.debug('Comando: %s status: %d', comando, proc.returncode)
    return proc.returncode

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

        self.anterior = dt.datetime.now()
        self.contador = 0

        self.lastFrameMove = 0
        self.lastTotMove = 0
        self.maximg = 50

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

        #frame anterior e atual e o mesmo
        if lista_crua is None:
            return None

        lista = aglutinador(lista_crua, 0, self.canvas_img.width, self.canvas_img.height)

        tot_mov = len(lista)

        image = self.move.image

        cv2.putText(image, "FPS:" + str(int(self.stream.fps)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)
        cv2.putText(image, "Date:" + dt.datetime.now().isoformat()[:-7], (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)

        # alert1 = Entidade(str(1), 80, 180, 150, 100, None)
        #alert1.prefix_texo = 'Detect Area'

        #alert2 = Entidade(str(2), 575, 300, 150, 150, None)
        #alert2.prefix_texo = 'Detect Area'

        #se há movimento desenhe retangulos e ajuste o FPS na Tela
        if tot_mov > 0 or self.lastFrameMove > 0:

            # for entidade in lista:
            #     entidade.draw_rectangle(image)

                # if alert1.is_collide(entidade, 0, self.canvas_img.width, self.canvas_img.height) is True:
                #     alert1.cor_retangulo = (0, 0, 255)
                #     break

                # if alert2.is_collide(entidade, 0, self.canvas_img.width, self.canvas_img.height) is True:
                #     alert2.cor_retangulo = (0, 0, 255)
                #     break

            # if tot_mov != 0:
            #     self.lastTotMov = tot_mov
            # else:
            #     tot_mov = self.lastTotMov

            cv2.putText(image, "Mov:" + str(int(tot_mov)), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

            atual = dt.datetime.now()
            delta = atual - self.anterior
            if delta.total_seconds() >= 3:
                self.anterior = atual

                if tot_mov != 0:
                    self.lastFrameMove = 5
                else:
                    if self.lastFrameMove != 0:
                        self.lastFrameMove -= 1

                cv2.imwrite('{0}.jpg'.format(self.contador), image)
                print('imagem ' + str(self.contador))

                ## Envio direto AWS
                # ip_data = '18.212.73.83'
                # ip_data = '127.0.0.1'
                # comando1 = 'scp -i remota1.pem {0}.jpg ubuntu@{1}:~/FlaskStreaming/imgs/{0}.jpg'.format(self.contador, ip_data)
                # execute_comando(comando1)

                # Envio RestAPI
                info = {}
                url = 'http://127.0.0.1:5000/newzzxxccA1'
                info['name'] = '{0}.jpg'.format(self.contador)
                info['tot'] = self.maximg
                file = open('{0}.jpg'.format(self.contador), mode='rb')

                result = self.postRestApiDic(info, url, file)
                if result[0] is False:
                    print('{0} Envio {1}'.format(result[1], str(info['name'])))

                self.contador += 1
                if self.contador >= self.maximg:
                    self.contador = 0

        #alert1.draw_rectangle(image)
        #alert2.draw_rectangle(image)

        if self.rec is not None:
            self.rec.write_frame(image, self.stream._frame_count)

        return image


    def postRestApiDic(self, info, url_methodo, fileHandle):
        """[Executa um metodo POST (MultiPart) enviando um dictionary e um arquivo recebendo ok]
        Arguments:
            info {[dictionary]} -- [dados a enviar]
            methodo {[string]} -- [metodo do POST]
            fileHandle {[type]} -- [handle de arquivo se existir ou None]
        Returns:
            [type] -- [description]
        """

        msg_erro = ''

        try:
            files = {}
            files['json'] = (None, json.dumps(info), 'application/json')
            if fileHandle is not None:
                files['file'] = (os.path.basename(info['name']), fileHandle, 'application/octet-stream')

            response = requests.post(url_methodo, files=files)
            if response.ok is True:
                return True, "OK"
            else:    
                if response.reason is not None:
                    tot = len(response.reason)
                    if tot > 0:
                        msg_erro = 'Erro web: {0} URL: {1}'.format(str(response.reason), url_methodo)
                    else:
                        msg_erro = 'Erro Desconhecido no web URL: {0}'.format(url_methodo)
                else:
                    msg_erro = 'Erro Desconhecido no web URL: {0}'.format(url_methodo)
        
        except Exception as exp:
            msg_erro = 'Erro web: {0} URL: {1}'.format(str(exp), url_methodo)

        return False, msg_erro