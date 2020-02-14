#!/usr/bin/env python3
'''
Created on 20171012
Update on 20200214
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703
import time
import cv2

from src.utils import load_config_app
from src.MoveWrapper import MoveWrapper

#from src.CanvasImg import CanvasImg
#from src.VideoStreamDev import VideoStreamDev
#from src.MoveDetect import MoveDetect, Entidade, classificador
#from src.Recorder import Recorder, get_recorder

# cores das linhas e textos do opencv
# cvWhite = (255, 255, 255)
# cvBlack = (0, 0, 0)
# cvBlue = (255, 0, 0)
# cvGreen = (0, 255, 0)
# cvRed = (0, 0, 255)

if __name__ == '__main__':

    #le configuracoes gerais, sai se falha
    config_global, logging = load_config_app('./config/config.yaml')

    log = logging.getLogger(__name__)
    log.info('Detector de movimento à inicializar')

    mv = MoveWrapper(config_global)
    mv.start()

    try:
        contador = 0
        while True:

            image = mv.capture()
            if image is not None:
                cv2.imshow('pressione q para sair', image)

                #cv2.imwrite('img_{0}.jpg'.format(contador), image)
                #contador +=1

                # (flag, encodedImage) = cv2.imencode(".jpg", image)

                # if not flag:
                #     continue

                #yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
                #raw = (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

                # with open("img_{0}.jpg".format(contador), 'w') as f:
                #     f.write(encodedImage)

            # else:
            #     time.sleep(0.1)
            #     log.info('vazio')

            #if move.differenceimage is not None:
            #    cv2.imshow('differenceimage', move.differenceimage)

            #if move.thresholdimage is not None:
            #    cv2.imshow('thresholdimage', move.thresholdimage)

            #espera tela de saida para fechar app
            if cv2.waitKey(1) & 0xFF == ord('q'):
                log.info("encerrando sistema")
                break

    except KeyboardInterrupt:

        log.info("User Pressed Keyboard ctrl-c")

    except Exception as exp:

        log.fatal('ERRO:%s', str(exp))

    finally:

        mv.stop()

        cv2.destroyAllWindows()

    log.info('FIM App')
