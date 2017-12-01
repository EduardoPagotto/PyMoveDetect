#!/usr/bin/env python3
'''
Created on 20171130
Update on 20171130
@author: Eduardo Pagotto
 '''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

import subprocess
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

import logging
import logging.handlers

import hashlib
import json

# Adicionar com o comando crontab -e
# */1  *  *  *  * /home/desenv/Projetos/PyMoveDetect/send_ip_email.py

log = logging.getLogger('SendIP')
log.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address='/dev/log')
log.addHandler(handler)

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

def verifica_ip_igual(dados_atuais, arquivo_verificador):
    '''
    Verifica se ouve alteracao no IP
    dados_atuais: dados de ips gerados
    arquivo_verificador: buffer que armazena os ips anteriores
    Retorno: True se os ips se mantem, False se ouve alguma alteracao
    '''
    try:
        with open(arquivo_verificador, 'r') as myfile:
            data = myfile.read()

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

        elemento = None #
        with open("/home/desenv/Projetos/PyMoveDetect/dados.json", 'r') as fin:
        #with open("dados.json", 'r') as fin:
            elemento = json.load(fin)

        #Dados Device
        id_device = elemento['device']

        #Dados Email logon
        gmail_dados_usuario = (elemento['usuario'], elemento['senha'])

        #destino
        to = elemento['destino']

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
