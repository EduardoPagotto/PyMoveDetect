#!/usr/bin/env python3
'''
Created on 20171012
Update on 20171130
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703
#pylint: disable=R0913

import os
import datetime

#from config import *

import logging
import cv2
import time
#from threading import Thread
import threading

class canvas_img(object):

    CAMERA_WIDTH = 352    # default = 320 PiCamera image width can be greater if quad core RPI
    CAMERA_HEIGHT = 288   # default = 240 PiCamera image height
    CAMERA_HFLIP = False  # True=flip camera image horizontally
    CAMERA_VFLIP = False  # True=flip camera image vertically
    CAMERA_ROTATION = 0   # Rotate camera image valid values 0, 90, 180, 270
    CAMERA_FRAMERATE = 25 # default = 25 lower for USB Web Cam. Try different settings

    def __init__(self):

        self.x_center = CAMERA_WIDTH/2
        self.y_center = CAMERA_HEIGHT/2
        self.x_max = CAMERA_HEIGHT
        self.y_max = CAMERA_WIDTH
        self.x_buf = CAMERA_WIDTH/10
        self.y_buf = CAMERA_HEIGHT/10

    def crossed_x_centerline(self, enter, leave, movelist):
        xbuf = 20  # buffer space on either side of x_center to avoid extra counts
        # Check if over center line then count
        if len(movelist) > 1:  # Are there two entries
            if ( movelist[0] <= self.x_center
                    and  movelist[-1] > self.x_center + self.x_buf):
                leave += 1
                movelist = []
            elif ( movelist[0] > self.x_center
                    and  movelist[-1] < self.x_center - self.x_buf):
                enter += 1
                movelist = []
        return enter, leave, movelist

    def crossed_y_centerline(self, enter, leave, movelist):
        # Check if over center line then count
        if len(movelist) > 1:  # Are there two entries
            if ( movelist[0] <= self.y_center
                    and  movelist[-1] > self.y_center + self.y_buf ):
                leave += 1
                movelist = []
            elif ( movelist[0] > self.y_center
                    and  movelist[-1] < self.y_center - self.y_buf ):
                enter += 1
                movelist = []
        return enter, leave, movelist


# cores das linhas e textos do opencv
cvWhite = (255,255,255)
cvBlack = (0,0,0)
cvBlue = (255,0,0)
cvGreen = (0,255,0)
cvRed = (0,0,255)

color_mo = cvRed  # cor do circulo de trackeamento
color_txt = cvBlue   # cor do texto da linha central

font = cv2.FONT_HERSHEY_SIMPLEX
FRAME_COUNTER = 1000  
quote = '"'  

mypath=os.path.abspath(__file__)
baseDir=mypath[0:mypath.rfind("/")+1]
baseFileName=mypath[mypath.rfind("/")+1:mypath.rfind(".")]
progName = os.path.basename(__file__)

logFilePath = baseDir + baseFileName + ".log"
if verbose:
    print("carregando inteligencia artificial")
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
elif save_log:
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=logFilePath,
                    filemode='w')
else:
    print("Logging Disabled per Variable verbose=False")
    logging.basicConfig(level=logging.CRITICAL,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

if not os.path.isdir(image_path):
    logging.info("Creating Image Storage Folder %s", image_path )
    os.makedirs(image_path)

class PiVideoStream:
    def __init__(self, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=CAMERA_FRAMERATE, rotation=0, hflip=False, vflip=False):
        # inicializacao da camera
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.rotation = rotation
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

class FileVideoStream(object):
    '''Classe de stream do arquivo'''
    def __init__(self, device_cam, width, height):
        '''Inicializacao thread de video'''

        self._thead = threading.Thread(target=self.update, args=())
        self._thead.daemon = True
        self._stopped = False
        
        self._ao_vivo = isinstance( device_cam, int )

        self._stream = cv2.VideoCapture(device_cam)
        self._stream.set(3,width)
        self._stream.set(4,height)

        (self._grabbed, self._frame) = self._stream.read()

    def start(self):
        '''Ativa a Thread'''
        # start the thread to read frames from the video stream
        self._thead.start()
        return self

    def update(self):
        '''Atualiza status do video'''
        while True:
            if self._stopped:
                return
            
            if self._ao_vivo is False:
                time.sleep(0.037)#delay devido ao video continuo 1/27 (27FPS)

            #Le o proximo frame
            (self._grabbed, self._frame) = self._stream.read()


    def read(self):
        '''retorna o frame mais recente'''
        return self._frame

    def stop(self):
        '''Sinaliza parada da thread'''
        # indicate that the thread should be stopped
        self._stopped = True

# def crossed_y_centerline(enter, leave, movelist):
#     # Check if over center line then count
#     if len(movelist) > 1:  # Are there two entries
#         if ( movelist[0] <= y_center
#                    and  movelist[-1] > y_center + y_buf ):
#             leave += 1
#             movelist = []
#         elif ( movelist[0] > y_center
#                    and  movelist[-1] < y_center - y_buf ):
#             enter += 1
#             movelist = []
#     return enter, leave, movelist

def log_to_csv_file(data_to_append):
    log_file_path = baseDir + baseFileName + ".csv"
    if not os.path.exists(log_file_path):
        open( log_file_path, 'w' ).close()
        f = open( log_file_path, 'ab' )
        f.close()
        logging.info("Create New Data Log File %s", log_file_path )
    filecontents = data_to_append + "\n"
    f = open( log_file_path, 'a+' )
    f.write( filecontents )
    f.close()
    return

def show_FPS(start_time,frame_count):
    if debug:
        if frame_count >= FRAME_COUNTER:
            duration = float(time.time() - start_time)
            FPS = float(frame_count / duration)
            logging.info("Processing at %.2f fps last %i frames", FPS, frame_count)
            frame_count = 0
            start_time = time.time()
        else:
            frame_count += 1
    return start_time, frame_count

def get_image_name(path, prefix):
    # nome das imagens a serem salvas
    rightNow = datetime.datetime.now()
    filename = ("%s/%s-%04d%02d%02d-%02d%02d%02d.jpg" %
          ( path, prefix ,rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second ))
    return filename

def track2(vs):

    image1 = vs.read()   # initialize image1 (done once)
    try:
        grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    except:
        vs.stop()
        print("Problem Connecting To Camera Stream.")
        print("Restarting Camera.  One Moment Please .....")
        time.sleep(4)
        return

    if window_on:
        print("Press q in window Quits")
    else:
        print("Press ctrl-c to Quit")
    print("Start Tracking Enter Leave Activity ....")

    if not verbose:
        print("Note: Console Messages Suppressed per verbose=%s" % verbose)

    big_w = int(CAMERA_WIDTH * WINDOW_BIGGER)
    big_h = int(CAMERA_HEIGHT * WINDOW_BIGGER)
    cx, cy, cw, ch = 0, 0, 0, 0   # initialize contour center variables
    frame_count = 0  #initialize for show_fps
    start_time = time.time() #initialize for show_fps

    still_scanning = True
    movelist = []
    move_time = time.time()
    enter = 0
    leave = 0

    while still_scanning:
        # initialize variables
        motion_found = False
        biggest_area = MIN_AREA

        image2 = vs.read()  # initialize image2

        if ( WEBCAM_HFLIP and WEBCAM_VFLIP ):
            image2 = cv2.flip( image2, -1 )
        elif WEBCAM_HFLIP:
            image2 = cv2.flip( image2, 1 )
        elif WEBCAM_VFLIP:
            image2 = cv2.flip( image2, 0 )
                
        # if window_on:
        #     if centerline_vert:
        #         cv2.line( image2,( x_center, 60 ),( x_center, 200 ),color_txt, 2 )
        #     else:
        #         cv2.line( image2,( 0, y_center ),( x_max, y_center ),color_txt, 2 )

        grayimage2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        # Get differences between the two greyed images
        differenceimage = cv2.absdiff(grayimage1, grayimage2)
        grayimage1 = grayimage2  # save grayimage2 to grayimage1 ready for next image2
        differenceimage = cv2.blur(differenceimage,(BLUR_SIZE, BLUR_SIZE))
        # Get threshold of difference image based on THRESHOLD_SENSITIVITY variable
        retval, thresholdimage = cv2.threshold( differenceimage, THRESHOLD_SENSITIVITY, 255, cv2.THRESH_BINARY )
        try:
            thresholdimage, contours, hierarchy = cv2.findContours( thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
        except:
            contours, hierarchy = cv2.findContours( thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )

        if contours:
            total_contours = len(contours)  # Get total number of contours
            for c in contours:              # find contour with biggest area
                found_area = cv2.contourArea(c)  # get area of next contour
                # find the middle of largest bounding rectangle
                if found_area > biggest_area:
                    motion_found = True
                    biggest_area = found_area
                    (x, y, w, h) = cv2.boundingRect(c)
                    cx = int(x + w/2)   # put circle in middle of width
                    cy = int(y + h/2)   # put circle in middle of height
                    cw, ch = w, h

            if motion_found:
                move_timer = time.time() - move_time
                if (move_timer >= movelist_timeout):
                    movelist = []
                    #logging.info("Exceeded %.2f Seconds - Clear movelist" % movelist_timeout)
                move_time = time.time()

                old_enter = enter
                old_leave = leave
                if centerline_vert:
                    movelist.append(cx)
                    enter, leave, movelist = crossed_x_centerline(enter, leave, movelist)
                else:
                    movelist.append(cy)
                    enter, leave, movelist = crossed_y_centerline(enter, leave, movelist)

                if not movelist:
                    if enter > old_enter:
                        if inout_reverse:   # reverse enter leave if required
                            prefix = "leave"
                        else:
                            prefix = "enter"
                    elif leave > old_leave:
                        if inout_reverse:
                            prefix = enter
                        else:
                            prefix = "leave"
                    else:
                        prefix = "error"

                    if inout_reverse:
                        logging.info("leave=%i enter=%i Diff=%i" % ( leave, enter, abs(enter-leave)))
                    else:
                        logging.info("enter=%i leave=%i Diff=%i" % ( enter, leave, abs(enter-leave)))

                    # Save image
                    if save_images:
                        filename = get_image_name( image_path, prefix)
                        save_image = vs.read()
                        logging.info("Save: %s", filename)
                        cv2.imwrite(filename, save_image)

                    # Save data to csv file
                    if save_CSV:
                        log_time = datetime.datetime.now()
                        log_csv_time = ("%s%04d%02d%02d%s,%s%02d%s,%s%02d%s,%s%02d%s" %
                                       ( quote, log_time.year, log_time.month,
                                         log_time.day, quote,
                                         quote, log_time.hour, quote,
                                         quote, log_time.minute, quote,
                                         quote, log_time.second, quote ))

                        log_csv_text = ("%s,%s%s%s,%s%s%s,%i,%i,%i,%i,%i" %
                                    ( log_csv_time,
                                      quote, prefix, quote,
                                      quote, filename, quote,
                                      cx, cy, cw, ch, cw * ch ))
                        log_to_csv_file( log_csv_text )

                if window_on:
                    # show small circle at motion location
                    if SHOW_CIRCLE and motion_found:
                        cv2.circle(image2,(cx,cy),CIRCLE_SIZE,(color_mo), LINE_THICKNESS)
                    else:
                        cv2.rectangle(image2,(cx,cy),(x+cw,y+ch),(color_mo), LINE_THICKNESS)

                if show_moves:
                    logging.info("cx,cy(%i,%i) C:%2i A:%ix%i=%i SqPx" %
                                      (cx ,cy, total_contours, cw, ch, biggest_area))

        if show_fps:
            start_time, frame_count = show_FPS(start_time, frame_count)

        if window_on:

            if inout_reverse:
                img_text = ("saida %i          entrada %i" % (leave, enter))
            else:
                img_text = ("entrada %i          saida %i" % (enter, leave))
            cv2.putText( image2, img_text, (35,15), font, font_scale,(color_txt),1)

            if diff_window_on:
                cv2.imshow('Difference Image',differenceimage)
            if thresh_window_on:
                cv2.imshow('OpenCV Threshold', thresholdimage)
            if WINDOW_BIGGER > 1:  # Note setting a bigger window will slow the FPS
                image3 = cv2.resize( image2,( big_w, big_h ))
            cv2.imshow('pressione q para sair)', image3)

            # Close Window if q pressed while mouse over opencv gui window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                vs.stop()
                print("encerrando sistema")
                quit(0)
#https://askubuntu.com/questions/83161/use-ffmpeg-to-transform-mp4-to-same-high-quality-avi-file
def track(vs):
    while True:
        image1 = vs.read()   # initialize image1 (done once)

        if image1 is not None:
            try:
                grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)#cv2.COLOR_YUV420p2GRAY)

                cv2.imshow('frame',grayimage1)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            except:
                vs.stop()
                print("Problem Connecting To Camera Stream.")
                print("Restarting Camera.  One Moment Please .....")
                time.sleep(4)
            #return
        else:
            time.sleep(1)
            print('espera...')


if __name__ == '__main__':
    while True:
        try:
            
            print("Inicializando Video ....")
            vs = FileVideoStream('/home/locutus/Projetos/PyMoveDetect/video/VID_20171021_144029337.mp4',
                                  CAMERA_WIDTH,
                                  CAMERA_HEIGHT)

            # print("Inicializando USB webcam ....")
            # vs = FileVideoStream(0,
            #                      CAMERA_WIDTH,
            #                      CAMERA_HEIGHT)

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
