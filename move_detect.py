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

def track2(vs):
    me = MoveEntity()
    grayimage1 = vs.get_gray_image()

    if vs.canvas.windows_on:
        logging.info('pressione q para sair')
    else:
        logging.info('precione crt-c para sair')


    logging.info('A iniciar tracking...')

    big_w, big_h = canvas_img.get_bigger()

    cx, cy, cw, ch = 0, 0, 0, 0   # initialize contour center variables
    frame_count = 0  #initialize for show_fps
    start_time = time.time() #initialize for show_fps

    still_scanning = True
    movelist = []
    move_time = time.time()
    enter = 0
    leave = 0

#     while still_scanning:
#         # initialize variables
#         motion_found = False
#         biggest_area = MIN_AREA

#         image2 = vs.read()  # initialize image2

#         if ( WEBCAM_HFLIP and WEBCAM_VFLIP ):
#             image2 = cv2.flip( image2, -1 )
#         elif WEBCAM_HFLIP:
#             image2 = cv2.flip( image2, 1 )
#         elif WEBCAM_VFLIP:
#             image2 = cv2.flip( image2, 0 )
                
#         # if window_on:
#         #     if centerline_vert:
#         #         cv2.line( image2,( x_center, 60 ),( x_center, 200 ),color_txt, 2 )
#         #     else:
#         #         cv2.line( image2,( 0, y_center ),( x_max, y_center ),color_txt, 2 )

#         grayimage2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
#         # Get differences between the two greyed images
#         differenceimage = cv2.absdiff(grayimage1, grayimage2)
#         grayimage1 = grayimage2  # save grayimage2 to grayimage1 ready for next image2
#         differenceimage = cv2.blur(differenceimage,(BLUR_SIZE, BLUR_SIZE))
#         # Get threshold of difference image based on THRESHOLD_SENSITIVITY variable
#         retval, thresholdimage = cv2.threshold( differenceimage, THRESHOLD_SENSITIVITY, 255, cv2.THRESH_BINARY )
#         try:
#             thresholdimage, contours, hierarchy = cv2.findContours( thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
#         except:
#             contours, hierarchy = cv2.findContours( thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )

#         if contours:
#             total_contours = len(contours)  # Get total number of contours
#             for c in contours:              # find contour with biggest area
#                 found_area = cv2.contourArea(c)  # get area of next contour
#                 # find the middle of largest bounding rectangle
#                 if found_area > biggest_area:
#                     motion_found = True
#                     biggest_area = found_area
#                     (x, y, w, h) = cv2.boundingRect(c)
#                     cx = int(x + w/2)   # put circle in middle of width
#                     cy = int(y + h/2)   # put circle in middle of height
#                     cw, ch = w, h

#             if motion_found:
#                 move_timer = time.time() - move_time
#                 if (move_timer >= movelist_timeout):
#                     movelist = []
#                     #logging.info("Exceeded %.2f Seconds - Clear movelist" % movelist_timeout)
#                 move_time = time.time()

#                 old_enter = enter
#                 old_leave = leave
#                 if centerline_vert:
#                     movelist.append(cx)
#                     enter, leave, movelist = crossed_x_centerline(enter, leave, movelist)
#                 else:
#                     movelist.append(cy)
#                     enter, leave, movelist = crossed_y_centerline(enter, leave, movelist)

#                 if not movelist:
#                     if enter > old_enter:
#                         if inout_reverse:   # reverse enter leave if required
#                             prefix = "leave"
#                         else:
#                             prefix = "enter"
#                     elif leave > old_leave:
#                         if inout_reverse:
#                             prefix = enter
#                         else:
#                             prefix = "leave"
#                     else:
#                         prefix = "error"

#                     if inout_reverse:
#                         logging.info("leave=%i enter=%i Diff=%i" % ( leave, enter, abs(enter-leave)))
#                     else:
#                         logging.info("enter=%i leave=%i Diff=%i" % ( enter, leave, abs(enter-leave)))

