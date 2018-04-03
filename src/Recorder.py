#!/usr/bin/env python3
'''
Created on 20180326
Update on 20180326
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

import logging
import cv2

class Recorder(object):
    '''
    Classe de gravador de video
    '''
    def __init__(self, file_name, fps, dim, codec):
        '''
        Inicializa Gravador com dados da midia
        file_name: nome do arquivo
        fps: frames por segundo
        dim: dimenção em tupla (wxh)
        codec: nome do codec
        '''
        self.count_frame = 0
        self.codec = codec
        #inicializa encode para gravação de video
        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        self.out = cv2.VideoWriter(file_name, fourcc, fps, dim, True)

        self.log = logging.getLogger(__name__)
        self.log.info('Recorder arquivo:%s configurado', file_name)

    def write_frame(self, frame, count_frame):
        '''
        Grava o frame corrente no arquiv de midia
        frame: imagem a ser gravada
        count_frame: sequencial do frame
        return: True se frame novo
        '''
        if count_frame != self.count_frame:
            self.out.write(frame)
            self.count_frame = count_frame
            return True
        #else:
        #    print('pulei')
        #compactar com:
        #ffmpeg -i output.avi -b:v 200k -c:v libx264 -vf scale=640:480 -pix_fmt yuv420p -c:a aac -strict experimental -b:a 128k -ac 2 -an -threads 2 -f mp4 output2.mp4
        return False

    def close(self):
        '''
        Fecha o arquivo de midia
        '''
        self.out.release()
        self.log.info('Recoder finalizado')

def get_recorder(config_global):
    '''
    Identifica se ha gravador pelo dict
    config_global: dictionary com os dados
    retorn: se ha recorder no arquivo de configuração carregar na memoria
    '''
    if 'recorder' in config_global:
        conf_rec = config_global['recorder']
        return Recorder(conf_rec['output_file'], conf_rec['fps'], (conf_rec['width'], conf_rec['height']), conf_rec['codec'])

    return None
