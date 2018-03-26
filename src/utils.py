#!/usr/bin/env python3
'''
Created on 20171012
Update on 20171216
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

#import json
import logging
import logging.config
import os

import subprocess

import yaml

import smtplib
from email.mime.text import MIMEText

#mypath = os.path.abspath(__file__)
#baseDir = mypath[0:mypath.rfind("/")+1]
#baseFileName = mypath[mypath.rfind("/")+1:mypath.rfind(".")]
#progName = os.path.basename(__file__)

def load_config_app(config_file):
    '''
    Carrega configuração do arquivo YAML
    config_file: pathfile do arquivo de configuração
    returno: Tupla (dict,log) dictionary com configuracao e loggin
    '''
    with open(config_file) as stream:
        try:
            global_config = yaml.load(stream)
            dados_log = global_config['loggin']
            logging.config.dictConfig(dados_log)
            #log = logging.getLogger(__name__)
            return global_config, logging
        except yaml.YAMLError as exc:
            print(exc)
            quit()
        except Exception as exp:
            print(str(exp))
            quit()

def gera_dados_ip():
    '''
    Consulta SO para dados de Conexao,
    retornando texto com rota default e interfaces conectadas
    '''
    #call subprocess piped
    p = subprocess.Popen('ip route list', shell=True, stdout=subprocess.PIPE)
    data = p.communicate()

    #filtra linhas
    texto = data[0].decode('UTF-8')
    linhas = texto.split('\n')

    #retorno inicia vazio
    retorno_ips = ''

    for linha in linhas:
        tamanho_linha = len(linha)
        inicio = linha.find('default ', 0, tamanho_linha)
        linha = linha.replace('  ', ' ')
        itens = linha.split(' ')
        if inicio != -1:
            #defaul Route
            retorno_ips += 'Rota {0} {1}\n'.format(itens[4], itens[2])
            continue

        if len(itens) > 8:
            #dev com IP
            retorno_ips += 'IP {0} {1}\n'.format(itens[2], itens[8])

    return retorno_ips

def envia_email(payload, lista_destino, user_data):
    '''
    Envia Email ao GMAIL
    payload : msg a ser enviada
    lista_destino : lista de destinatatios
    user_data : tupla com usuario e senha
    '''
    smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(user_data[0], user_data[1])
    smtpserver.sendmail(user_data[0], lista_destino, payload.as_string())
    smtpserver.quit()