#                     # Save image
#                     if save_images:
#                         filename = get_image_name( image_path, prefix)
#                         save_image = vs.read()
#                         logging.info("Save: %s", filename)
#                         cv2.imwrite(filename, save_image)

#                     # Save data to csv file
#                     if save_CSV:
#                         log_time = datetime.datetime.now()
#                         log_csv_time = ("%s%04d%02d%02d%s,%s%02d%s,%s%02d%s,%s%02d%s" %
#                                        ( quote, log_time.year, log_time.month,
#                                          log_time.day, quote,
#                                          quote, log_time.hour, quote,
#                                          quote, log_time.minute, quote,
#                                          quote, log_time.second, quote ))

#                         log_csv_text = ("%s,%s%s%s,%s%s%s,%i,%i,%i,%i,%i" %
#                                     ( log_csv_time,
#                                       quote, prefix, quote,
#                                       quote, filename, quote,
#                                       cx, cy, cw, ch, cw * ch ))
#                         log_to_csv_file( log_csv_text )

#                 if window_on:
#                     # show small circle at motion location
#                     if SHOW_CIRCLE and motion_found:
#                         cv2.circle(image2,(cx,cy),CIRCLE_SIZE,(color_mo), LINE_THICKNESS)
#                     else:
#                         cv2.rectangle(image2,(cx,cy),(x+cw,y+ch),(color_mo), LINE_THICKNESS)

#                 if show_moves:
#                     logging.info("cx,cy(%i,%i) C:%2i A:%ix%i=%i SqPx" %
#                                       (cx ,cy, total_contours, cw, ch, biggest_area))

#         if show_fps:
#             start_time, frame_count = show_FPS(start_time, frame_count)

#         if window_on:

#             if inout_reverse:
#                 img_text = ("saida %i          entrada %i" % (leave, enter))
#             else:
#                 img_text = ("entrada %i          saida %i" % (enter, leave))
#             cv2.putText( image2, img_text, (35,15), font, font_scale,(color_txt),1)

#             if diff_window_on:
#                 cv2.imshow('Difference Image',differenceimage)
#             if thresh_window_on:
#                 cv2.imshow('OpenCV Threshold', thresholdimage)
#             if WINDOW_BIGGER > 1:  # Note setting a bigger window will slow the FPS
#                 image3 = cv2.resize( image2,( big_w, big_h ))
#             cv2.imshow('pressione q para sair)', image3)

#             # Close Window if q pressed while mouse over opencv gui window
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 cv2.destroyAllWindows()
#                 vs.stop()
#                 print("encerrando sistema")
#                 quit(0)

#https://askubuntu.com/questions/83161/use-ffmpeg-to-transform-mp4-to-same-high-quality-avi-file
# def track(vs):
#     while True:
#         image1 = vs.read()   # initialize image1 (done once)

#         if image1 is not None:
#             try:
#                 grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)#cv2.COLOR_YUV420p2GRAY)

#                 cv2.imshow('frame',grayimage1)
#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                     break
                    
#             except:
#                 vs.stop()
#                 print("Problem Connecting To Camera Stream.")
#                 print("Restarting Camera.  One Moment Please .....")
#                 time.sleep(4)
#             #return
#         else:
#             time.sleep(1)
#             print('espera...')


if __name__ == '__main__':

    cf = None
    canvas_img = None
    vs = None

    try:
        cf = ConfigFile('config/config.json')

    except Exception as exp:
        print('Erro Critico identificado no loadas de config')

    while True:
        try:

            canvas_img = CanvasImg(cf.get()['canvas'])

            logging.info("Inicializando Video device....")
            vs = VideoStreamDev(cf.get()['video_device'], canvas_img, cf.get()['debug'])

            # print("Inicializando USB webcam ....")
            #vs = VideoStreamDev(0, canvas_img.CAMERA_WIDTH, canvas_img.CAMERA_HEIGHT)

            vs.start()
            time.sleep(4)

            track2(vs)

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
