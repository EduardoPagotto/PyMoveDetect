#!/usr/bin/env python3
'''
Created on 20180326
Update on 20200215
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

import json
import os
import time
import logging
from datetime import datetime as dt
import requests

import cv2
from src.CanvasImg import CanvasImg
from src.VideoStreamDev import VideoStreamDev
from src.MoveDetect import MoveDetect, Entidade, aglutinador
from src.Recorder import Recorder, get_recorder

import subprocess

import datetime as dt 

# def execute_comando(comando):
#     separado = comando.split(' ')
#     proc = subprocess.Popen(separado,
#                             #shell=True,
#                             #preexec_fn=os.setsid,
#                             stdout=subprocess.PIPE,
#                             stderr=subprocess.STDOUT)
#     proc.wait()
#     #logging.debug('Comando: %s status: %d', comando, proc.returncode)
#     return proc.returncode

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

        remoto = config_global['remoto']

        self.lastFrameMove = 0
        self.maximg = remoto['maximg']
        server = remoto['server']
        self.url_audi = server + '/' + remoto['url_audi']
        self.url_file = server + '/' + remoto['url_file']
        self.delay = remoto['delay']
        self.cache_frame = remoto['cache_frame']      

        self.pathimg = remoto['pathimg']
        if not os.path.exists(self.pathimg):
            os.makedirs(self.pathimg)

        self.log = logging.getLogger('MoveWrapper')


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

        #cv2.putText(image, "FPS:" + str(int(self.stream.fps)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 0, 0), 2)
        cv2.putText(image, dt.datetime.now().isoformat()[:-7], (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 0, 0), 1)

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

            cv2.putText(image, "Mov:" + str(int(tot_mov)), (0, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 0, 255), 1)

            atual = dt.datetime.now()
            delta = atual - self.anterior
            if delta.total_seconds() >= self.delay:
                self.anterior = atual

                if tot_mov != 0:
                    self.lastFrameMove = self.cache_frame
                else:
                    if self.lastFrameMove != 0:
                        self.lastFrameMove -= 1

                val = self.getRestApiJson(self.url_audi)
                if val[0] is True:
                    audience = val[1]
                    if 'hasAudience' in audience:
                        if audience['hasAudience'] is True:
                            cv2.imwrite(self.pathimg + '/{0}.jpg'.format(self.contador), image)
                            self.log.info('send imagem ' + str(self.contador))

                            ## Envio direto AWS
                            # ip_data = '18.212.73.83'
                            # ip_data = '127.0.0.1'
                            # comando1 = 'scp -i remota1.pem {0}.jpg ubuntu@{1}:~/FlaskStreaming/imgs/{0}.jpg'.format(self.contador, ip_data)
                            # execute_comando(comando1)

                            # Envio RestAPI
                            info = {}
                            info['date'] = dt.datetime.now().strftime("%Y%m%d%H%M%S_%f")
                            file = open(self.pathimg + '/{0}.jpg'.format(self.contador), mode='rb')

                            result = self.postRestApiDic(info, self.url_file, file)
                            if result[0] is False:
                                self.log.error('%s Envio %s', result[1], str(info['name']))

                            self.contador += 1
                            if self.contador >= self.maximg:
                                self.contador = 0
                        else:
                            self.log.info('no audience, sleeping....')
                            time.sleep(10)
                else:
                    self.log.error(val[1])
                    time.sleep(15)

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

    def getRestApiJson(self, url_methodo):
        """[Excuta um metodo GET recebendo un dictionary]
        Arguments:
            methodo {[string]} -- [nome do metodo]
        Returns:
            [dict] -- [dados do metodo]
        """
        msg_erro = ''
        try:
            response = requests.get(url=url_methodo)
            if response.ok is True:
                return True, response.json()
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
