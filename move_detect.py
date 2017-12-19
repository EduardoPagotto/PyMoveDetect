#!/usr/bin/env python3
'''
Created on 20171012
Update on 20171216
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

#import os
import datetime

import logging
import cv2
import time
#import threading

from CanvasImg import CanvasImg 
from MoveEntity import MoveEntity
from VideoStreamDev import VideoStreamDev
from ConfigFile import ConfigFile

# cores das linhas e textos do opencv
cvWhite = (255, 255, 255)
cvBlack = (0, 0, 0)
cvBlue = (255, 0, 0)
cvGreen = (0, 255, 0)
cvRed = (0, 0, 255)

color_mo = cvRed  # cor do circulo de trackeamento
color_txt = cvBlue   # cor do texto da linha central

#font = cv2.FONT_HERSHEY_SIMPLEX
FRAME_COUNTER = 1000
quote = '"'

# def log_to_csv_file(data_to_append):
#     log_file_path = baseDir + baseFileName + ".csv"
#     if not os.path.exists(log_file_path):
#         open( log_file_path, 'w' ).close()
#         f = open( log_file_path, 'ab' )
#         f.close()
#         logging.info("Create New Data Log File %s", log_file_path )
#     filecontents = data_to_append + "\n"
#     f = open( log_file_path, 'a+' )
#     f.write( filecontents )
#     f.close()
#     return

# def show_FPS(start_time,frame_count):
#     if debug:
#         if frame_count >= FRAME_COUNTER:
#             duration = float(time.time() - start_time)
#             FPS = float(frame_count / duration)
#             logging.info("Processing at %.2f fps last %i frames", FPS, frame_count)
#             frame_count = 0
#             start_time = time.time()
#         else:
#             frame_count += 1
#     return start_time, frame_count

def get_image_name(path, prefix):
    # nome das imagens a serem salvas
    rightNow = datetime.datetime.now()
    filename = ("%s/%s-%04d%02d%02d-%02d%02d%02d.jpg" % (path, prefix, rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second))
    return filename

def track2(vs, mv):

    grayimage1 = vs.get_gray_image()
    if vs.canvas.windows_on:
        logging.info('pressione q para sair')
    else:
        logging.info('precione crt-c para sair')


    logging.info('A iniciar tracking...')

    #big_w, big_h = canvas_img.get_bigger()

    cx, cy, cw, ch = 0, 0, 0, 0   # initialize contour center variables
    frame_count = 0  #initialize for show_fps
    start_time = time.time() #initialize for show_fps

    still_scanning = True

    move_time = time.time()

    while still_scanning:

        #FIXME mudei a ordem da aquisicao do get com o gray
        grayimage2 = vs.get_gray_image()#cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

        mv.detect_area(grayimage1, grayimage2, move_time)

        grayimage1 = grayimage2

if __name__ == '__main__':

    try:
        cf = ConfigFile('config/config.json')
    except Exception as exp:
        print('Erro Critico identificado no loadas de config')

    while True:
        try:

            canvas_img = CanvasImg(cf.get()['canvas'])

            mv = MoveEntity(canvas_img, cf.get()['move_entity'])

            logging.info("Inicializando Video device....")
            vs = VideoStreamDev(cf.get()['video_device'], canvas_img, cf.get()['debug'])

            # print("Inicializando USB webcam ....")
            #vs = VideoStreamDev(0, canvas_img.CAMERA_WIDTH, canvas_img.CAMERA_HEIGHT)

            vs.start()
            time.sleep(4)

            track2(vs, mv)

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
            break

    print('FIM')
