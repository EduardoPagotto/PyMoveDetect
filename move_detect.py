#!/usr/bin/env python3
'''
Created on 20171012
Update on 20171226
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

import datetime
import logging
import time
import cv2

from CanvasImg import CanvasImg
from MoveDetect import MoveDetect
from VideoStreamDev import VideoStreamDev
from ConfigFile import ConfigFile

# cores das linhas e textos do opencv
# cvWhite = (255, 255, 255)
# cvBlack = (0, 0, 0)
# cvBlue = (255, 0, 0)
# cvGreen = (0, 255, 0)
# cvRed = (0, 0, 255)
#color_mo = cvRed  # cor do circulo de trackeamento
#color_txt = cvBlue   # cor do texto da linha central

# def exibir(vs):
#     while True:
#         imagem = vs.read()
#         cv2.imshow('Exibir',imagem)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             cv2.destroyAllWindows()
#             vs.stop()
#             print("encerrando sistema")
#             quit(0)

def track2(vs, mv):
    '''
    executa o tracking basico
    '''
    logging.info('A iniciar tracking...')

    grayimage1 = vs.get_gray_image()
    still_scanning = True

    while still_scanning:

        #le imagem colorida inteira
        image = vs.read()

        #converte para GRAY
        grayimage2 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Start timer
        timer = cv2.getTickCount()

        #retorna a lista de movimentos detectados nao normalizada
        # TODO: criar normalização de movimento para fluidez e correto posicionamento 
        lista = mv.detect(grayimage1, grayimage2, time.time())
        tot_mov = len(lista)

        # Calcula o FPS (FPS)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
        cv2.putText(image, "FPS : " + str(int(fps)), (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(image, "Entidades : " + str(int(tot_mov)), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        #se há movimento desenhe retangulos e ajuste o FPS na Tela
        if tot_mov > 0:
            logging.debug('FPS: %d, Total Movimento: %d', fps, tot_mov)
            for entidade in lista:
                entidade.draw_rectangle(image)
        
        #ajusta o tamanho da imagem de teste
        image_final = cv2.resize(image, (vs.canvas.width, vs.canvas.height))
        cv2.imshow('pressione q para sair', image_final)

        #para a imagem 2 para a imagem 1 para re-captura de frame
        grayimage1 = grayimage2

        #espera tela de saida para fechar app 
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            still_scanning = False
            logging.info("encerrando sistema")


if __name__ == '__main__':

    try:
        #le configuracoes
        cf = ConfigFile('config/config.json')
    except Exception as exp:
        print('Erro Critico identificado no loadas de config')

    try:
        canvas_img = CanvasImg(cf.get()['canvas'])

        #mv = MoveEntity(canvas_img, cf.get()['move_entity'])
        mv = MoveDetect(cf.get()['move_entity'])

        logging.info("Inicializando Video device....")
        vs = VideoStreamDev(cf.get()['video_device'], canvas_img, cf.get()['debug'])

        # print("Inicializando USB webcam ....")
        #vs = VideoStreamDev(0, canvas_img.CAMERA_WIDTH, canvas_img.CAMERA_HEIGHT)

        vs.start()
        #time.sleep(1)
        #exibir(vs)
        track2(vs, mv)

        vs.stop()

    except KeyboardInterrupt:
        vs.stop()
        print("")
        print("+++++++++++++++++++++++++++++++++++")
        print("User Pressed Keyboard ctrl-c")
        # print("%s %s - Exiting" % (progname, ver))
        print("+++++++++++++++++++++++++++++++++++")
        print("")
        quit(0)
    except Exception as exp:
        print('Erro:{0}'.format(str(exp)))

    print('FIM')
