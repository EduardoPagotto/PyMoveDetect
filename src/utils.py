#!/usr/bin/env python3
'''
Created on 20171012
Update on 20171216
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

import json
import logging
import os

#mypath = os.path.abspath(__file__)
#baseDir = mypath[0:mypath.rfind("/")+1]
#baseFileName = mypath[mypath.rfind("/")+1:mypath.rfind(".")]
#progName = os.path.basename(__file__)

class ConfigFile(object):
    '''
    Setting de dados
    '''
    def __init__(self, nome_arquivo):
        '''
        Le dados de configuracao e inicializa arquiivos de log
        nome_arquivo: nome do arquivo totalmente qualificado
        retorno: dict com dados de configuracao
        '''
        self.dados_def = None
        with open(nome_arquivo, 'r') as configFile:
            self.dados_def = json.load(configFile)

        if self.dados_def['log']['kind'] == 'verbose':
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
        elif self.dados_def['log']['kind'] == 'save_log':
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S',
                                filename=self.dados_def['log']['log_file'],
                                filemode='w')
        else:
            print("Logging Disabled per Variable verbose=False")
            logging.basicConfig(level=logging.CRITICAL,
                                format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')

        image_path = self.dados_def['img_pat']
        if not os.path.isdir(image_path):
            logging.info("Creating Image Storage Folder %s", image_path)
            os.makedirs(image_path)

    def get(self):
        '''
        retorna dados
        '''
        return self.dados_def

    # def get(self, parametro):
    #     '''
    #     retorna dados
    #     '''
    #     if parametro in self.dados_def:
    #         return self.dados_def[parametro]

    #     logging.error('Parametro: %s nao existe', parametro)
    #     raise Exception('Paremetro: {0} nao exite'.format(parametro))
