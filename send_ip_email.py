#!/usr/bin/env python3
'''
Created on 20171130
Update on 20180326
@author: Eduardo Pagotto
 '''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

from email.mime.text import MIMEText
from datetime import datetime

import hashlib

from src.utils import load_config_app, gera_dados_ip, envia_email

# Adicionar com o comando crontab -e
# */1  *  *  *  * /home/desenv/Projetos/PyMoveDetect/send_ip_email.py

def verifica_ip_igual(dados_atuais, arquivo_verificador):
    '''
    Verifica se ouve alteracao no IP
    dados_atuais: dados de ips gerados
    arquivo_verificador: buffer que armazena os ips anteriores
    Retorno: True se os ips se mantem, False se ouve alguma alteracao
    '''
    try:
        with open(arquivo_verificador, 'r') as myfile_hash:
            data = myfile_hash.read()

            hash_arquivo = hashlib.md5(data.encode('UTF-8')).hexdigest()
            hash_ips_atuais = hashlib.md5(dados_atuais.encode('UTF-8')).hexdigest()

            if hash_arquivo == hash_ips_atuais:
                return True

            log.info('IP Alterado')

    except Exception:
        log.info('Arquivo com ip ainda nao existe')

    return False

if __name__ == '__main__':
    try:
        #carrega logger e configuracao
        config_data, logging = load_config_app('config/dados.yaml')
        log = logging.getLogger(__name__)

        elemento = config_data['email_setup']

        #Dados Device
        id_device = elemento['device']

        #Dados Email logon
        gmail_dados_usuario = (elemento['usuario'], elemento['senha'])

        #destino
        to = elemento['destino']

        log.info('Validar Configurações de rede')

        #adiquire dados de conexao
        lista_ips_txt = gera_dados_ip()

        #verifica se IP nao foi alterado
        if verifica_ip_igual(lista_ips_txt, '/tmp/IP_ATUAL_ENVIADO.txt') is False:
            msg = MIMEText(lista_ips_txt)
            msg['Subject'] = 'Novo IP Device {0} Data {1}'.format(id_device, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            msg['From'] = gmail_dados_usuario[0]
            msg['To'] = to
            envia_email(msg, [to], gmail_dados_usuario)

            with open('/tmp/IP_ATUAL_ENVIADO.txt', 'w') as myfile:
                myfile.write(lista_ips_txt)
                myfile.flush()
                log.info('Arquivo com ip Enviado')

    except Exception as expt:
        log.critical('Falha na validacao do IP:%s', str(expt))

    log.debug('Ip verificado')
