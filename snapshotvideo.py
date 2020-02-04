'''
Created on 20200202
Update on 20200202
@author: Eduardo Pagotto
'''

import subprocess
import time

def execute_comando(comando):
    separado = comando.split(' ')
    proc = subprocess.Popen(separado,
                            #shell=True,
                            #preexec_fn=os.setsid,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    proc.wait()
    #logging.debug('Comando: %s status: %d', comando, proc.returncode)
    return proc.returncode


if __name__ == '__main__':

    ip_data = '54.210.179.46'

    while True:
        for i in range(3):
            comando1 = 'ffmpeg -f video4linux2 -video_size 640x480 -input_format yuyv422 -i /dev/video0 -f image2 -frames:v 1 -qscale:v 2 pipe:1 > {0}.jpeg'.format(i)
            comando2 = 'scp -i remota1.pem ./{1}.jpeg  ubuntu@{2}:~/flask-video-streaming/{1}.jpg'.format(i, ip_data)
            execute_comando(comando1)
            execute_comando(comando2)
            time.sleep(5)