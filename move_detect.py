#!/usr/bin/env python3
'''
Created on 20171012
Update on 20171228
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

import logging
import time
import cv2

from CanvasImg import CanvasImg
from MoveDetect import MoveDetect, Entidade, classificador
from VideoStreamDev import VideoStreamDev
from ConfigFile import ConfigFile

# cores das linhas e textos do opencv
# cvWhite = (255, 255, 255)
# cvBlack = (0, 0, 0)
# cvBlue = (255, 0, 0)
# cvGreen = (0, 255, 0)
# cvRed = (0, 0, 255)

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

        #inicializa encode para gravação de video
        fourcc = cv2.VideoWriter_fourcc('D','I','V','3') # MPEG 4.3
        #fourcc = cv2.VideoWriter_fourcc('M','P','4','2') # MPEG 4.2
        #fourcc = cv2.VideoWriter_fourcc('M','J','P','G') # Motion Jpeg
        #fourcc = cv2.VideoWriter_fourcc('U','2','6','3') # H263
        #fourcc = cv2.VideoWriter_fourcc('I','2','6','3') # H263I
        #fourcc = cv2.VideoWriter_fourcc('F','L','V','1') # FLV
        #fourcc = cv2.VideoWriter_fourcc('P','I','M','1') # MPEG-1
        #fourcc = cv2.VideoWriter_fourcc('D','I','V','X') # MPEG-4 = MPEG-1
        #fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('output.avi',fourcc, 20.0, (800,640), True)

        logging.info('Captura Primeiro Frame')
        move.start_frame()

        count = stream._frame_count

        while True:

            lista_crua = move.detect(time.time())

            lista = classificador(lista_crua, 0, canvas_img.width, canvas_img.height)

            tot_mov = len(lista)

            image = move.image

            cv2.putText(image, "FPS : " + str(int(stream.fps)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)

            alerta_area1 = 0
            alerta_area2 = 0

            alert1 = Entidade(str(1), 80, 180, 150, 100, None)
            alert1.prefix_texo = 'Detect Area'

            alert2 = Entidade(str(2), 575, 300, 150, 150, None)
            alert2.prefix_texo = 'Detect Area'

            #se há movimento desenhe retangulos e ajuste o FPS na Tela
            if tot_mov > 0:
                cv2.putText(image, "Entidades : " + str(int(tot_mov)), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
                for entidade in lista:
                    entidade.draw_rectangle(image)

                    if alert1.is_collide(entidade, 0, canvas_img.width, canvas_img.height) is True:
                        alert1.cor_retangulo = (0, 0, 255)
                        break

                    if alert2.is_collide(entidade, 0, canvas_img.width, canvas_img.height) is True:
                        alert2.cor_retangulo = (0, 0, 255)
                        break

            alert1.draw_rectangle(image)
            alert2.draw_rectangle(image)
  
            novo = stream._frame_count
            if novo != count:
                out.write(image)
                count = novo
            # else:
            #     print('pulei')
            #compactar com:
            #ffmpeg -i output.avi -b:v 200k -c:v libx264 -vf scale=640:480 -pix_fmt yuv420p -c:a aac -strict experimental -b:a 128k -ac 2 -an -threads 2 -f mp4 output2.mp4

            cv2.imshow('pressione q para sair', image)
            
            #if move.differenceimage is not None:
            #    cv2.imshow('differenceimage', move.differenceimage)

            #if move.thresholdimage is not None:
            #    cv2.imshow('thresholdimage', move.thresholdimage)

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

        out.release()

        cv2.destroyAllWindows()

    print('FIM')
