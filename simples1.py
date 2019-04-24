#!/usr/bin/env python3
'''
Created on 20190322
Update on 20190322
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

import time
import cv2
from src.VideoStreamDev import VideoStreamDev

if __name__ == '__main__':

    stream = VideoStreamDev(0, 640, 480)
    stream.start()

    contador = 0

    try:

        while True:
            frame, image = stream.read()

            if image is None:
                time.sleep(0.04)
                continue

            if frame > contador:
                cv2.putText(image, "FPS : " + str(int(stream.fps)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)
                cv2.imshow('pressione q para sair', image)
                frame = contador
            else:
                time.sleep(0.04)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("User Pressed Keyboard ctrl-c")
    except Exception as exp:
        print('ERRO:%s',str(exp))
    finally:
        stream.stop()
        cv2.destroyAllWindows()