#!/usr/bin/env python3
'''
Created on 20171012
Update on 20171227
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

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

if __name__ == '__main__':

    #le configuracoes gerais, sai se falha
    try:
        cf = ConfigFile('config/config.json')
    except Exception as exp:
        print('Erro Critico identificado no loadas de config')
        quit()

    try:
        canvas_img = CanvasImg(cf.get()['canvas'])

        logging.info("A iniciar Thread Video device....")
        stream = VideoStreamDev(cf.get()['video_device'], canvas_img.width, canvas_img.height)
        stream.start()

        logging.info('A inicializar detector de movimento')
        move = MoveDetect(stream, canvas_img.width, canvas_img.height, cf.get()['move_entity'])

        logging.info('Captura Primeiro Frame')
        move.start_frame()

        while True:

            lista = move.detect(time.time())
            tot_mov = len(lista)

            image = move.image

            cv2.putText(image, "FPS : " + str(int(stream.fps)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)

            #se há movimento desenhe retangulos e ajuste o FPS na Tela
            if tot_mov > 0:
                cv2.putText(image, "Entidades : " + str(int(tot_mov)), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
                for entidade in lista:
                    entidade.draw_rectangle(image)

            cv2.imshow('pressione q para sair', image)

            if move.differenceimage is not None:
                cv2.imshow('differenceimage', move.differenceimage)

            if move.thresholdimage is not None:
                cv2.imshow('thresholdimage', move.thresholdimage)

            #espera tela de saida para fechar app
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("encerrando sistema")
                break

    except KeyboardInterrupt:
        print("")
        print("+++++++++++++++++++++++++++++++++++")
        print("User Pressed Keyboard ctrl-c")
        # print("%s %s - Exiting" % (progname, ver))
        print("+++++++++++++++++++++++++++++++++++")
        print("")
    except Exception as exp:
        print('Erro:{0}'.format(str(exp)))
    finally:
        stream.stop()
        time.sleep(1)
        cv2.destroyAllWindows()

    print('FIM')
