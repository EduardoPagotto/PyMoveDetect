#!/usr/bin/env python3
'''
Created on 20171217
Update on 20171218
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

import time
import logging
import cv2

from CanvasImg import CanvasImg

class MoveEntity(object):
    '''
    Classe de Movimentos detectados
    '''
    def __init__(self, canvas, config_settings):
        self.bigger = config_settings['bigger']
        self.min_area = config_settings['min_area']
        self.blur_size = config_settings['blur_size']
        self.threshold_sensitivity = config_settings['threshold_sensitivity']

        self.movelist_timeout = config_settings['movelist_timeout']
        self.inout_reverse = config_settings['inout_reverse']

        self.canvas = canvas
        #self.big_w = int(w * self.bigger)
        #self.big_h = int(h * self.bigger)

    def crossed_x_centerline(self, enter, leave, movelist):
        '''
        Determina se cruza o meio em X
        '''
        #xbuf = 20  # buffer space on either side of x_center to avoid extra counts
        # Check if over center line then count
        if len(movelist) > 1:  # Are there two entries
            if movelist[0] <= self.canvas.x_center and  movelist[-1] > self.canvas.x_center + self.canvas.x_buf:
                leave += 1
                movelist = []
            elif movelist[0] > self.canvas.x_center and  movelist[-1] < self.canvas.x_center - self.canvas.x_buf:
                enter += 1
                movelist = []

        return enter, leave, movelist

    def crossed_y_centerline(self, enter, leave, movelist):
        '''
        Determina se cruza o meio em Y
        '''
        # Check if over center line then count
        if len(movelist) > 1:  # Are there two entries
            if movelist[0] <= self.canvas.y_center and  movelist[-1] > self.canvas.y_center + self.canvas.y_buf:
                leave += 1
                movelist = []
            elif movelist[0] > self.canvas.y_center and  movelist[-1] < self.canvas.y_center - self.canvas.y_buf:
                enter += 1
                movelist = []
        return enter, leave, movelist


    def detect_area(self, grayimage1, grayimage2, move_time_inicial):

        #FIXME usar o nome correto da variavel
        biggest_area = self.min_area

        move_time = move_time_inicial

        motion_found = False

        # Get differences between the two greyed images
        differenceimage = cv2.absdiff(grayimage1, grayimage2)
        differenceimage = cv2.blur(differenceimage, (self.blur_size, self.blur_size))

        # Get threshold of difference image based on THRESHOLD_SENSITIVITY variable
        retval, thresholdimage = cv2.threshold(differenceimage, self.threshold_sensitivity, 255, cv2.THRESH_BINARY)
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
                if (move_timer >= self.movelist_timeout):  #se ficar mais de um tempo determinado sem movimento apaga alista !!!!!!!(MUDAR)
                    movelist = []
                    #logging.info("Exceeded %.2f Seconds - Clear movelist" % movelist_timeout)
                move_time = time.time()

                old_enter = enter
                old_leave = leave
                if centerline_vert:
                    movelist.append(cx)
                    enter, leave, movelist = self.crossed_x_centerline(enter, leave, movelist)
                else:
                    movelist.append(cy)
                    enter, leave, movelist = self.crossed_y_centerline(enter, leave, movelist)

                if not movelist:
                    if enter > old_enter:
                        if self.inout_reverse:   # reverse enter leave if required
                            prefix = "leave"
                        else:
                            prefix = "enter"
                    elif leave > old_leave:
                        if self.inout_reverse:
                            prefix = enter
                        else:
                            prefix = "leave"
                    else:
                        prefix = "error"

                    if self.inout_reverse:
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